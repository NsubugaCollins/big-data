import sqlite3
import pandas as pd
import os

def load_data_to_db():
    print("Beginning database loading process...")
    
    db_path = 'patent_database.db'
    schema_path = 'sql/schema.sql'
    
    if not os.path.exists(schema_path):
        raise FileNotFoundError(f"{schema_path} not found.")
        
    # Connect to SQLite database (this creates it if it doesn't exist)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 1. Execute Schema
    with open(schema_path, 'r') as f:
        schema_sql = f.read()
    
    try:
        # executescript allows running multiple statements separated by colons
        cursor.executescript(schema_sql)
        conn.commit()
        print("Successfully applied schema.sql")
    except sqlite3.Error as e:
        print(f"An error occurred applying the schema: {e}")
        return

    # 2. Map of table names to their corresponding clean CSV files
    tables_to_files = {
        'patents': 'data/processed/clean_patents.csv',
        'inventors': 'data/processed/clean_inventors.csv',
        'companies': 'data/processed/clean_companies.csv',
        'relationships': 'data/processed/clean_relationships.csv'
    }

    # 3. Load each CSV into its respective table
    for table_name, csv_path in tables_to_files.items():
        if os.path.exists(csv_path):
            print(f"-> Loading {csv_path} into '{table_name}' table...")
            total_rows = 0
            # Read in chunks of 100,000 rows to keep memory usage low
            for chunk in pd.read_csv(csv_path, chunksize=100000):
                # Use append to respect the schema created by executescript
                chunk.to_sql(table_name, conn, if_exists='append', index=False)
                total_rows += len(chunk)
            print(f"   Successfully loaded {total_rows} rows.")
        else:
            print(f"Warning: Data file {csv_path} not found.")

    conn.close()
    print("Database loading complete.")

if __name__ == "__main__":
    load_data_to_db()
