import sqlite3
import pandas as pd
import os

def test_queries():
    db_path = 'patent_database.db'
    if not os.path.exists(db_path):
        print("Database not found.")
        return

    conn = sqlite3.connect(db_path)
    
    print("Testing Trends Query...")
    try:
        query = """
            SELECT 
                COALESCE(grant_year, filing_year) as activity_year,
                COUNT(CASE WHEN grant_year IS NOT NULL THEN 1 END) as grants,
                COUNT(CASE WHEN filing_year IS NOT NULL THEN 1 END) as filings
            FROM patents 
            WHERE grant_year IS NOT NULL OR filing_year IS NOT NULL
            GROUP BY activity_year 
            ORDER BY activity_year
        """
        df = pd.read_sql_query(query, conn)
        print(f"Trends Data (top 5):\n{df.head()}")
    except Exception as e:
        print(f"Trends Query Failed: {e}")

    print("\nTesting Search Query...")
    try:
        search_sql = """
            SELECT patent_id, title, grant_date, filing_date 
            FROM patents 
            LIMIT 5
        """
        df = pd.read_sql_query(search_sql, conn)
        print(f"Search Data:\n{df}")
    except Exception as e:
        print(f"Search Query Failed: {e}")

    conn.close()

if __name__ == "__main__":
    test_queries()
