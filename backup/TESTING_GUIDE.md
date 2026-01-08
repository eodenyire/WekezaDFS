# Wekeza DFS Platform - Testing Guide

## 🚀 How to Test Your Running System

### Prerequisites
1. MySQL database running with `wekeza_dfs_db` created
2. All services started using the startup scripts
3. All applications accessible at their respective URLs

## 1. Backend API Testing (http://localhost:8000)

### A. Swagger UI Testing
1. **Open Swagger Documentation**: http://localhost:8000/docs
2. **Test Health Check**: Look for a `/` or `/health` endpoint and click "Try it out"
3. **Test Database Connection**: The API should start without database connection errors

### B. API Endpoint Testing
Test these key endpoints in Swagger UI:

#### Authentication Endpoints:
- `POST /token` - Test login functionality
- `POST /users/` - Test user registration

#### Banking Endpoints:
- `GET /accounts/me` - Test account retrieval (requires authentication)
- `POST /loans/apply` - Test loan application
- `POST /transfers/internal` - Test money transfers

### C. Database Verification
Check if tables are created automatically:
```sql
USE wekeza_dfs_db;
SHOW TABLES;
-- Should show: users, accounts, loans, transactions, user_policies, etc.
```

## 2. Customer Portal Testing (http://localhost:8502)

### A. User Registration Flow
1. **Access Portal**: http://localhost:8502
2. **Registration Test**:
   - Try creating a new account
   - Fill in: Full Name, Email, Phone, National ID, Password
   - Verify account creation success

### B. Login & Dashboard Testing
1. **Login Test**:
   - Use registered credentials
   - Verify successful login and token storage
2. **Dashboard Features**:
   - Check wallet balance display
   - Verify account status shows

### C. BIMS Features Testing
Test each tab functionality:

#### 📉 Borrow Tab:
- Apply for a loan (try KES 5,000)
- Check loan approval/rejection
- Test loan repayment (if loan approved)

#### 🛡️ Insure Tab:
- Buy personal accident insurance
- Verify policy creation

#### 💸 Move Tab:
- Test internal money transfer
- Use another account number for testing

#### 💰 Save Tab:
- Load transaction statement
- Verify transaction history display

#### ⚙️ Settings Tab:
- Test account disable/enable functionality

## 3. Business Portal Testing (http://localhost:8504)

### A. Business Login
1. **Access Portal**: http://localhost:8504
2. **Login Test**:
   - Use business director credentials
   - Verify corporate dashboard loads

### B. SME Banking Features

#### 📉 SME Finance Tab:
- Apply for working capital loan
- Test different sectors (Retail, Technology, Agriculture)
- Verify application submission

#### 🛡️ Business Insurance Tab:
- **WIBA Testing**:
  - Enter annual payroll amount
  - Calculate WIBA quote
  - Test policy purchase
- **Asset Insurance**:
  - Enter asset value
  - Get fire & burglary quote
  - Test policy activation

#### 💸 Bulk Payments Tab:
- Test CSV file upload functionality
- Verify batch processing queue

#### ⚙️ Admin Tab:
- Check director management interface
- Verify user roles display

## 4. Admin Portal Testing (http://localhost:8503)

### A. Risk Operations Dashboard
1. **Access Portal**: http://localhost:8503
2. **Database Connection**: Verify direct database connectivity
3. **Analytics**: Check if risk metrics and charts load
4. **User Management**: Test admin user management features

## 5. Integration Testing Scenarios

### A. End-to-End Customer Journey
1. **Customer Registration** → **Login** → **Apply for Loan** → **Get Approved/Rejected**
2. **Customer** → **Transfer Money** → **Check Statement** → **Verify Transaction**
3. **Customer** → **Buy Insurance** → **Verify Policy Creation**

### B. Business Customer Journey
1. **Business Login** → **Apply for Working Capital** → **Check Status**
2. **Business** → **Calculate Insurance Quote** → **Buy Policy** → **Verify Coverage**
3. **Business** → **Upload Payroll CSV** → **Process Batch Payments**

### C. Cross-System Testing
1. **Customer Action** → **Admin Portal** → **Verify Data Appears**
2. **Loan Application** → **Risk Engine** → **Check Approval Logic**
3. **Insurance Purchase** → **Database** → **Verify Policy Records**

## 6. Error Testing

### A. Authentication Errors
- Try invalid login credentials
- Test expired token scenarios
- Verify proper error messages

### B. Business Logic Errors
- Apply for loan with insufficient credit score
- Try transfers with insufficient balance
- Test insurance with invalid values

### C. Database Errors
- Test with database temporarily down
- Verify graceful error handling
- Check connection recovery

## 7. Performance Testing

### A. Load Testing
- Multiple simultaneous logins
- Concurrent loan applications
- Bulk transaction processing

### B. Response Time Testing
- API endpoint response times
- Streamlit app loading speeds
- Database query performance

## 8. Testing Checklist

### ✅ Backend API
- [ ] Swagger UI loads successfully
- [ ] Database tables created automatically
- [ ] Authentication endpoints work
- [ ] Banking endpoints respond correctly
- [ ] Error handling works properly

### ✅ Customer Portal
- [ ] Registration flow works
- [ ] Login/logout functionality
- [ ] All BIMS tabs functional
- [ ] Transaction history loads
- [ ] Insurance purchase works

### ✅ Business Portal
- [ ] Corporate login works
- [ ] SME loan application
- [ ] Business insurance quotes
- [ ] Bulk payment upload
- [ ] Director management

### ✅ Admin Portal
- [ ] Risk dashboard loads
- [ ] Database connectivity
- [ ] User management features
- [ ] Analytics and reports

### ✅ Integration
- [ ] Cross-system data consistency
- [ ] End-to-end workflows
- [ ] Error propagation
- [ ] Real-time updates

## 9. Common Issues & Solutions

### Issue: "Connection Refused" Errors
**Solution**: Ensure all services are running and check port availability

### Issue: Database Connection Errors
**Solution**: Verify MySQL is running and credentials are correct

### Issue: Token/Authentication Errors
**Solution**: Check JWT secret key consistency across services

### Issue: Streamlit Session State Issues
**Solution**: Clear browser cache and restart Streamlit apps

## 10. Test Data Setup

### Sample Users for Testing:
```sql
-- Insert test users directly into database if needed
INSERT INTO users (full_name, email, phone_number, national_id, password_hash) 
VALUES ('John Doe', 'john@test.com', '0712345678', '12345678', 'hashed_password');
```

### Sample Business Data:
```sql
-- Insert test business
INSERT INTO businesses (business_name, registration_no, kra_pin, sector) 
VALUES ('Test Corp Ltd', 'BIZ001', 'A123456789', 'Technology');
```

This comprehensive testing approach will help you verify that your Wekeza DFS platform is working correctly across all components!