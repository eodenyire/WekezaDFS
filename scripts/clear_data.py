import mysql.connector

conn = mysql.connector.connect(host='localhost', user='root', password='root', database='wekeza_dfs_db')
cursor = conn.cursor()

# Clear data in correct order (foreign keys first)
cursor.execute('DELETE FROM transactions')
cursor.execute('DELETE FROM user_policies') 
cursor.execute('DELETE FROM loans')
cursor.execute('DELETE FROM accounts')
cursor.execute('DELETE FROM users')
cursor.execute('DELETE FROM businesses')

conn.commit()
print('✅ Cleared all user data')
conn.close()