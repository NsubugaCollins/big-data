import pandas as pd
import sqlite3
import os

def clean_data():
    print("Beginning USPTO TSV data cleaning and database loading process...")
    
    RAW_DIR = "data/raw"
    db_path = 'patent_database.db'
    schema_path = 'sql/schema.sql'
    
    # Check schema
    if not os.path.exists(schema_path):
        raise FileNotFoundError(f"{schema_path} not found.")
        
    def get_path(filename):
        path = os.path.join(RAW_DIR, filename)
        if not os.path.exists(path):
            raise FileNotFoundError(f"Required raw file not found: {path}")
        return path
        
    # Connect to SQLite
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("PRAGMA temp_store = 1;")
    
    # 1. Initialize schema
    with open(schema_path, 'r') as f:
        schema_sql = f.read()
    cursor.executescript(schema_sql)
    conn.commit()
    print("-> Database schema initialized.")

    # 2. Define staging mappings
    # Map of staging_table_name -> (tsv_filename, [columns_to_keep])
    staging_files = {
        'staging_abstract': ('g_patent_abstract.tsv', ['patent_id', 'patent_abstract']),
        'staging_application': ('g_application.tsv', ['patent_id', 'filing_date']),
        'staging_patent': ('g_patent.tsv', ['patent_id', 'patent_title', 'patent_date']),
        'staging_location': ('g_location_disambiguated.tsv', ['location_id', 'disambig_country']),
        'staging_inventor': ('g_inventor_disambiguated.tsv', ['patent_id', 'inventor_id', 'location_id', 'disambig_inventor_name_first', 'disambig_inventor_name_last']),
        'staging_assignee': ('g_assignee_disambiguated.tsv', ['patent_id', 'assignee_id', 'disambig_assignee_organization'])
    }
    
    CHUNK_SIZE = 50000
    
    for table_name, (tsv_filename, usecols) in staging_files.items():
        print(f"-> Loading {tsv_filename} into temporary table {table_name}...")
        tsv_path = get_path(tsv_filename)
        
        # Drop staging table if exists
        cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
        
        total_rows = 0
        for chunk in pd.read_csv(tsv_path, sep="\t", dtype=str, usecols=usecols, chunksize=CHUNK_SIZE):
            chunk.to_sql(table_name, conn, if_exists='append', index=False)
            total_rows += len(chunk)
        print(f"   Successfully loaded {total_rows} rows into {table_name}.")
        
    # Create indexes for fast joins
    print("-> Creating indexes on staging tables...")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_abs_patent ON staging_abstract(patent_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_app_patent ON staging_application(patent_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_pat_patent ON staging_patent(patent_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_loc_loc ON staging_location(location_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_inv_patent ON staging_inventor(patent_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_ass_patent ON staging_assignee(patent_id);")
    conn.commit()

    # 3. Transform and insert into final tables
    print("-> Performing data transformation and populating final tables...")
    
    print("   -> Populating patents table...")
    cursor.execute("""
        INSERT OR IGNORE INTO patents (patent_id, title, abstract, grant_date, grant_year, filing_date, filing_year)
        SELECT 
            p.patent_id, 
            COALESCE(NULLIF(TRIM(p.patent_title), ''), 'Unknown Title'), 
            COALESCE(NULLIF(TRIM(a.patent_abstract), ''), 'No Abstract'), 
            DATE(p.patent_date), 
            CAST(STRFTIME('%Y', p.patent_date) AS INTEGER), 
            DATE(app.filing_date), 
            CAST(STRFTIME('%Y', app.filing_date) AS INTEGER)
        FROM staging_patent p
        LEFT JOIN staging_abstract a ON p.patent_id = a.patent_id
        LEFT JOIN staging_application app ON p.patent_id = app.patent_id
        WHERE p.patent_id IS NOT NULL;
    """)
    conn.commit()
    
    print("   -> Populating inventors table...")
    cursor.execute("""
        INSERT OR IGNORE INTO inventors (inventor_id, name, country)
        SELECT DISTINCT
            i.inventor_id,
            COALESCE(NULLIF(TRIM(IFNULL(i.disambig_inventor_name_first, '') || ' ' || IFNULL(i.disambig_inventor_name_last, '')), ''), 'Unknown Inventor'),
            COALESCE(NULLIF(TRIM(l.disambig_country), ''), 'Unknown')
        FROM staging_inventor i
        LEFT JOIN staging_location l ON i.location_id = l.location_id
        WHERE i.inventor_id IS NOT NULL;
    """)
    conn.commit()
    
    print("   -> Populating companies table...")
    cursor.execute("""
        INSERT OR IGNORE INTO companies (company_id, name)
        SELECT DISTINCT
            assignee_id,
            COALESCE(NULLIF(TRIM(disambig_assignee_organization), ''), 'Unknown Company')
        FROM staging_assignee
        WHERE assignee_id IS NOT NULL AND disambig_assignee_organization IS NOT NULL AND disambig_assignee_organization != '';
    """)
    conn.commit()
    
    print("   -> Populating relationships table...")
    cursor.execute("""
        INSERT INTO relationships (patent_id, inventor_id, company_id)
        SELECT DISTINCT
            COALESCE(i.patent_id, a.patent_id) as patent_id,
            i.inventor_id,
            a.assignee_id as company_id
        FROM staging_inventor i
        FULL OUTER JOIN staging_assignee a ON i.patent_id = a.patent_id
        WHERE COALESCE(i.patent_id, a.patent_id) IS NOT NULL;
    """)
    conn.commit()

    # 4. Cleanup staging tables
    print("-> Cleaning up temporary staging tables...")
    for table_name in staging_files.keys():
        cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
    conn.commit()
    
    # 5. Vacuum database to reclaim space
    print("-> Vacuuming database...")
    cursor.execute("VACUUM;")
    
    conn.close()
    print("Data extraction, cleaning, and relation building complete!")

if __name__ == "__main__":
    clean_data()
