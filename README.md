# 🏦 WekezaDFS - Digital Financial Services Platform

A comprehensive digital banking and financial services platform built with Python, Streamlit, and MySQL. WekezaDFS provides end-to-end banking solutions including personal banking, business banking, loans, insurance, and branch operations.

## 🌟 Features

### 🏦 **Core Banking System**
- **Personal Banking**: Individual customer accounts with full transaction capabilities
- **Business Banking**: Corporate accounts with enhanced features for businesses
- **Account Management**: Real-time balance tracking, transaction history, and account operations
- **Multi-Currency Support**: KES (Kenyan Shilling) with extensible currency framework

### 💰 **Lending & Credit**
- **Personal Loans**: Quick loan applications with automated risk assessment
- **Business Loans**: Working capital and term loans for businesses
- **Loan Management**: Application processing, approval workflows, and repayment tracking
- **Interest Calculation**: Dynamic interest rates based on loan terms and risk profiles
- **Automated Disbursement**: Instant fund transfer upon loan approval

### 🛡️ **Insurance Services**
- **Personal Insurance**: 
  - Personal Accident Cover (KES 500K coverage)
  - Credit Life Protection (KES 1M coverage)
  - Health & Medical Cover (KES 2M coverage)
  - Device & Asset Protection (KES 200K coverage)
- **Business Insurance**: Scalable coverage for businesses based on employees and assets
- **Claims Management**: End-to-end claims processing with automated payouts
- **Premium Management**: Automated premium deductions and policy renewals

### 🏪 **Branch Operations**
- **Teller System**: Cash deposits, withdrawals, and customer service operations
- **Customer Lookup**: Advanced search and account inquiry capabilities
- **New Customer Registration**: On-site customer onboarding and account creation
- **Transaction Processing**: Real-time transaction handling with receipt generation
- **Daily Reports**: Branch performance and transaction summaries

### 👥 **Staff Management**
- **Multi-Role Support**: Tellers, Relationship Managers, Supervisors, Branch Managers, Admins
- **Branch Management**: Multiple branch locations with staff assignments
- **Access Control**: Role-based permissions and authentication
- **Staff Directory**: Complete staff information and contact management

### 📊 **Admin & Risk Management**
- **Comprehensive Dashboard**: Real-time KPIs and business metrics
- **User Management**: Customer and business account administration
- **Transaction Monitoring**: Real-time transaction tracking and fraud detection
- **Loan Approval Workflows**: Manual and automated loan processing
- **Insurance Claims Processing**: Claims review and payout management
- **System Configuration**: Platform settings and parameter management

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- MySQL 8.0+
- Git

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/eodenyire/WekezaDFS.git
cd WekezaDFS/wekeza_dfs_platform
```

2. **Install dependencies**
```bash
pip install streamlit pandas mysql-connector-python sqlalchemy plotly
```

3. **Database Setup**
```bash
# Create MySQL database
mysql -u root -p
CREATE DATABASE wekeza_dfs_db;
exit

# Initialize database schema
python setup_clean_database.py
python create_staff_tables.py
python setup_insurance_products.py
```

4. **Start the platform**
```bash
# Start all services
.\setup_local_dev.bat

# Or start individual services:
.\start_customer_portal.bat    # Port 8502
.\start_business_portal.bat    # Port 8504
.\start_admin_portal.bat       # Port 8503
.\start_teller_app.bat         # Port 8505
```

## 🖥️ Application Access

| Service | URL | Default Credentials |
|---------|-----|-------------------|
| **Customer Portal** | http://localhost:8502 | Register new account or admin/admin |
| **Business Portal** | http://localhost:8504 | Register new business or admin/admin |
| **Admin Dashboard** | http://localhost:8503 | admin/admin |
| **Branch Teller** | http://localhost:8505 | TELLER001/teller123 |

## 📱 User Interfaces

### 🏦 Customer Portal
- **Dashboard**: Account balance, transaction history, quick actions
- **Borrow**: Loan applications, repayments, loan calculator
- **Insure**: Insurance products, policy management, claims filing
- **Move**: Internal transfers and payment processing
- **Save**: Savings products and investment options
- **Settings**: Profile management and preferences

### 🏢 Business Portal
- **Command Center**: Business account overview and metrics
- **SME Finance**: Business loans and working capital
- **Business Insurance**: Group policies and corporate coverage
- **Bulk Payments**: Payroll and supplier payment processing
- **Director Management**: Multi-user business account access

### 🏪 Branch Teller System
- **Cash Operations**: Deposits and withdrawals with receipt printing
- **Customer Lookup**: Advanced customer search and account inquiry
- **New Customer Registration**: On-site account opening
- **Transaction History**: Complete transaction tracking
- **Daily Reports**: Branch performance metrics

### 🔧 Admin Dashboard
- **System Overview**: Platform-wide KPIs and metrics
- **User Management**: Customer and business account administration
- **Loan Processing**: Application review and approval workflows
- **Insurance Management**: Policy administration and claims processing
- **Staff Management**: Employee records and branch assignments
- **Transaction Monitoring**: Real-time fraud detection and reporting

## 🏗️ Architecture

### Technology Stack
- **Frontend**: Streamlit (Python web framework)
- **Backend**: Python with direct database connections
- **Database**: MySQL 8.0 with optimized schema
- **Authentication**: Session-based with role management
- **Deployment**: Docker-ready with batch scripts for Windows

### Database Schema
- **Users & Accounts**: Customer and business account management
- **Transactions**: Complete transaction logging with references
- **Loans**: Loan lifecycle management from application to closure
- **Insurance**: Policy management and claims processing
- **Staff & Branches**: Organizational structure and access control

### Security Features
- **Role-Based Access Control**: Different permissions for different user types
- **Transaction Logging**: Complete audit trail for all operations
- **Session Management**: Secure session handling across all portals
- **Data Validation**: Input sanitization and business rule enforcement

## 📊 Business Intelligence

### Real-Time Dashboards
- **Customer Metrics**: Account growth, transaction volumes, customer satisfaction
- **Loan Portfolio**: Outstanding loans, default rates, approval metrics
- **Insurance Analytics**: Policy uptake, claims ratios, premium collection
- **Branch Performance**: Transaction volumes, customer service metrics
- **Financial Health**: Liquidity ratios, profitability analysis

### Reporting Capabilities
- **Regulatory Reports**: Central bank compliance and reporting
- **Management Reports**: Executive dashboards and KPI tracking
- **Operational Reports**: Daily operations and exception reporting
- **Customer Reports**: Account statements and transaction histories

## 🔧 Configuration

### Environment Setup
```bash
# Database Configuration
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=root
DB_NAME=wekeza_dfs_db

# Application Ports
CUSTOMER_PORT=8502
BUSINESS_PORT=8504
ADMIN_PORT=8503
TELLER_PORT=8505
```

### Default Test Data
The system includes comprehensive test data:
- **Sample Customers**: Pre-created personal and business accounts
- **Test Transactions**: Sample transaction history
- **Insurance Policies**: Active policies for testing
- **Staff Accounts**: Complete organizational structure

## 🧪 Testing

### Automated Testing
```bash
# Run all tests
python run_all_tests.py

# Test specific components
python test_database.py      # Database connectivity
python test_portals.py       # Portal functionality
python test_loan_system.py   # Loan processing
python test_insurance_system.py  # Insurance operations
```

### Manual Testing
- **Customer Journey**: Account creation → loan application → insurance purchase
- **Business Workflow**: Business registration → group insurance → bulk payments
- **Teller Operations**: Cash handling → customer service → reporting
- **Admin Functions**: User management → loan approval → system monitoring

## 📈 Performance

### Scalability Features
- **Database Optimization**: Indexed queries and optimized schema
- **Session Management**: Efficient state handling across portals
- **Concurrent Users**: Support for multiple simultaneous users
- **Transaction Processing**: High-throughput transaction handling

### Monitoring
- **Real-Time Metrics**: Live dashboard updates and alerts
- **Performance Tracking**: Response time and throughput monitoring
- **Error Logging**: Comprehensive error tracking and reporting
- **Audit Trails**: Complete transaction and user activity logs

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Author

**Emmanuel Odenyire Anyira**
- GitHub: [@eodenyire](https://github.com/eodenyire)
- Email: eodenyire@gmail.com

## 🙏 Acknowledgments

- Built with [Streamlit](https://streamlit.io/) for rapid web application development
- Database powered by [MySQL](https://www.mysql.com/)
- UI components inspired by modern banking interfaces
- Special thanks to the open-source community for excellent Python libraries

## 📞 Support

For support, email eodenyire@gmail.com or create an issue in the GitHub repository.

---

**WekezaDFS** - Empowering Digital Financial Services 🚀