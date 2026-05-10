import sqlite3
import os

db_path = 'patent_database.db'
if not os.path.exists(db_path):
    print(f"{db_path} not found")
else:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print("Tables in database:")
    for table in tables:
        tname = table[0]
        cursor.execute(f"SELECT count(*) FROM {tname}")
        count = cursor.fetchone()[0]
        print(f" - {tname}: {count} rows")
    
    conn.close()
