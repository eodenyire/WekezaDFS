# Wekeza Bank Agency Banking System

## Overview
The Agency Banking System transforms traditional branch operations into a distributed network of authorized agents who can provide banking services to customers in remote locations.

## Architecture
Based on Finacle's proven agency banking model:

### 1. Channel Architecture
- **Agency Gateway**: Middleware between agents and Core Banking System
- **Device Agnostic**: Supports POS terminals, mobile apps, USSD, web portals
- **Store & Forward**: Offline transaction capability for poor connectivity areas

### 2. Agent Hierarchy
- **Bank Admin**: Global rules and commission structures
- **Super Agent**: Aggregator managing multiple sub-agents
- **Sub-Agent/Retailer**: Shop owner performing transactions
- **Teller/Operator**: Employee using the device

### 3. Key Features
- Real-time transaction processing
- Float/liquidity management
- Commission engine with flexible splits
- Biometric authentication
- Geo-fencing security
- Comprehensive audit trails

## Services Offered
- Cash In/Out (Deposits/Withdrawals)
- Account Opening (eKYC)
- Bill Payments
- Fund Transfers
- Balance Inquiries
- Mini Statements
- Loan Repayments

## Security Features
- Multi-factor authentication
- Biometric verification
- GPS location validation
- Transaction limits and controls
- Real-time fraud monitoring

## Getting Started
1. Install dependencies: `pip install -r requirements.txt`
2. Configure database: `python setup_agency_db.py`
3. Start the system: `python start_agency_system.py`

## Directory Structure
```
agency_banking/
├── core/                   # Core agency banking logic
├── agents/                 # Agent management
├── devices/               # Device management (POS, Mobile)
├── transactions/          # Transaction processing
├── security/              # Security and authentication
├── reporting/             # Reports and analytics
├── api/                   # REST API endpoints
└── ui/                    # User interfaces
```