# Migration Guide: Branch Teller to Agency Banking

## Overview
This guide explains how to migrate from the traditional branch teller system to the new agency banking channel, following Finacle's proven architecture.

## Key Differences

### Traditional Branch Teller System
- **Location**: Fixed bank branches
- **Staff**: Bank employees (tellers)
- **Transactions**: Direct to core banking system
- **Float**: Bank vault cash
- **Supervision**: Branch manager oversight

### Agency Banking System
- **Location**: Distributed agent locations (shops, kiosks)
- **Staff**: Third-party agents (shop owners, retailers)
- **Transactions**: Through agency gateway middleware
- **Float**: Agent-managed digital float
- **Supervision**: Remote monitoring + hierarchical structure

## Architecture Comparison

### Old: Branch Teller Architecture
```
Customer → Teller → Core Banking System → Account Update
```

### New: Agency Banking Architecture
```
Customer → Agent → Agency Gateway → Core Banking System → Account Update
                ↓
         Float Management & Commission Engine
```

## Migration Steps

### 1. Database Setup
```bash
# Navigate to agency banking directory
cd wekeza_dfs_platform/03_Source_Code/agency_banking

# Install dependencies
pip install -r requirements.txt

# Setup agency banking tables
python setup_agency_db.py
```

### 2. Agent Onboarding
The system supports a hierarchical agent structure:

#### Super Agents
- Large retail chains or aggregators
- High transaction limits (KES 5M daily)
- Manage multiple sub-agents
- Lower commission rates (0.3%)

#### Sub-Agents
- Medium-sized businesses
- Moderate limits (KES 1M daily)
- Report to super agents
- Standard commission rates (0.5%)

#### Retailers
- Small shops and kiosks
- Basic limits (KES 500K daily)
- Highest commission rates (0.7%)

### 3. Service Mapping

| Branch Teller Service | Agency Banking Equivalent | Notes |
|----------------------|---------------------------|-------|
| Cash Deposit | Cash In | Agent receives cash, credits customer |
| Cash Withdrawal | Cash Out | Agent debits customer, gives cash |
| Balance Inquiry | Balance Inquiry | Same functionality |
| Account Opening | eKYC Account Opening | Simplified digital process |
| Fund Transfer | Fund Transfer | Same functionality |
| Bill Payment | Bill Payment | Same functionality |

### 4. Security Enhancements

#### Multi-Factor Authentication
- PIN authentication (mandatory)
- Biometric verification (optional)
- Device binding
- GPS geo-fencing

#### Transaction Controls
- Real-time limit checking
- Daily transaction limits
- Float balance validation
- Fraud monitoring

### 5. Float Management

#### Traditional Branch
- Physical cash in vault
- Manual cash counting
- End-of-day reconciliation

#### Agency Banking
- Digital float balance
- Real-time float tracking
- Automated reconciliation
- Remote float top-up

## Key Features

### 1. Real-Time Processing
- Instant transaction processing
- Real-time balance updates
- Immediate commission calculation
- Live float management

### 2. Offline Capability
- Store-and-forward for poor connectivity
- Encrypted local storage
- Automatic sync when online
- Reduced transaction limits offline

### 3. Commission Engine
- Flexible commission structures
- Real-time commission calculation
- Automatic splits (Bank/Super Agent/Agent)
- Performance-based incentives

### 4. Comprehensive Reporting
- Real-time transaction monitoring
- Agent performance analytics
- Float utilization reports
- Commission statements

## Sample Agent Credentials

The system comes with pre-configured sample agents:

### Super Agent
- **Agent ID**: AG20240101SUPER1
- **Name**: Nairobi Super Agent Ltd
- **PIN**: 1234
- **Float**: KES 1,000,000
- **Daily Limit**: KES 5,000,000

### Sub-Agent
- **Agent ID**: AG20240101SUB001
- **Name**: Westlands Electronics
- **PIN**: 5678
- **Float**: KES 200,000
- **Daily Limit**: KES 1,000,000

### Retailer
- **Agent ID**: AG20240101RET001
- **Name**: Mama Mboga Shop
- **PIN**: 9999
- **Float**: KES 50,000
- **Daily Limit**: KES 500,000

## Starting the System

### Option 1: Using Startup Script
```bash
python start_agency_system.py
```

### Option 2: Direct Streamlit
```bash
streamlit run ui/agent_portal.py --server.port=8501
```

### Option 3: Using Batch File (Windows)
```bash
start_agency_banking.bat
```

## Testing the System

### 1. Agent Login
1. Open http://localhost:8501
2. Use sample agent credentials
3. Verify authentication works

### 2. Cash In Transaction
1. Login as any agent
2. Go to "Cash In" section
3. Use existing customer account (e.g., ACC1000014)
4. Process deposit transaction
5. Verify customer balance increases
6. Verify agent float decreases

### 3. Cash Out Transaction
1. Go to "Cash Out" section
2. Use customer account with sufficient balance
3. Process withdrawal transaction
4. Verify customer balance decreases
5. Verify agent float increases

### 4. Balance Inquiry
1. Go to "Balance Inquiry" section
2. Enter customer account number
3. Verify balance is displayed correctly

## Benefits of Agency Banking

### For the Bank
- **Expanded Reach**: Serve customers in remote areas
- **Reduced Costs**: Lower operational costs than branches
- **24/7 Service**: Agents can operate extended hours
- **Scalability**: Easy to add new agents

### For Customers
- **Convenience**: Banking services closer to home
- **Accessibility**: Services in local communities
- **Extended Hours**: Many agents open longer than banks
- **Familiar Environment**: Local shops they already know

### For Agents
- **Additional Revenue**: Commission on transactions
- **Customer Traffic**: Banking services attract customers
- **Business Growth**: Become financial service provider
- **Technology Access**: Modern POS/mobile systems

## Compliance and Risk Management

### KYC Requirements
- Agent onboarding with full KYC
- Customer verification for account opening
- Transaction monitoring and reporting
- Regular compliance audits

### Risk Controls
- Transaction limits and controls
- Real-time fraud monitoring
- Geo-location verification
- Device authentication

### Audit Trail
- Complete transaction logging
- Agent activity monitoring
- System access logs
- Compliance reporting

## Next Steps

1. **Setup Database**: Run `python setup_agency_db.py`
2. **Start System**: Run `python start_agency_system.py`
3. **Test Transactions**: Use sample agents to test all services
4. **Onboard Real Agents**: Use agent management system
5. **Monitor Performance**: Use reporting dashboard
6. **Scale Operations**: Add more agents as needed

## Support and Troubleshooting

### Common Issues
- **Database Connection**: Ensure MySQL is running
- **Port Conflicts**: Change port in startup script if needed
- **Authentication Failures**: Check agent credentials
- **Transaction Failures**: Verify float balances and limits

### Getting Help
- Check logs in the system
- Review error messages carefully
- Ensure all dependencies are installed
- Verify database tables are created

The agency banking system provides a robust, scalable alternative to traditional branch operations while maintaining security and compliance standards.