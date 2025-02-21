import logging
import azure.functions as func
import json
import base64
import tempfile
import os
import sys

# Ensure your src folder is on the Python path
current_dir = os.path.dirname(os.path.realpath(__file__))
parent_dir = os.path.join(current_dir, "..")
sys.path.append(os.path.join(parent_dir, "src"))

from extraction.pdf_parser import extract_invoice_data

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Processing a PDF invoice HTTP request.')
    try:
        req_body = req.get_json()
        pdf_base64 = req_body.get('fileContent')
        if not pdf_base64:
            return func.HttpResponse("No file content provided", status_code=400)

        # Decode base64 to bytes
        pdf_bytes = base64.b64decode(pdf_base64)
        # Write to a temporary file so pdf_parser can read it
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp_file:
            tmp_file.write(pdf_bytes)
            tmp_file_path = tmp_file.name

        # Process the PDF to extract invoice data
        invoice_data = extract_invoice_data(tmp_file_path)

        # Return the extracted data as JSON
        return func.HttpResponse(
            json.dumps(invoice_data),
            status_code=200,
            mimetype="application/json"
        )
    except Exception as e:
        logging.error(f"Error processing invoice: {e}")
        return func.HttpResponse("Internal Server Error", status_code=500)
