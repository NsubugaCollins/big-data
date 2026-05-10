import sqlite3
import os

db_path = 'patent_database.db'
if not os.path.exists(db_path):
    print(f"{db_path} not found")
else:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    tables = ['patents', 'inventors', 'companies', 'relationships']
    for table in tables:
        try:
            cursor.execute(f"SELECT count(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"{table}: {count} rows")
        except sqlite3.OperationalError as e:
            print(f"Error checking {table}: {e}")
    
    conn.close()
