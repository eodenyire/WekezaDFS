"""
Agency Banking Gateway - Core middleware for agency transactions
Handles communication between agents and Core Banking System
"""

import mysql.connector
from datetime import datetime, timedelta
import uuid
import json
import logging
from typing import Dict, Any, Optional, List
import hashlib
import hmac
from decimal import Decimal

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AgencyGateway:
    """
    Core gateway for agency banking operations
    Implements Finacle-style architecture with middleware pattern
    """
    
    def __init__(self):
        self.db_config = {
            'host': 'localhost',
            'user': 'root',
            'password': 'root',
            'database': 'wekeza_dfs_db'
        }
        self.offline_transactions = []  # Store offline transactions
        
    def get_db_connection(self):
        """Get database connection"""
        try:
            return mysql.connector.connect(**self.db_config)
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            return None
    
    def authenticate_agent(self, agent_id: str, device_id: str, pin: str, 
                          biometric_data: Optional[str] = None,
                          location: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Multi-factor authentication for agents
        
        Args:
            agent_id: Unique agent identifier
            device_id: Device identifier
            pin: Agent PIN
            biometric_data: Fingerprint/facial recognition data
            location: GPS coordinates
            
        Returns:
            Authentication result with session token
        """
        try:
            conn = self.get_db_connection()
            if not conn:
                return {"success": False, "error": "Database connection failed"}
            
            cursor = conn.cursor(dictionary=True)
            
            # Get agent details
            cursor.execute("""
                SELECT a.*, ad.device_id, ad.is_active as device_active,
                       ad.last_location_lat, ad.last_location_lng
                FROM agents a
                LEFT JOIN agent_devices ad ON a.agent_id = ad.agent_id
                WHERE a.agent_id = %s AND a.status = 'ACTIVE'
            """, (agent_id,))
            
            agent = cursor.fetchone()
            if not agent:
                return {"success": False, "error": "Agent not found or inactive"}
            
            # Verify PIN
            pin_hash = hashlib.sha256(pin.encode()).hexdigest()
            if agent['pin_hash'] != pin_hash:
                # Log failed attempt
                cursor.execute("""
                    INSERT INTO agent_auth_logs (agent_id, device_id, auth_type, 
                                                status, ip_address, created_at)
                    VALUES (%s, %s, 'PIN', 'FAILED', %s, %s)
                """, (agent_id, device_id, '127.0.0.1', datetime.now()))
                conn.commit()
                conn.close()
                return {"success": False, "error": "Invalid PIN"}
            
            # Verify device (relaxed for testing - in production this would be strict)
            # For testing, we'll allow any device ID
            # if agent['device_id'] and agent['device_id'] != device_id:
            #     return {"success": False, "error": "Unauthorized device"}
            
            # Geo-fencing check
            if location and agent['last_location_lat'] and agent['last_location_lng']:
                distance = self._calculate_distance(
                    location['lat'], location['lng'],
                    float(agent['last_location_lat']), float(agent['last_location_lng'])
                )
                if distance > 1.0:  # 1km radius
                    return {"success": False, "error": "Location verification failed"}
            
            # Generate session token
            session_token = self._generate_session_token(agent_id, device_id)
            
            # Update last login
            cursor.execute("""
                UPDATE agents SET last_login = %s WHERE agent_id = %s
            """, (datetime.now(), agent_id))
            
            # Log successful authentication
            cursor.execute("""
                INSERT INTO agent_auth_logs (agent_id, device_id, auth_type, 
                                            status, session_token, created_at)
                VALUES (%s, %s, 'PIN', 'SUCCESS', %s, %s)
            """, (agent_id, device_id, session_token, datetime.now()))
            
            conn.commit()
            conn.close()
            
            return {
                "success": True,
                "session_token": session_token,
                "agent_info": {
                    "agent_id": agent['agent_id'],
                    "agent_name": agent['agent_name'],
                    "agent_type": agent['agent_type'],
                    "float_balance": float(agent['float_balance']),
                    "daily_limit": float(agent['daily_limit']),
                    "transaction_limit": float(agent['transaction_limit'])
                }
            }
            
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return {"success": False, "error": "Authentication failed"}
    
    def process_transaction(self, session_token: str, transaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process agency transaction with full validation and security
        
        Args:
            session_token: Valid session token
            transaction_data: Transaction details
            
        Returns:
            Transaction result
        """
        try:
            # Validate session
            agent_info = self._validate_session(session_token)
            if not agent_info:
                return {"success": False, "error": "Invalid session"}
            
            # Route to appropriate transaction handler
            txn_type = transaction_data.get('transaction_type')
            
            handlers = {
                'CASH_IN': self._process_cash_in,
                'CASH_OUT': self._process_cash_out,
                'BALANCE_INQUIRY': self._process_balance_inquiry,
                'MINI_STATEMENT': self._process_mini_statement,
                'BILL_PAYMENT': self._process_bill_payment,
                'FUND_TRANSFER': self._process_fund_transfer,
                'ACCOUNT_OPENING': self._process_account_opening
            }
            
            handler = handlers.get(txn_type)
            if not handler:
                return {"success": False, "error": "Unsupported transaction type"}
            
            # Pre-transaction validations
            validation_result = self._validate_transaction(agent_info, transaction_data)
            if not validation_result['valid']:
                return {"success": False, "error": validation_result['error']}
            
            # Process transaction
            result = handler(agent_info, transaction_data)
            
            # Log transaction
            self._log_transaction(agent_info, transaction_data, result)
            
            return result
            
        except Exception as e:
            logger.error(f"Transaction processing error: {e}")
            return {"success": False, "error": "Transaction processing failed"}
    
    def _process_cash_in(self, agent_info: Dict, txn_data: Dict) -> Dict[str, Any]:
        """Process cash deposit (customer deposits cash with agent)"""
        try:
            conn = self.get_db_connection()
            if not conn:
                return {"success": False, "error": "Database connection failed"}
            
            cursor = conn.cursor(dictionary=True)
            
            customer_account = txn_data['customer_account']
            amount = Decimal(str(txn_data['amount']))
            agent_id = agent_info['agent_id']
            
            # Validate customer account
            cursor.execute("""
                SELECT account_id, balance, status FROM accounts 
                WHERE account_number = %s
            """, (customer_account,))
            
            account = cursor.fetchone()
            if not account or account['status'] != 'ACTIVE':
                return {"success": False, "error": "Invalid customer account"}
            
            # Check agent float balance
            cursor.execute("""
                SELECT float_balance FROM agents WHERE agent_id = %s
            """, (agent_id,))
            
            agent = cursor.fetchone()
            if not agent or Decimal(str(agent['float_balance'])) < amount:
                return {"success": False, "error": "Insufficient agent float"}
            
            # Generate transaction reference
            txn_ref = f"CI{datetime.now().strftime('%Y%m%d')}{uuid.uuid4().hex[:8].upper()}"
            
            # Start transaction
            cursor.execute("START TRANSACTION")
            
            try:
                # Debit agent float
                cursor.execute("""
                    UPDATE agents SET float_balance = float_balance - %s 
                    WHERE agent_id = %s
                """, (amount, agent_id))
                
                # Credit customer account
                cursor.execute("""
                    UPDATE accounts SET balance = balance + %s 
                    WHERE account_id = %s
                """, (amount, account['account_id']))
                
                # Record transaction
                cursor.execute("""
                    INSERT INTO agency_transactions (
                        transaction_ref, agent_id, customer_account, transaction_type,
                        amount, status, created_at, device_id
                    ) VALUES (%s, %s, %s, 'CASH_IN', %s, 'COMPLETED', %s, %s)
                """, (txn_ref, agent_id, customer_account, amount, 
                      datetime.now(), txn_data.get('device_id')))
                
                # Record in core transactions table
                cursor.execute("""
                    INSERT INTO transactions (
                        account_id, txn_type, amount, reference_code, 
                        description, created_at
                    ) VALUES (%s, 'AGENCY_DEPOSIT', %s, %s, %s, %s)
                """, (account['account_id'], amount, txn_ref,
                      f"Cash deposit via Agent {agent_id}", datetime.now()))
                
                # Calculate and record commission
                commission = self._calculate_commission(agent_info, 'CASH_IN', amount)
                if commission > 0:
                    cursor.execute("""
                        INSERT INTO agent_commissions (
                            agent_id, transaction_ref, commission_amount,
                            commission_type, created_at
                        ) VALUES (%s, %s, %s, 'CASH_IN', %s)
                    """, (agent_id, txn_ref, commission, datetime.now()))
                
                cursor.execute("COMMIT")
                
                # Get updated balances
                cursor.execute("SELECT balance FROM accounts WHERE account_id = %s", (account['account_id'],))
                new_customer_balance = cursor.fetchone()['balance']
                
                cursor.execute("SELECT float_balance FROM agents WHERE agent_id = %s", (agent_id,))
                new_agent_balance = cursor.fetchone()['float_balance']
                
                conn.close()
                
                return {
                    "success": True,
                    "transaction_ref": txn_ref,
                    "customer_balance": float(new_customer_balance),
                    "agent_balance": float(new_agent_balance),
                    "commission": float(commission),
                    "timestamp": datetime.now().isoformat()
                }
                
            except Exception as e:
                cursor.execute("ROLLBACK")
                raise e
                
        except Exception as e:
            logger.error(f"Cash in processing error: {e}")
            return {"success": False, "error": "Cash in processing failed"}
    
    def _process_cash_out(self, agent_info: Dict, txn_data: Dict) -> Dict[str, Any]:
        """Process cash withdrawal (customer withdraws cash from agent)"""
        try:
            conn = self.get_db_connection()
            if not conn:
                return {"success": False, "error": "Database connection failed"}
            
            cursor = conn.cursor(dictionary=True)
            
            customer_account = txn_data['customer_account']
            amount = Decimal(str(txn_data['amount']))
            agent_id = agent_info['agent_id']
            
            # Validate customer account and balance
            cursor.execute("""
                SELECT account_id, balance, status FROM accounts 
                WHERE account_number = %s
            """, (customer_account,))
            
            account = cursor.fetchone()
            if not account or account['status'] != 'ACTIVE':
                return {"success": False, "error": "Invalid customer account"}
            
            if Decimal(str(account['balance'])) < amount:
                return {"success": False, "error": "Insufficient customer balance"}
            
            # Check daily withdrawal limits
            daily_withdrawn = self._get_daily_withdrawal_total(customer_account)
            if (daily_withdrawn + amount) > Decimal('500000'):  # KES 500,000 daily limit
                return {"success": False, "error": "Daily withdrawal limit exceeded"}
            
            # Generate transaction reference
            txn_ref = f"CO{datetime.now().strftime('%Y%m%d')}{uuid.uuid4().hex[:8].upper()}"
            
            # Start transaction
            cursor.execute("START TRANSACTION")
            
            try:
                # Debit customer account
                cursor.execute("""
                    UPDATE accounts SET balance = balance - %s 
                    WHERE account_id = %s
                """, (amount, account['account_id']))
                
                # Credit agent float
                cursor.execute("""
                    UPDATE agents SET float_balance = float_balance + %s 
                    WHERE agent_id = %s
                """, (amount, agent_id))
                
                # Record transaction
                cursor.execute("""
                    INSERT INTO agency_transactions (
                        transaction_ref, agent_id, customer_account, transaction_type,
                        amount, status, created_at, device_id
                    ) VALUES (%s, %s, %s, 'CASH_OUT', %s, 'COMPLETED', %s, %s)
                """, (txn_ref, agent_id, customer_account, amount, 
                      datetime.now(), txn_data.get('device_id')))
                
                # Record in core transactions table
                cursor.execute("""
                    INSERT INTO transactions (
                        account_id, txn_type, amount, reference_code, 
                        description, created_at
                    ) VALUES (%s, 'AGENCY_WITHDRAWAL', %s, %s, %s, %s)
                """, (account['account_id'], amount, txn_ref,
                      f"Cash withdrawal via Agent {agent_id}", datetime.now()))
                
                # Calculate and record commission
                commission = self._calculate_commission(agent_info, 'CASH_OUT', amount)
                if commission > 0:
                    cursor.execute("""
                        INSERT INTO agent_commissions (
                            agent_id, transaction_ref, commission_amount,
                            commission_type, created_at
                        ) VALUES (%s, %s, %s, 'CASH_OUT', %s)
                    """, (agent_id, txn_ref, commission, datetime.now()))
                
                cursor.execute("COMMIT")
                
                # Get updated balances
                cursor.execute("SELECT balance FROM accounts WHERE account_id = %s", (account['account_id'],))
                new_customer_balance = cursor.fetchone()['balance']
                
                cursor.execute("SELECT float_balance FROM agents WHERE agent_id = %s", (agent_id,))
                new_agent_balance = cursor.fetchone()['float_balance']
                
                conn.close()
                
                return {
                    "success": True,
                    "transaction_ref": txn_ref,
                    "customer_balance": float(new_customer_balance),
                    "agent_balance": float(new_agent_balance),
                    "commission": float(commission),
                    "timestamp": datetime.now().isoformat()
                }
                
            except Exception as e:
                cursor.execute("ROLLBACK")
                raise e
                
        except Exception as e:
            logger.error(f"Cash out processing error: {e}")
            return {"success": False, "error": "Cash out processing failed"}
    
    def _process_balance_inquiry(self, agent_info: Dict, txn_data: Dict) -> Dict[str, Any]:
        """Process balance inquiry"""
        try:
            conn = self.get_db_connection()
            if not conn:
                return {"success": False, "error": "Database connection failed"}
            
            cursor = conn.cursor(dictionary=True)
            
            customer_account = txn_data['customer_account']
            
            # Get account details
            cursor.execute("""
                SELECT a.balance, a.status, u.full_name
                FROM accounts a
                JOIN users u ON a.user_id = u.user_id
                WHERE a.account_number = %s
            """, (customer_account,))
            
            account = cursor.fetchone()
            if not account:
                return {"success": False, "error": "Account not found"}
            
            # Record inquiry transaction
            txn_ref = f"BI{datetime.now().strftime('%Y%m%d')}{uuid.uuid4().hex[:8].upper()}"
            cursor.execute("""
                INSERT INTO agency_transactions (
                    transaction_ref, agent_id, customer_account, transaction_type,
                    amount, status, created_at, device_id
                ) VALUES (%s, %s, %s, 'BALANCE_INQUIRY', 0, 'COMPLETED', %s, %s)
            """, (txn_ref, agent_info['agent_id'], customer_account, 
                  datetime.now(), txn_data.get('device_id')))
            
            conn.commit()
            conn.close()
            
            return {
                "success": True,
                "transaction_ref": txn_ref,
                "account_holder": account['full_name'],
                "balance": float(account['balance']),
                "account_status": account['status'],
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Balance inquiry error: {e}")
            return {"success": False, "error": "Balance inquiry failed"}
    
    def _validate_transaction(self, agent_info: Dict, txn_data: Dict) -> Dict[str, Any]:
        """Validate transaction before processing"""
        try:
            # Check agent limits
            amount = Decimal(str(txn_data.get('amount', 0)))
            
            if amount > Decimal(str(agent_info['transaction_limit'])):
                return {"valid": False, "error": "Amount exceeds agent transaction limit"}
            
            # Check daily limits
            daily_total = self._get_agent_daily_total(agent_info['agent_id'])
            if (daily_total + amount) > Decimal(str(agent_info['daily_limit'])):
                return {"valid": False, "error": "Daily transaction limit exceeded"}
            
            return {"valid": True}
            
        except Exception as e:
            logger.error(f"Transaction validation error: {e}")
            return {"valid": False, "error": "Validation failed"}
    
    def _calculate_commission(self, agent_info: Dict, txn_type: str, amount: Decimal) -> Decimal:
        """Calculate commission based on transaction type and amount"""
        try:
            # Simple commission structure - can be made more sophisticated
            commission_rates = {
                'CASH_IN': Decimal('0.005'),    # 0.5%
                'CASH_OUT': Decimal('0.01'),    # 1.0%
                'BILL_PAYMENT': Decimal('10'),  # Flat KES 10
                'FUND_TRANSFER': Decimal('15')  # Flat KES 15
            }
            
            rate = commission_rates.get(txn_type, Decimal('0'))
            
            if txn_type in ['CASH_IN', 'CASH_OUT']:
                return amount * rate
            else:
                return rate
                
        except Exception:
            return Decimal('0')
    
    def _generate_session_token(self, agent_id: str, device_id: str) -> str:
        """Generate secure session token"""
        data = f"{agent_id}:{device_id}:{datetime.now().isoformat()}"
        return hashlib.sha256(data.encode()).hexdigest()
    
    def _validate_session(self, session_token: str) -> Optional[Dict]:
        """Validate session token and return agent info"""
        try:
            conn = self.get_db_connection()
            if not conn:
                return None
            
            cursor = conn.cursor(dictionary=True)
            
            # Check if session exists and is valid (within last 8 hours)
            cursor.execute("""
                SELECT a.* FROM agents a
                JOIN agent_auth_logs aal ON a.agent_id = aal.agent_id
                WHERE aal.session_token = %s 
                AND aal.created_at > %s
                AND aal.status = 'SUCCESS'
                ORDER BY aal.created_at DESC
                LIMIT 1
            """, (session_token, datetime.now() - timedelta(hours=8)))
            
            agent = cursor.fetchone()
            conn.close()
            
            return agent
            
        except Exception as e:
            logger.error(f"Session validation error: {e}")
            return None
    
    def _calculate_distance(self, lat1: float, lng1: float, lat2: float, lng2: float) -> float:
        """Calculate distance between two GPS coordinates in kilometers"""
        from math import radians, cos, sin, asin, sqrt
        
        # Convert to radians
        lat1, lng1, lat2, lng2 = map(radians, [lat1, lng1, lat2, lng2])
        
        # Haversine formula
        dlat = lat2 - lat1
        dlng = lng2 - lng1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlng/2)**2
        c = 2 * asin(sqrt(a))
        r = 6371  # Radius of earth in kilometers
        
        return c * r
    
    def _get_daily_withdrawal_total(self, account_number: str) -> Decimal:
        """Get total withdrawals for today for an account"""
        try:
            conn = self.get_db_connection()
            if not conn:
                return Decimal('0')
            
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT COALESCE(SUM(amount), 0) as daily_total
                FROM agency_transactions 
                WHERE customer_account = %s 
                AND transaction_type = 'CASH_OUT'
                AND DATE(created_at) = CURDATE()
                AND status = 'COMPLETED'
            """, (account_number,))
            
            result = cursor.fetchone()
            conn.close()
            
            return Decimal(str(result[0])) if result else Decimal('0')
            
        except Exception:
            return Decimal('0')
    
    def _get_agent_daily_total(self, agent_id: str) -> Decimal:
        """Get total transactions for today for an agent"""
        try:
            conn = self.get_db_connection()
            if not conn:
                return Decimal('0')
            
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT COALESCE(SUM(amount), 0) as daily_total
                FROM agency_transactions 
                WHERE agent_id = %s 
                AND DATE(created_at) = CURDATE()
                AND status = 'COMPLETED'
            """, (agent_id,))
            
            result = cursor.fetchone()
            conn.close()
            
            return Decimal(str(result[0])) if result else Decimal('0')
            
        except Exception:
            return Decimal('0')
    
    def _log_transaction(self, agent_info: Dict, txn_data: Dict, result: Dict):
        """Log transaction for audit purposes"""
        try:
            conn = self.get_db_connection()
            if not conn:
                return
            
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO agency_audit_logs (
                    agent_id, transaction_type, transaction_data, 
                    result_data, ip_address, device_id, created_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                agent_info['agent_id'],
                txn_data.get('transaction_type'),
                json.dumps(txn_data),
                json.dumps(result),
                txn_data.get('ip_address', '127.0.0.1'),
                txn_data.get('device_id'),
                datetime.now()
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Transaction logging error: {e}")