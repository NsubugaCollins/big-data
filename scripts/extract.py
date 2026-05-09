import os
import urllib.request
import zipfile
import shutil

import subprocess

def download_file(url, target_path):
    print(f"   -> Downloading {url} using wget...")
    # Using wget -c to allow continuing interrupted downloads
    subprocess.run(["wget", "-c", url, "-O", target_path], check=True)

def extract_data():
    """
    Downloads and extracts raw patent data from PatentsView S3 storage.
    """
    print("Beginning USPTO data extraction from PatentsView...")
    
    BASE_URL = "https://s3.amazonaws.com/data.patentsview.org/download"
    RAW_DIR = "data/raw"
    os.makedirs(RAW_DIR, exist_ok=True)
    
    files_to_download = [
        "g_patent.tsv.zip",
        "g_patent_abstract.tsv.zip",
        "g_application.tsv.zip",
        "g_location_disambiguated.tsv.zip",
        "g_inventor_disambiguated.tsv.zip",
        "g_assignee_disambiguated.tsv.zip"
    ]
    
    for file_zip in files_to_download:
        zip_path = os.path.join(RAW_DIR, file_zip)
        tsv_name = file_zip.replace(".zip", "")
        tsv_path = os.path.join(RAW_DIR, tsv_name)
        
        # Check if already extracted
        if os.path.exists(tsv_path):
            print(f"   -> {tsv_name} already exists. Skipping.")
            continue
            
        # Download
        download_file(f"{BASE_URL}/{file_zip}", zip_path)
        
        # Extract
        print(f"   -> Extracting {file_zip}...")
        with zipfile.ZipFile(zip_path, 'r') as z:
            z.extractall(RAW_DIR)
            
        # Cleanup zip
        os.remove(zip_path)
        print(f"   -> Successfully extracted {tsv_name}")

if __name__ == "__main__":
    extract_data()
