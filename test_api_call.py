import base64
import json
import requests

# generate base64 string from PDF
with open(r"C:\Users\SamsonC\Documents\Accounting\Accounting_AR\invoice_pdf\salefish-invoice.pdf", "rb") as f:
    pdf_bytes = f.read()
encoded_pdf = base64.b64encode(pdf_bytes).decode('utf-8')

# save base64 to a text file
with open("encoded_pdf.txt", "w") as outfile:
    outfile.write(encoded_pdf)


# Azure Function endpoint
url = "http://localhost:7072/api/InvoiceExtractor"

#cCreate the payload with the encoded PDF
payload = {
    "fileContent": encoded_pdf
}

headers = {
    "Content-Type": "application/json"
}

# send the POST request
response = requests.post(url, data=json.dumps(payload), headers=headers)
print(response.text)
