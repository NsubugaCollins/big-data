import pandas as pd
import sqlite3
import json
import os

def generate_reports():
    print("Generating comprehensive reports...")
    
    db_path = 'patent_database.db'
    if not os.path.exists(db_path):
        raise FileNotFoundError(f"Database {db_path} not found. Please run the load script.")
        
    conn = sqlite3.connect(db_path)
    
    os.makedirs('reports', exist_ok=True)
    
    # 1. Basic Stats
    total_patents_df = pd.read_sql_query("SELECT COUNT(*) as total FROM patents", conn)
    total_patents = int(total_patents_df.iloc[0]['total'])
    
    # 2. Extract specific query results
    top_inventors = pd.read_sql_query("""
        SELECT i.name, COUNT(r.patent_id) as total_patents
        FROM inventors i
        JOIN relationships r ON i.inventor_id = r.inventor_id
        GROUP BY i.name
        ORDER BY total_patents DESC
        LIMIT 20;
    """, conn)
    
    top_companies = pd.read_sql_query("""
        SELECT c.name, COUNT(r.patent_id) as total_patents
        FROM companies c
        JOIN relationships r ON c.company_id = r.company_id
        GROUP BY c.name
        ORDER BY total_patents DESC
        LIMIT 20;
    """, conn)
    
    top_countries = pd.read_sql_query("""
        SELECT i.country, COUNT(r.patent_id) as total_patents
        FROM inventors i
        JOIN relationships r ON i.inventor_id = r.inventor_id
        GROUP BY i.country
        ORDER BY total_patents DESC
    """, conn)
    
    grant_trends = pd.read_sql_query("""
        SELECT grant_year as year, COUNT(patent_id) as total_patents
        FROM patents
        WHERE grant_year IS NOT NULL
        GROUP BY grant_year
        ORDER BY grant_year ASC
    """, conn)
    
    # 3. Advanced Analytics
    # Average patents per company
    avg_patents_per_company = pd.read_sql_query("""
        SELECT AVG(patent_count) as avg_pats
        FROM (
            SELECT company_id, COUNT(patent_id) as patent_count
            FROM relationships
            WHERE company_id IS NOT NULL
            GROUP BY company_id
        )
    """, conn).iloc[0]['avg_pats']

    # 4. Export CSV files
    top_inventors.to_csv('reports/top_inventors.csv', index=False)
    top_companies.to_csv('reports/top_companies.csv', index=False)
    grant_trends.to_csv('reports/grant_trends.csv', index=False)
    top_countries.to_csv('reports/top_countries.csv', index=False)
    
    # 5. Generate JSON Report
    json_data = {
        "total_patents": total_patents,
        "average_patents_per_company": round(float(avg_patents_per_company), 2) if avg_patents_per_company else 0,
        "top_inventors": [
            {"name": row['name'], "patents": int(row['total_patents'])} 
            for _, row in top_inventors.head(10).iterrows()
        ],
        "top_companies": [
            {"name": row['name'], "patents": int(row['total_patents'])}
            for _, row in top_companies.head(10).iterrows()
        ],
        "top_countries": [
            {"country": row['country'], "share": round(row['total_patents'] / total_patents, 3)}
            for _, row in top_countries.head(10).iterrows()
        ]
    }
    
    with open('reports/summary_report.json', 'w') as f:
        json.dump(json_data, f, indent=4)
        
    # 6. Console Report (Terminal Output)
    print("\n================== ADVANCED PATENT REPORT ===================")
    print(f"Total Patents Analyzed: {total_patents}")
    print(f"Avg Patents per Company: {round(float(avg_patents_per_company), 2) if avg_patents_per_company else 0}")
    
    print("\nTop 5 Inventors:")
    for idx, row in top_inventors.head(5).iterrows():
        print(f"  {idx+1}. {row['name']} ({row['total_patents']} patents)")
        
    print("\nTop 5 Companies:")
    for idx, row in top_companies.head(5).iterrows():
        print(f"  {idx+1}. {row['name']} ({row['total_patents']} patents)")
        
    print("\nTop 5 Countries:")
    for idx, row in top_countries.head(5).iterrows():
        print(f"  {idx+1}. {row['country']} ({round(row['total_patents']/total_patents*100, 1)}%)")
    print("============================================================\n")
    
    print("Reports generated successfully in the 'reports' directory.")
    conn.close()

if __name__ == "__main__":
    generate_reports()
