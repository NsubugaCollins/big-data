import sqlite3
db_path = 'patent_database.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()
try:
    cursor.execute("DROP TABLE IF EXISTS patents;")
    conn.commit()
    print("Dropped patents table successfully")
except Exception as e:
    print(f"Error: {e}")
conn.close()
