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

# Import the transformation function and database operations (if needed later)
from transformation.transform_data import transform_extracted_data
from database.database_operations import get_database_connection, insert_client, insert_invoice, insert_invoice_items

# API and Config
API_URL = os.getenv("INVOICE_EXTRACTOR_URL")
if not API_URL:
    raise Exception("INVOICE_EXTRACTOR_URL is not set in the environment variables")

headers = {"Content-Type": "application/json"}

# Test payload for a simple test call (adjust payload as needed for your function)
payload = {"InvoiceDataExtractor": "TestUser"}

response = requests.post(API_URL, data=json.dumps(payload), headers=headers)

if response.status_code == 200:
    print("✅ Successfully received response:")
    print(response.text)
else:
    print(f"❌ API Request Failed: {response.status_code}, {response.text}")