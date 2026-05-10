import sqlite3
db_path = 'patent_database.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()
try:
    cursor.execute("PRAGMA integrity_check;")
    print(f"Integrity check: {cursor.fetchone()[0]}")
except Exception as e:
    print(f"Error: {e}")
conn.close()
