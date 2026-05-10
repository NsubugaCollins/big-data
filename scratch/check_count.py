import sqlite3
conn = sqlite3.connect('patent_database.db')
cursor = conn.cursor()
cursor.execute("SELECT COUNT(*) FROM patents;")
print(f"Patents count: {cursor.fetchone()[0]}")
conn.close()
