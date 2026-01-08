"""
Admin Portal Authorization Helper
Ensures all admin operations go through maker-checker system
"""

import sys
import os
import uuid
from datetime import datetime
import json

# Add branch operations shared modules to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'branch_operations', 'shared'))

try:
    from authorization_helper import submit_to_authorization_queue, check_authorization_thresholds
except ImportError:
    print("Warning: Could not import authorization_helper")

def submit_admin_operation(operation_type, operation_data, admin_info, priority="HIGH"):
    """
    Submit admin operation to authorization queue
    
    Args:
        operation_type (str): Type of admin operation
        operation_data (dict): Operation details
        admin_info (dict): Admin user information
        priority (str): Priority level
    
    Returns:
        dict: Result of submission
    """
    try:
        # Admin operations typically have higher priority
        if priority == "HIGH":
            priority = "URGENT"
        
        # Add admin context to operation data
        operation_data['admin_user'] = admin_info.get('username', 'admin')
        operation_data['admin_portal'] = True
        operation_data['timestamp'] = datetime.now().isoformat()
        
        # Submit to authorization queue
        result = submit_to_authorization_queue(
            operation_type=operation_type,
            operation_data=operation_data,
            maker_info={
                'teller_id': admin_info.get('username', 'ADMIN001'),
                'full_name': f"Admin - {admin_info.get('username', 'Administrator')}",
                'branch_code': 'HQ001',  # Admin operations from HQ
                'role': 'admin'
            },
            priority=priority
        )
        
        return result
        
    except Exception as e:
        return {'success': False, 'error': str(e)}

def check_admin_authorization_thresholds(operation_type, amount=0):
    """
    Check if admin operation requires additional approval
    
    Args:
        operation_type (str): Type of operation
        amount (float): Amount involved (if applicable)
    
    Returns:
        dict: Authorization requirements
    """
    # Admin operations that always require approval
    always_approve = [
        'CUSTOMER_CREATE',
        'BUSINESS_CREATE', 
        'STAFF_CREATE',
        'ACCOUNT_FREEZE',
        'ACCOUNT_UNFREEZE',
        'BALANCE_ADJUSTMENT',
        'PASSWORD_RESET',
        'USER_ACTIVATION',
        'USER_DEACTIVATION'
    ]
    
    # High-value operations
    high_value_threshold = 100000  # KES 100,000
    
    if operation_type in always_approve:
        return {
            'requires_approval': True,
            'reason': f'Admin {operation_type} requires supervisor approval',
            'priority': 'URGENT'
        }
    
    if amount > high_value_threshold:
        return {
            'requires_approval': True,
            'reason': f'High-value operation (KES {amount:,.2f}) requires approval',
            'priority': 'URGENT'
        }
    
    return {
        'requires_approval': True,  # All admin operations require approval
        'reason': 'Admin operation requires supervisor approval',
        'priority': 'HIGH'
    }

# Specific admin operation helpers
def submit_customer_creation(customer_data, admin_info):
    """Submit customer creation for approval"""
    return submit_admin_operation(
        operation_type='CUSTOMER_CREATE',
        operation_data=customer_data,
        admin_info=admin_info,
        priority='URGENT'
    )

def submit_business_creation(business_data, admin_info):
    """Submit business creation for approval"""
    return submit_admin_operation(
        operation_type='BUSINESS_CREATE',
        operation_data=business_data,
        admin_info=admin_info,
        priority='URGENT'
    )

def submit_staff_creation(staff_data, admin_info):
    """Submit staff creation for approval"""
    return submit_admin_operation(
        operation_type='STAFF_CREATE',
        operation_data=staff_data,
        admin_info=admin_info,
        priority='HIGH'
    )

def submit_account_action(action_type, account_data, admin_info):
    """Submit account action (freeze/unfreeze/etc) for approval"""
    operation_types = {
        'freeze': 'ACCOUNT_FREEZE',
        'unfreeze': 'ACCOUNT_UNFREEZE',
        'activate': 'USER_ACTIVATION',
        'deactivate': 'USER_DEACTIVATION',
        'reset_password': 'PASSWORD_RESET'
    }
    
    return submit_admin_operation(
        operation_type=operation_types.get(action_type, 'ACCOUNT_MAINTENANCE'),
        operation_data=account_data,
        admin_info=admin_info,
        priority='URGENT'
    )

def submit_balance_adjustment(adjustment_data, admin_info):
    """Submit balance adjustment for approval"""
    return submit_admin_operation(
        operation_type='BALANCE_ADJUSTMENT',
        operation_data=adjustment_data,
        admin_info=admin_info,
        priority='URGENT'
    )

def get_admin_info():
    """Get current admin user info"""
    return {
        'username': 'admin',
        'full_name': 'System Administrator',
        'role': 'admin',
        'branch_code': 'HQ001'
    }