import os
db_path = 'patent_database.db'
print(f"Current Working Directory: {os.getcwd()}")
print(f"Database path: {os.path.abspath(db_path)}")
print(f"Exists? {os.path.exists(db_path)}")
print(f"Size: {os.path.getsize(db_path) if os.path.exists(db_path) else 'N/A'}")
