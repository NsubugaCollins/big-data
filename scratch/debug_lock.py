import sqlite3
import time

db_path = 'patent_database.db'
conn = sqlite3.connect(db_path, timeout=60)
cursor = conn.cursor()

tables = ['relationships', 'patents', 'inventors', 'companies', 'staging_abstract']

for table in tables:
    print(f"Attempting to drop {table}...")
    try:
        cursor.execute(f"DROP TABLE IF EXISTS {table}")
        conn.commit()
        print(f"Successfully dropped {table}")
    except Exception as e:
        print(f"Failed to drop {table}: {e}")
    time.sleep(1)

conn.close()
