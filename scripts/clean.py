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
        
    # Connect to SQLite with longer timeout
    conn = sqlite3.connect(db_path, timeout=60)
    cursor = conn.cursor()
    cursor.execute("PRAGMA temp_store = MEMORY;")
    cursor.execute("PRAGMA synchronous = OFF;")
    cursor.execute("PRAGMA journal_mode = WAL;")
    
    # 1. Initialize schema (only for final tables)
    # We don't want to drop EVERYTHING if we are resuming, 
    # but schema.sql only drops final tables which we want to repopulate anyway.
    with open(schema_path, 'r') as f:
        schema_sql = f.read()
    cursor.executescript(schema_sql)
    conn.commit()
    print("-> Final database tables initialized.")

    # 2. Define staging mappings
    staging_files = {
        'staging_abstract': ('g_patent_abstract.tsv', ['patent_id', 'patent_abstract']),
        'staging_application': ('g_application.tsv', ['patent_id', 'filing_date']),
        'staging_patent': ('g_patent.tsv', ['patent_id', 'patent_title', 'patent_date']),
        'staging_location': ('g_location_disambiguated.tsv', ['location_id', 'disambig_country']),
        'staging_inventor': ('g_inventor_disambiguated.tsv', ['patent_id', 'inventor_id', 'location_id', 'disambig_inventor_name_first', 'disambig_inventor_name_last']),
        'staging_assignee': ('g_assignee_disambiguated.tsv', ['patent_id', 'assignee_id', 'disambig_assignee_organization'])
    }
    
    ROW_LIMIT = 2000000
    CHUNK_SIZE = 100000 # Increased chunk size for better performance
    
    for table_name, (tsv_filename, usecols) in staging_files.items():
        # Check current progress
        cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
        exists = cursor.fetchone()
        
        current_rows = 0
        if exists:
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            current_rows = cursor.fetchone()[0]
            print(f"-> Table {table_name} already exists with {current_rows} rows.")
            
        if current_rows >= ROW_LIMIT:
            print(f"   -> {table_name} already reached limit. Skipping load.")
            continue
            
        print(f"-> Loading/Resuming {tsv_filename} into {table_name}...")
        tsv_path = get_path(tsv_filename)
        
        # If it doesn't exist, create it via pandas first chunk
        # If it exists but incomplete, we skip current_rows
        
        mode = 'append' if current_rows > 0 else 'replace'
        skip = current_rows if current_rows > 0 else 0
        
        # Note: reading with skiprows means we lose the header if skip > 0.
        # So we should use header=0 and skip the actual rows.
        
        rows_to_load = ROW_LIMIT - current_rows
        total_loaded_this_run = 0
        
        # Use pandas to skip rows and read only what's needed
        # We use skiprows=range(1, skip+1) to skip the first 'skip' data rows but keep header
        skip_range = range(1, skip + 1) if skip > 0 else None
        
        for chunk in pd.read_csv(tsv_path, sep="\t", dtype=str, usecols=usecols, 
                                chunksize=CHUNK_SIZE, skiprows=skip_range):
            chunk.to_sql(table_name, conn, if_exists='append', index=False)
            total_loaded_this_run += len(chunk)
            
            if (current_rows + total_loaded_this_run) >= ROW_LIMIT:
                print(f"   -> Reached limit of {ROW_LIMIT} rows for {table_name}.")
                break
                
            if total_loaded_this_run % (CHUNK_SIZE * 5) == 0:
                print(f"   -> Progress: {current_rows + total_loaded_this_run} / {ROW_LIMIT} rows...")
        
        print(f"   Successfully finalized {current_rows + total_loaded_this_run} rows in {table_name}.")
        conn.commit()
        
    # Create indexes for fast joins
    print("-> Creating indexes on staging tables for optimized transformation...")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_abs_patent ON staging_abstract(patent_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_app_patent ON staging_application(patent_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_pat_patent ON staging_patent(patent_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_loc_loc ON staging_location(location_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_inv_patent ON staging_inventor(patent_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_ass_patent ON staging_assignee(patent_id);")
    conn.commit()

    # 3. Transform and insert into final tables
    print("-> Performing final data transformation...")
    
    # Run transformations in a single transaction
    try:
        print("   -> Populating patents...")
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
        
        print("   -> Populating inventors...")
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
        
        print("   -> Populating companies...")
        cursor.execute("""
            INSERT OR IGNORE INTO companies (company_id, name)
            SELECT DISTINCT
                assignee_id,
                COALESCE(NULLIF(TRIM(disambig_assignee_organization), ''), 'Unknown Company')
            FROM staging_assignee
            WHERE assignee_id IS NOT NULL AND disambig_assignee_organization IS NOT NULL AND disambig_assignee_organization != '';
        """)
        
        print("   -> Populating relationships...")
        # Use a more efficient join for relationships
        cursor.execute("""
            INSERT INTO relationships (patent_id, inventor_id, company_id)
            SELECT DISTINCT
                i.patent_id,
                i.inventor_id,
                a.assignee_id
            FROM staging_inventor i
            LEFT JOIN staging_assignee a ON i.patent_id = a.patent_id
            WHERE i.patent_id IS NOT NULL;
        """)
        
        conn.commit()
        print("-> Final tables populated successfully.")
    except sqlite3.Error as e:
        print(f"Error during transformation: {e}")
        conn.rollback()

    # 4. Cleanup staging tables
    print("-> Cleaning up staging tables...")
    for table_name in staging_files.keys():
        cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
    conn.commit()
    
    # 5. Vacuum database
    print("-> Vacuuming database to optimize space...")
    cursor.execute("VACUUM;")
    
    conn.close()
    print("Process complete! All data extracted, cleaned, and loaded.")

if __name__ == "__main__":
    clean_data()
