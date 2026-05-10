import sqlite3
import os

def create_sample_db(source_db, target_db, sample_size=50000):
    print(f"Creating sampled database ({sample_size} records) for web deployment...")
    
    if not os.path.exists(source_db):
        print(f"Source database {source_db} not found.")
        return
        
    if os.path.exists(target_db):
        os.remove(target_db)
        
    src_conn = sqlite3.connect(source_db)
    tgt_conn = sqlite3.connect(target_db)
    tgt_cursor = tgt_conn.cursor()
    
    # 1. Create schema in target
    src_cursor = src_conn.cursor()
    src_cursor.execute("SELECT sql FROM sqlite_master WHERE type='table';")
    for row in src_cursor.fetchall():
        if row[0]:
            tgt_cursor.execute(row[0])
            
    # 2. Sample patents
    print(f"   -> Sampling {sample_size} patents...")
    tgt_cursor.execute(f"ATTACH DATABASE '{source_db}' AS src;")
    
    tgt_cursor.execute(f"""
        INSERT INTO patents 
        SELECT * FROM src.patents 
        LIMIT {sample_size};
    """)
    
    # 3. Get related data
    print("   -> Fetching related inventors...")
    tgt_cursor.execute("""
        INSERT INTO inventors
        SELECT DISTINCT i.* FROM src.inventors i
        JOIN src.relationships r ON i.inventor_id = r.inventor_id
        JOIN patents p ON r.patent_id = p.patent_id;
    """)
    
    print("   -> Fetching related companies...")
    tgt_cursor.execute("""
        INSERT INTO companies
        SELECT DISTINCT c.* FROM src.companies c
        JOIN src.relationships r ON c.company_id = r.company_id
        JOIN patents p ON r.patent_id = p.patent_id;
    """)
    
    print("   -> Fetching relationships...")
    tgt_cursor.execute("""
        INSERT INTO relationships
        SELECT r.* FROM src.relationships r
        JOIN patents p ON r.patent_id = p.patent_id;
    """)
    
    tgt_conn.commit()
    
    # 4. Vacuum and Clean
    print("   -> Finalizing sample database...")
    tgt_cursor.execute("VACUUM;")
    
    src_conn.close()
    tgt_conn.close()
    print(f"Sample database created: {target_db} ({os.path.getsize(target_db) / 1024 / 1024:.2f} MB)")

if __name__ == "__main__":
    create_sample_db('patent_database.db', 'patent_database_sample.db', sample_size=100000)
