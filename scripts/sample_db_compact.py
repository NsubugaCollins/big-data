import sqlite3
import os

def create_compact_sample_db(source_db, target_db, sample_size=500000):
    print(f"Creating compact sampled database ({sample_size} records) for web deployment...")
    
    if os.path.exists(target_db):
        os.remove(target_db)
        
    src_conn = sqlite3.connect(source_db)
    tgt_conn = sqlite3.connect(target_db)
    tgt_cursor = tgt_conn.cursor()
    
    # 1. Create schema (slightly modified: abstract can be null or empty)
    tgt_cursor.execute("""
        CREATE TABLE patents (
            patent_id TEXT PRIMARY KEY,
            title TEXT,
            abstract TEXT,
            grant_date TEXT,
            grant_year INTEGER,
            filing_date TEXT,
            filing_year INTEGER
        );
    """)
    tgt_cursor.execute("CREATE TABLE inventors (inventor_id TEXT PRIMARY KEY, name TEXT, country TEXT);")
    tgt_cursor.execute("CREATE TABLE companies (company_id TEXT PRIMARY KEY, name TEXT);")
    tgt_cursor.execute("CREATE TABLE relationships (patent_id TEXT, inventor_id TEXT, company_id TEXT);")
    
    # 2. Sample patents (EMPTY ABSTRACT to save space)
    print(f"   -> Sampling {sample_size} patents (compact)...")
    tgt_cursor.execute(f"ATTACH DATABASE '{source_db}' AS src;")
    
    tgt_cursor.execute(f"""
        INSERT INTO patents (patent_id, title, abstract, grant_date, grant_year, filing_date, filing_year)
        SELECT patent_id, title, '', grant_date, grant_year, filing_date, filing_year
        FROM src.patents 
        LIMIT {sample_size};
    """)
    
    # 3. Get related data
    print("   -> Fetching related data...")
    tgt_cursor.execute("""
        INSERT INTO inventors
        SELECT DISTINCT i.* FROM src.inventors i
        JOIN src.relationships r ON i.inventor_id = r.inventor_id
        JOIN patents p ON r.patent_id = p.patent_id;
    """)
    tgt_cursor.execute("""
        INSERT INTO companies
        SELECT DISTINCT c.* FROM src.companies c
        JOIN src.relationships r ON c.company_id = r.company_id
        JOIN patents p ON r.patent_id = p.patent_id;
    """)
    tgt_cursor.execute("""
        INSERT INTO relationships
        SELECT r.* FROM src.relationships r
        JOIN patents p ON r.patent_id = p.patent_id;
    """)
    
    tgt_conn.commit()
    tgt_cursor.execute("VACUUM;")
    src_conn.close()
    tgt_conn.close()
    print(f"Compact sample database created: {target_db} ({os.path.getsize(target_db) / 1024 / 1024:.2f} MB)")

if __name__ == "__main__":
    create_compact_sample_db('patent_database.db', 'patent_database_sample.db', sample_size=500000)
