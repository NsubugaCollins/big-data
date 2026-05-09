import os
import sys

def main():
    print("Starting Global Patent Intelligence Data Pipeline...")
    
    # Add root folder to sys.path in case scripts try to import each other
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    
    from scripts.extract import extract_data
    from scripts.clean import clean_data

    from scripts.report import generate_reports

    try:
        # Step 1: Extract data from PatentsView S3 URL to local storage
        extract_data()
        
        print("\n" + "-"*50 + "\n")
        
        # Step 2: Clean and format data from local files (and load into DB)
        clean_data()
        
        print("\n" + "-"*50 + "\n")
        
        # Step 4: Run Analytics & Generate Reports
        generate_reports()
        
        print("\nPipeline execution complete! You can now start the dashboard by running: streamlit run dashboard.py")
        
    except Exception as e:
        print(f"\nPipeline failed: {e}")

if __name__ == "__main__":
    main()
