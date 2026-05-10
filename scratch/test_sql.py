import sqlite3
conn = sqlite3.connect(':memory:')
cursor = conn.cursor()
cursor.execute('CREATE TABLE t (a INT, b INT)')
cursor.execute('INSERT INTO t VALUES (1, NULL), (NULL, 2)')
print("Testing alias in WHERE:")
try:
    cursor.execute('SELECT COALESCE(a, b) as year FROM t WHERE year = 1')
    print(f"Result for year=1: {cursor.fetchall()}")
except Exception as e:
    print(f"Error for year=1: {e}")

try:
    cursor.execute('SELECT COALESCE(a, b) as val FROM t WHERE val IS NOT NULL')
    print(f"Result for val IS NOT NULL: {cursor.fetchall()}")
except Exception as e:
    print(f"Error for val IS NOT NULL: {e}")

conn.close()
