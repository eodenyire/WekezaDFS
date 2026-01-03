import mysql.connector
from datetime import datetime

conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='root',
    database='wekeza_dfs_db'
)
cursor = conn.cursor()

print("🛡️ Setting up comprehensive insurance products...")

# Clear existing products and add new ones
cursor.execute("DELETE FROM insurance_products")

# Insert 4 comprehensive insurance products
insurance_products = [
    {
        'name': 'Personal Accident Cover',
        'code': 'PAC-001',
        'description': 'Comprehensive personal accident insurance covering accidental death, permanent disability, and medical expenses.',
        'premium': 150.00,
        'cover': 500000.00,
        'frequency': 'MONTHLY'
    },
    {
        'name': 'Credit Life Protection',
        'code': 'CLP-001', 
        'description': 'Protects your loans and credit obligations in case of death, permanent disability, or critical illness.',
        'premium': 50.00,
        'cover': 1000000.00,
        'frequency': 'MONTHLY'
    },
    {
        'name': 'Health & Medical Cover',
        'code': 'HMC-001',
        'description': 'Comprehensive health insurance covering hospitalization, outpatient services, and emergency medical care.',
        'premium': 300.00,
        'cover': 2000000.00,
        'frequency': 'MONTHLY'
    },
    {
        'name': 'Device & Asset Protection',
        'code': 'DAP-001',
        'description': 'Protects your mobile devices, laptops, and personal assets against theft, damage, and loss.',
        'premium': 100.00,
        'cover': 200000.00,
        'frequency': 'MONTHLY'
    }
]

for i, product in enumerate(insurance_products, 1):
    cursor.execute("""
        INSERT INTO insurance_products (product_id, product_name, product_code, description, 
                                      premium_amount, cover_amount, frequency, is_active)
        VALUES (%s, %s, %s, %s, %s, %s, %s, 1)
    """, (i, product['name'], product['code'], product['description'], 
          product['premium'], product['cover'], product['frequency']))

conn.commit()
conn.close()

print("✅ Insurance products setup complete!")
print("\n📋 Available Insurance Products:")
for i, product in enumerate(insurance_products, 1):
    print(f"{i}. {product['name']} ({product['code']})")
    print(f"   Premium: KES {product['premium']}/month")
    print(f"   Cover: KES {product['cover']:,.2f}")
    print(f"   {product['description']}")
    print()