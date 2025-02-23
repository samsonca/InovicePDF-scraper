import base64
import json
import requests
import sys
import os
import pyodbc


# Ensure the src folder is on the Python path
project_root = os.path.abspath(os.path.join(os.getcwd()))
sys.path.append(os.path.join(project_root, "src"))

# Import the transformation function
from transformation.transform_data import transform_extracted_data

# Generate the base64 string from your PDF
with open(r"C:\Users\SamsonC\Documents\Accounting\Accounting_AR\invoice_pdf\salefish-invoice.pdf", "rb") as f:
    pdf_bytes = f.read()
encoded_pdf = base64.b64encode(pdf_bytes).decode('utf-8')

# Define the URL of your Azure Function endpoint (local testing)
url = "http://localhost:7072/api/InvoiceExtractor"

# Create the payload with the encoded PDF
payload = {
    "fileContent": encoded_pdf
}

headers = {
    "Content-Type": "application/json"
}

# Send the POST request to test the Azure Function API endpoint
response = requests.post(url, data=json.dumps(payload), headers=headers)
print("Function API Response:")
print(response.text)


# For testing the transformation, let's assume the function output (extracted data)
# is similar to the following sample JSON (you can use the actual output from your API):
sample_extracted_data = {
    "invoice_number": "4560",
    "date": "2020-11-30",
    "client_name": "Branthaven Marz Inc.",
    "address": "720 Oval Court",
    "unit": "N/A",
    "building": "N/A",
    "city": "Burlington",
    "province": "ON",
    "postal_code": "L7L 6A9",
    "agreement_number": "A0224",
    "client_project": "Casa De Torri",
    "items": [
        ["To bill for Hosting and Upgrades as per section 3 of the contract: November, 2020", "1", "400.00", "400.00"],
        ["HST On Sales", "-", "13.00%", "52.00"]
    ]
}

extracted_data = json.loads(response.text)

# Transform the extracted data to match your database schema
client_data, invoice_data, invoice_items = transform_extracted_data(extracted_data)

print("\nTransformed Data:")
print("Client Data:")
print(json.dumps(client_data, indent=2))
print("\nInvoice Data:")
print(json.dumps(invoice_data, indent=2))
print("\nInvoice Items:")
print(json.dumps(invoice_items, indent=2))


# Azure Database connection
try:
    conn = pyodbc.connect(
        "DRIVER={ODBC Driver 18 for SQL Server};"
        "SERVER=tpgazsqlcadvault.database.windows.net;"
        "DATABASE=timesheet;"
        "UID=CADVaultAdmin;"
        "PWD=y2RF2*Yk5\\;"
        "Encrypt=yes;TrustServerCertificate=no;"
    )
    print("✅ Connection Successful!")
except Exception as e:
    print("❌ Connection Failed:", e)

# Azure SQL Database connection settings
# server = 'tpgazsqlcadvault.database.windows.net'
# database = 'timesheet'
# username = 'CADVaultAdmin'
# password =  'y2RF2*Yk5\\'
# driver = '{ODBC Driver 18 for SQL Server}'

# connection_string = (
#     f"DRIVER={driver};"
#     f"SERVER={server};"
#     f"DATABASE={database};"
#     f"UID={username};"
#     f"PWD={password}"
#     "Encrypt=yes;TrustServerCertificate=no;"

# )

# # Connect to Azure SQL Database
# conn = pyodbc.connect(connection_string)
cursor = conn.cursor()

def insert_client(client_data):
    # Check if client exists
    select_query = "SELECT ClientId FROM AR_Clients WHERE Name = ? AND Address = ?"
    cursor.execute(select_query, (client_data["Name"], client_data["Address"]))
    row = cursor.fetchone()
    if row:
        return row[0]
    else:
        insert_query = """
            INSERT INTO AR_Clients (Name, Address, City, Province, Postal)
            OUTPUT INSERTED.ClientId
            VALUES (?, ?, ?, ?, ?)
        """
        cursor.execute(insert_query, (
            client_data["Name"],
            client_data["Address"],
            client_data["City"],
            client_data["Province"],
            client_data["Postal"]
        ))
        return cursor.fetchone()[0]

def insert_invoice(invoice_data, client_id):
    insert_query = """
        INSERT INTO AR_Invoices (ClientId, InvoiceNumber, Date, AgreementNumber, Project)
        OUTPUT INSERTED.InvoiceId
        VALUES (?, ?, ?, ?, ?)
    """
    cursor.execute(insert_query, (
        client_id,
        invoice_data["InvoiceNumber"],
        invoice_data["Date"],
        invoice_data["AgreementNumber"],
        invoice_data["Project"]
    ))
    return cursor.fetchone()[0]

def insert_invoice_items(invoice_items, invoice_id):
    insert_query = """
        INSERT INTO AR_Invoice_Items (InvoiceId, Description, Quantity, Rate, Amount)
        VALUES (?, ?, ?, ?, ?)
    """
    for item in invoice_items:
        cursor.execute(insert_query, (
            invoice_id,
            item["Description"],
            item["Quantity"],
            item["Rate"],
            item["Amount"]
        ))

try:
    # Insert or retrieve the client record
    client_id = insert_client(client_data)
    # Insert the invoice record
    invoice_id = insert_invoice(invoice_data, client_id)
    # Insert all invoice items for the invoice
    insert_invoice_items(invoice_items, invoice_id)
    
    conn.commit()
    print("Data inserted successfully!")
except Exception as e:
    conn.rollback()
    print("Error inserting data:", e)
finally:
    cursor.close()
    conn.close()