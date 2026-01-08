"""
Agent Management System
Handles agent onboarding, hierarchy, and lifecycle management
"""

import mysql.connector
from datetime import datetime, timedelta
import uuid
import hashlib
import json
from typing import Dict, Any, List, Optional
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)

class AgentManager:
    """
    Manages the complete agent lifecycle and hierarchy
    Supports multi-tier structure: Bank -> Super Agent -> Sub-Agent -> Teller
    """
    
    def __init__(self):
        self.db_config = {
            'host': 'localhost',
            'user': 'root',
            'password': 'root',
            'database': 'wekeza_dfs_db'
        }
    
    def get_db_connection(self):
        """Get database connection"""
        try:
            return mysql.connector.connect(**self.db_config)
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            return None
    
    def onboard_agent(self, agent_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Onboard new agent with KYC and compliance checks
        
        Args:
            agent_data: Agent information including personal and business details
            
        Returns:
            Onboarding result with agent ID and status
        """
        try:
            conn = self.get_db_connection()
            if not conn:
                return {"success": False, "error": "Database connection failed"}
            
            cursor = conn.cursor(dictionary=True)
            
            # Validate required fields
            required_fields = ['agent_name', 'national_id', 'phone_number', 'email', 
                             'business_name', 'business_location', 'agent_type']
            
            for field in required_fields:
                if not agent_data.get(field):
                    return {"success": False, "error": f"Missing required field: {field}"}
            
            # Check for duplicate national ID or phone
            cursor.execute("""
                SELECT agent_id FROM agents 
                WHERE national_id = %s OR phone_number = %s
            """, (agent_data['national_id'], agent_data['phone_number']))
            
            if cursor.fetchone():
                return {"success": False, "error": "Agent already exists with this ID or phone"}
            
            # Generate agent ID
            agent_id = f"AG{datetime.now().strftime('%Y%m%d')}{uuid.uuid4().hex[:6].upper()}"
            
            # Hash PIN
            pin_hash = hashlib.sha256(agent_data['pin'].encode()).hexdigest()
            
            # Set default limits based on agent type
            limits = self._get_default_limits(agent_data['agent_type'])
            
            # Insert agent record
            cursor.execute("""
                INSERT INTO agents (
                    agent_id, agent_name, national_id, phone_number, email,
                    business_name, business_location, agent_type, parent_agent_id,
                    pin_hash, daily_limit, transaction_limit, float_balance,
                    commission_rate, status, created_at, created_by
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
            """, (
                agent_id, agent_data['agent_name'], agent_data['national_id'],
                agent_data['phone_number'], agent_data['email'], agent_data['business_name'],
                agent_data['business_location'], agent_data['agent_type'],
                agent_data.get('parent_agent_id'), pin_hash,
                limits['daily_limit'], limits['transaction_limit'], 0,
                limits['commission_rate'], 'PENDING_APPROVAL', datetime.now(),
                agent_data.get('created_by', 'SYSTEM')
            ))
            
            # Create agent settlement account
            settlement_account = self._create_settlement_account(agent_id, cursor)
            
            # Insert KYC documents
            if agent_data.get('kyc_documents'):
                for doc in agent_data['kyc_documents']:
                    cursor.execute("""
                        INSERT INTO agent_kyc_documents (
                            agent_id, document_type, document_number,
                            document_path, verified, created_at
                        ) VALUES (%s, %s, %s, %s, %s, %s)
                    """, (
                        agent_id, doc['type'], doc['number'],
                        doc['path'], False, datetime.now()
                    ))
            
            conn.commit()
            conn.close()
            
            return {
                "success": True,
                "agent_id": agent_id,
                "settlement_account": settlement_account,
                "status": "PENDING_APPROVAL",
                "message": "Agent onboarded successfully. Awaiting approval."
            }
            
        except Exception as e:
            logger.error(f"Agent onboarding error: {e}")
            return {"success": False, "error": "Agent onboarding failed"}
    
    def approve_agent(self, agent_id: str, approver_id: str, 
                     initial_float: Optional[Decimal] = None) -> Dict[str, Any]:
        """
        Approve agent and activate for transactions
        
        Args:
            agent_id: Agent identifier
            approver_id: ID of approving officer
            initial_float: Initial float amount to credit
            
        Returns:
            Approval result
        """
        try:
            conn = self.get_db_connection()
            if not conn:
                return {"success": False, "error": "Database connection failed"}
            
            cursor = conn.cursor(dictionary=True)
            
            # Get agent details
            cursor.execute("SELECT * FROM agents WHERE agent_id = %s", (agent_id,))
            agent = cursor.fetchone()
            
            if not agent:
                return {"success": False, "error": "Agent not found"}
            
            if agent['status'] != 'PENDING_APPROVAL':
                return {"success": False, "error": "Agent not in pending status"}
            
            # Update agent status
            cursor.execute("""
                UPDATE agents SET 
                    status = 'ACTIVE',
                    approved_by = %s,
                    approved_at = %s,
                    float_balance = COALESCE(%s, float_balance)
                WHERE agent_id = %s
            """, (approver_id, datetime.now(), initial_float or 0, agent_id))
            
            # Log approval
            cursor.execute("""
                INSERT INTO agent_status_logs (
                    agent_id, old_status, new_status, changed_by, 
                    reason, created_at
                ) VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                agent_id, 'PENDING_APPROVAL', 'ACTIVE', approver_id,
                'Agent approved for operations', datetime.now()
            ))
            
            # If initial float provided, record the transaction
            if initial_float and initial_float > 0:
                cursor.execute("""
                    INSERT INTO agent_float_transactions (
                        agent_id, transaction_type, amount, reference,
                        processed_by, created_at
                    ) VALUES (%s, 'INITIAL_CREDIT', %s, %s, %s, %s)
                """, (
                    agent_id, initial_float, f"INIT_{agent_id}",
                    approver_id, datetime.now()
                ))
            
            conn.commit()
            conn.close()
            
            return {
                "success": True,
                "message": "Agent approved and activated successfully",
                "agent_id": agent_id,
                "initial_float": float(initial_float) if initial_float else 0
            }
            
        except Exception as e:
            logger.error(f"Agent approval error: {e}")
            return {"success": False, "error": "Agent approval failed"}
    
    def manage_agent_float(self, agent_id: str, operation: str, amount: Decimal,
                          processed_by: str, reference: str = None) -> Dict[str, Any]:
        """
        Manage agent float (credit/debit operations)
        
        Args:
            agent_id: Agent identifier
            operation: 'CREDIT' or 'DEBIT'
            amount: Amount to credit/debit
            processed_by: ID of processing officer
            reference: Transaction reference
            
        Returns:
            Float management result
        """
        try:
            conn = self.get_db_connection()
            if not conn:
                return {"success": False, "error": "Database connection failed"}
            
            cursor = conn.cursor(dictionary=True)
            
            # Get current agent details
            cursor.execute("""
                SELECT agent_id, float_balance, status FROM agents 
                WHERE agent_id = %s
            """, (agent_id,))
            
            agent = cursor.fetchone()
            if not agent:
                return {"success": False, "error": "Agent not found"}
            
            if agent['status'] != 'ACTIVE':
                return {"success": False, "error": "Agent not active"}
            
            current_balance = Decimal(str(agent['float_balance']))
            
            # Validate operation
            if operation == 'DEBIT' and current_balance < amount:
                return {"success": False, "error": "Insufficient float balance"}
            
            # Calculate new balance
            if operation == 'CREDIT':
                new_balance = current_balance + amount
            else:  # DEBIT
                new_balance = current_balance - amount
            
            # Generate reference if not provided
            if not reference:
                reference = f"FLT{datetime.now().strftime('%Y%m%d')}{uuid.uuid4().hex[:6].upper()}"
            
            # Update agent float balance
            cursor.execute("""
                UPDATE agents SET float_balance = %s WHERE agent_id = %s
            """, (new_balance, agent_id))
            
            # Record float transaction
            cursor.execute("""
                INSERT INTO agent_float_transactions (
                    agent_id, transaction_type, amount, reference,
                    old_balance, new_balance, processed_by, created_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                agent_id, operation, amount, reference,
                current_balance, new_balance, processed_by, datetime.now()
            ))
            
            conn.commit()
            conn.close()
            
            return {
                "success": True,
                "reference": reference,
                "old_balance": float(current_balance),
                "new_balance": float(new_balance),
                "operation": operation,
                "amount": float(amount)
            }
            
        except Exception as e:
            logger.error(f"Float management error: {e}")
            return {"success": False, "error": "Float management failed"}
    
    def get_agent_hierarchy(self, agent_id: str) -> Dict[str, Any]:
        """
        Get complete agent hierarchy (parent and children)
        
        Args:
            agent_id: Agent identifier
            
        Returns:
            Hierarchy information
        """
        try:
            conn = self.get_db_connection()
            if not conn:
                return {"success": False, "error": "Database connection failed"}
            
            cursor = conn.cursor(dictionary=True)
            
            # Get agent details
            cursor.execute("SELECT * FROM agents WHERE agent_id = %s", (agent_id,))
            agent = cursor.fetchone()
            
            if not agent:
                return {"success": False, "error": "Agent not found"}
            
            # Get parent agent
            parent = None
            if agent['parent_agent_id']:
                cursor.execute("""
                    SELECT agent_id, agent_name, agent_type FROM agents 
                    WHERE agent_id = %s
                """, (agent['parent_agent_id'],))
                parent = cursor.fetchone()
            
            # Get child agents
            cursor.execute("""
                SELECT agent_id, agent_name, agent_type, status, float_balance
                FROM agents WHERE parent_agent_id = %s
            """, (agent_id,))
            children = cursor.fetchall()
            
            conn.close()
            
            return {
                "success": True,
                "agent": {
                    "agent_id": agent['agent_id'],
                    "agent_name": agent['agent_name'],
                    "agent_type": agent['agent_type'],
                    "status": agent['status'],
                    "float_balance": float(agent['float_balance'])
                },
                "parent": parent,
                "children": [
                    {
                        "agent_id": child['agent_id'],
                        "agent_name": child['agent_name'],
                        "agent_type": child['agent_type'],
                        "status": child['status'],
                        "float_balance": float(child['float_balance'])
                    } for child in children
                ]
            }
            
        except Exception as e:
            logger.error(f"Hierarchy retrieval error: {e}")
            return {"success": False, "error": "Hierarchy retrieval failed"}
    
    def get_agent_performance(self, agent_id: str, period_days: int = 30) -> Dict[str, Any]:
        """
        Get agent performance metrics
        
        Args:
            agent_id: Agent identifier
            period_days: Performance period in days
            
        Returns:
            Performance metrics
        """
        try:
            conn = self.get_db_connection()
            if not conn:
                return {"success": False, "error": "Database connection failed"}
            
            cursor = conn.cursor(dictionary=True)
            
            start_date = datetime.now() - timedelta(days=period_days)
            
            # Get transaction statistics
            cursor.execute("""
                SELECT 
                    transaction_type,
                    COUNT(*) as transaction_count,
                    SUM(amount) as total_amount
                FROM agency_transactions 
                WHERE agent_id = %s 
                AND created_at >= %s
                AND status = 'COMPLETED'
                GROUP BY transaction_type
            """, (agent_id, start_date))
            
            transactions = cursor.fetchall()
            
            # Get commission earned
            cursor.execute("""
                SELECT 
                    SUM(commission_amount) as total_commission
                FROM agent_commissions 
                WHERE agent_id = %s 
                AND created_at >= %s
            """, (agent_id, start_date))
            
            commission_result = cursor.fetchone()
            total_commission = float(commission_result['total_commission'] or 0)
            
            # Get current float balance
            cursor.execute("""
                SELECT float_balance FROM agents WHERE agent_id = %s
            """, (agent_id,))
            
            agent = cursor.fetchone()
            current_float = float(agent['float_balance']) if agent else 0
            
            conn.close()
            
            # Format transaction statistics
            transaction_stats = {}
            total_transactions = 0
            total_volume = 0
            
            for txn in transactions:
                txn_type = txn['transaction_type']
                count = txn['transaction_count']
                amount = float(txn['total_amount'] or 0)
                
                transaction_stats[txn_type] = {
                    "count": count,
                    "volume": amount
                }
                
                total_transactions += count
                total_volume += amount
            
            return {
                "success": True,
                "period_days": period_days,
                "agent_id": agent_id,
                "summary": {
                    "total_transactions": total_transactions,
                    "total_volume": total_volume,
                    "total_commission": total_commission,
                    "current_float": current_float
                },
                "transaction_breakdown": transaction_stats
            }
            
        except Exception as e:
            logger.error(f"Performance retrieval error: {e}")
            return {"success": False, "error": "Performance retrieval failed"}
    
    def suspend_agent(self, agent_id: str, reason: str, suspended_by: str) -> Dict[str, Any]:
        """
        Suspend agent operations
        
        Args:
            agent_id: Agent identifier
            reason: Suspension reason
            suspended_by: ID of suspending officer
            
        Returns:
            Suspension result
        """
        try:
            conn = self.get_db_connection()
            if not conn:
                return {"success": False, "error": "Database connection failed"}
            
            cursor = conn.cursor()
            
            # Update agent status
            cursor.execute("""
                UPDATE agents SET 
                    status = 'SUSPENDED',
                    suspended_by = %s,
                    suspended_at = %s
                WHERE agent_id = %s AND status = 'ACTIVE'
            """, (suspended_by, datetime.now(), agent_id))
            
            if cursor.rowcount == 0:
                return {"success": False, "error": "Agent not found or not active"}
            
            # Log suspension
            cursor.execute("""
                INSERT INTO agent_status_logs (
                    agent_id, old_status, new_status, changed_by, 
                    reason, created_at
                ) VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                agent_id, 'ACTIVE', 'SUSPENDED', suspended_by,
                reason, datetime.now()
            ))
            
            conn.commit()
            conn.close()
            
            return {
                "success": True,
                "message": "Agent suspended successfully",
                "agent_id": agent_id,
                "reason": reason
            }
            
        except Exception as e:
            logger.error(f"Agent suspension error: {e}")
            return {"success": False, "error": "Agent suspension failed"}
    
    def _get_default_limits(self, agent_type: str) -> Dict[str, Any]:
        """Get default limits based on agent type"""
        limits = {
            'SUPER_AGENT': {
                'daily_limit': Decimal('5000000'),      # KES 5M
                'transaction_limit': Decimal('500000'),  # KES 500K
                'commission_rate': Decimal('0.003')     # 0.3%
            },
            'SUB_AGENT': {
                'daily_limit': Decimal('1000000'),      # KES 1M
                'transaction_limit': Decimal('100000'),  # KES 100K
                'commission_rate': Decimal('0.005')     # 0.5%
            },
            'RETAILER': {
                'daily_limit': Decimal('500000'),       # KES 500K
                'transaction_limit': Decimal('50000'),   # KES 50K
                'commission_rate': Decimal('0.007')     # 0.7%
            }
        }
        
        return limits.get(agent_type, limits['RETAILER'])
    
    def _create_settlement_account(self, agent_id: str, cursor) -> str:
        """Create settlement account for agent"""
        try:
            # Generate settlement account number
            settlement_account = f"AGNT{agent_id[2:]}"  # Remove AG prefix
            
            # Insert settlement account record
            cursor.execute("""
                INSERT INTO agent_settlement_accounts (
                    agent_id, account_number, balance, currency,
                    status, created_at
                ) VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                agent_id, settlement_account, 0, 'KES',
                'ACTIVE', datetime.now()
            ))
            
            return settlement_account
            
        except Exception as e:
            logger.error(f"Settlement account creation error: {e}")
            return f"AGNT{agent_id[2:]}"  # Return default even if creation fails