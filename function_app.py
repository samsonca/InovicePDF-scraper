
import logging
import azure.functions as func
import json
import base64
import tempfile
import os
import sys

# Ensure the src folder is on the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from extraction.pdf_parser import extract_invoice_data
from transformation.transform_data import transform_extracted_data

app = func.FunctionApp()

@app.function_name(name="InvoiceExtractor")
@app.route(route="InvoiceExtractor", auth_level=func.AuthLevel.ANONYMOUS)
def InvoiceDataExtractor(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("[START] InvoiceDataExtractor function triggered.")

    try:
        req_body = req.get_json()
        logging.info(f"Received payload: {req_body}")

        pdf_base64 = req_body.get("fileContent")
        if not pdf_base64:
            logging.error("No file content provided in request.")
            return func.HttpResponse(
                json.dumps({"error": "No file content provided"}),
                status_code=400,
                mimetype="application/json"
            )

        try:
            pdf_bytes = base64.b64decode(pdf_base64)
            logging.info("Base64 decoding successful.")
        except Exception as e:
            logging.error(f"Base64 decoding error: {e}")
            return func.HttpResponse(
                json.dumps({"error": "Invalid Base64 encoding"}),
                status_code=400,
                mimetype="application/json"
            )

        try:
            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp_file:
                tmp_file.write(pdf_bytes)
                tmp_file_path = tmp_file.name
            logging.info(f"Temporary PDF file saved at: {tmp_file_path}")
        except Exception as e:
            logging.error(f"Error saving temp file: {e}")
            return func.HttpResponse(
                json.dumps({"error": "Failed to save temp file"}),
                status_code=500,
                mimetype="application/json"
            )

        try:
            raw_invoice_data = extract_invoice_data(tmp_file_path)
            logging.info(f"Extracted invoice data: {raw_invoice_data}")
        except Exception as e:
            logging.error(f"Invoice extraction failed: {e}")
            return func.HttpResponse(
                json.dumps({"error": "Invoice extraction failed"}),
                status_code=500,
                mimetype="application/json"
            )

        if os.path.exists(tmp_file_path):
            os.remove(tmp_file_path)
            logging.info("Temporary file deleted.")

        try:
            client_data, invoice_data, invoice_items = transform_extracted_data(raw_invoice_data)
        except Exception as e:
            logging.error(f"Data transformation failed: {e}")
            return func.HttpResponse(
                json.dumps({"error": "Data transformation failed"}),
                status_code=500,
                mimetype="application/json"
            )

        response_data = {
            "message": "Extraction successful",
            "data": {
                "client_data": client_data,
                "invoice_data": invoice_data,
                "invoice_items": invoice_items
            }
        }
        logging.info(f"Sending response: {response_data}")

        return func.HttpResponse(
            json.dumps(response_data),
            status_code=200,
            mimetype="application/json"
        )

    except Exception as e:
        logging.error(f"Unexpected server error: {e}")
        return func.HttpResponse(
            json.dumps({"error": "Internal Server Error"}),
            status_code=500,
            mimetype="application/json"
        )

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("[ENTRY] Main function called.")
    return InvoiceDataExtractor(req)
