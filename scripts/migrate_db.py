import sqlite3
import os

def migrate():
    db_path = 'patent_database.db'
    if not os.path.exists(db_path):
        print(f"Error: {db_path} not found.")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    print("Checking current schema...")
    cursor.execute("PRAGMA table_info(patents)")
    columns = [row[1] for row in cursor.fetchall()]
    print(f"Current columns: {columns}")

    # Add missing columns
    new_cols = {
        'grant_date': 'TEXT',
        'grant_year': 'INTEGER',
        'filing_year': 'INTEGER'
    }

    for col, dtype in new_cols.items():
        if col not in columns:
            print(f"Adding column {col}...")
            try:
                cursor.execute(f"ALTER TABLE patents ADD COLUMN {col} {dtype}")
            except sqlite3.Error as e:
                print(f"Error adding {col}: {e}")
        else:
            print(f"Column {col} already exists.")

    # Data Migration
    print("Migrating data...")
    
    # 1. Map old 'year' to 'grant_year' if grant_year is null
    if 'year' in columns:
        print("Mapping old 'year' to 'grant_year'...")
        cursor.execute("UPDATE patents SET grant_year = year WHERE grant_year IS NULL AND year IS NOT NULL")
    
    # 2. Extract filing_year from filing_date
    if 'filing_date' in columns:
        print("Extracting filing_year from filing_date...")
        # Assuming filing_date is in YYYY-MM-DD or similar where first 4 chars are year
        cursor.execute("""
            UPDATE patents 
            SET filing_year = CAST(SUBSTR(filing_date, 1, 4) AS INTEGER) 
            WHERE filing_year IS NULL AND filing_date IS NOT NULL AND LENGTH(filing_date) >= 4
        """)

    conn.commit()
    print("Migration complete!")
    
    # Verify
    cursor.execute("PRAGMA table_info(patents)")
    print(f"New columns: {[row[1] for row in cursor.fetchall()]}")
    conn.close()

if __name__ == "__main__":
    migrate()
