import base64
import json
import requests
import sys
import os

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
