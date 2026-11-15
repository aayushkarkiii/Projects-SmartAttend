from db_config import get_mysql_connection

try:
    conn = get_mysql_connection()
    cursor = conn.cursor()
    cursor.execute("show databases")
    data = cursor.fetchall()
    print("Databases:", data)
    conn.close()
except Exception as e:
    print("MySQL connection failed:", e)
