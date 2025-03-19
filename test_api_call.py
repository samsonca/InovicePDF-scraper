import base64
import json
import requests
import sys
import os
import pyodbc
import time
import psutil 
from dotenv import load_dotenv

load_dotenv()


# Ensure the src folder is on the Python path
project_root = os.path.abspath(os.path.join(os.getcwd()))
sys.path.append(os.path.join(project_root, "src"))

# Import the transformation function
from transformation.transform_data import transform_extracted_data
from database.database_operations import get_database_connection, insert_client, insert_invoice, insert_invoice_items


# API and Config
# url = "http://localhost:7072/api/InvoiceExtractor"
API_URL = os.getenv("INVOICE_EXTRACTOR_URL")

if not API_URL:
    raise Exception("INVOICE_EXTRACTOR_URL is not set in the environment variables")

headers = {"Content-Type": "application/json"}
INVOICE_FOLDER = r"C:\Users\SamsonC\Documents\Accounting\Accounting_AR\Selfish\Misc"

payload = {"InvoiceDataExtractor": "TestUser"}

response = requests.post(API_URL, data=json.dumps(payload), headers=headers)

if response.status_code == 200:
    print("✅ Successfully received response:")
    print(response.text)
else:
    print(f"❌ API Request Failed: {response.status_code}, {response.text}")

# Azure SQL Database connection settings
connection_string = (
    "DRIVER={ODBC Driver 18 for SQL Server};"
    "SERVER=tpgazsqlcadvault.database.windows.net;"
    "DATABASE=timesheet;"
    "UID=CADVaultAdmin;"
    "PWD=y2RF2*Yk5\\;"  # Ensure proper escaping
    "Encrypt=yes;TrustServerCertificate=no;"
)

# Track time and memory
total_start_time = time.time()
process = psutil.Process(os.getpid())  # Get current process
start_memory = process.memory_info().rss / (1024 * 1024)  # Convert to MB

# Connect to the database
conn = get_database_connection()
if not conn:
    print("❌ Exiting: Database connection failed")
    sys.exit(1)
cursor = conn.cursor()

# Process each PDF in the folder
for filename in os.listdir(INVOICE_FOLDER):
    if filename.endswith(".pdf"):  # Process only PDF files
        pdf_path = os.path.join(INVOICE_FOLDER, filename)
        print(f"\n📄 Processing: {filename}")

        file_start_time = time.time()  # Start timer for this file

        try:
            # Read the PDF and encode to Base64
            with open(pdf_path, "rb") as f:
                pdf_bytes = f.read()
            encoded_pdf = base64.b64encode(pdf_bytes).decode('utf-8')

            # send API request
            payload = {"fileContent": encoded_pdf}
            response = requests.post(url, data=json.dumps(payload), headers=headers)

            if response.status_code == 200:
                print(f"✅ Successfully processed {filename}")

                try:
                    extracted_data = response.json()  # Parse response as JSON
                except json.JSONDecodeError:
                    print(f"❌ JSON Decoding Failed for {filename}")
                    continue  # Skip to next file

                # Transform extracted data to match the database schema
                client_data, invoice_data, invoice_items = transform_extracted_data(extracted_data)

                print("\nTransformed Data:")
                print(f"Client Data: {json.dumps(client_data, indent=2)}")
                print(f"Invoice Data: {json.dumps(invoice_data, indent=2)}")
                print(f"Invoice Items: {json.dumps(invoice_items, indent=2)}")

                # Insert into SQL Database
                try:
                    client_id = insert_client(cursor, client_data)
                    invoice_id = insert_invoice(cursor, invoice_data, client_id)
                    insert_invoice_items(cursor, invoice_items, invoice_id)

                    conn.commit()  
                    print(f"✅ Data for {filename} inserted successfully!")

                except Exception as e:
                    conn.rollback()
                    print(f"❌ Error inserting data for {filename}: {e}")

            else:
                print(f"❌ API Request Failed for {filename}: {response.status_code}, {response.text}")

        except Exception as e:
            print(f"❌ Error processing {filename}: {e}")

        file_end_time = time.time()
        file_duration = file_end_time - file_start_time
        print(f"⏱️ Processing time for {filename}: {file_duration:.2f} seconds")

# End overall processing timer
total_end_time = time.time()
total_duration = total_end_time - total_start_time

# Track memory after processing
end_memory = process.memory_info().rss / (1024 * 1024)  # Convert to MB
memory_used = end_memory - start_memory

# Close database connection after all files are processed
cursor.close()
conn.close()

print("\n🎉 All PDFs in the folder have been processed and stored in the database!")
print(f"⏱️ Total processing time: {total_duration:.2f} seconds")
print(f"💾 Total memory used: {memory_used:.2f} MB")
