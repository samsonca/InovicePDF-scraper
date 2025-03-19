import logging
import azure.functions as func
import json
import base64
import tempfile
import os
import sys

# current_dir = os.path.dirname(os.path.realpath(__file__))
# parent_dir = os.path.join(current_dir, "..")
# sys.path.append(os.path.join(parent_dir, "src"))
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))


from extraction.pdf_parser import extract_invoice_data  # Your PDF extraction function

app = func.FunctionApp()

@app.function_name(name="InvoiceExtractor")
@app.route(route="InvoiceExtractor", auth_level=func.AuthLevel.ANONYMOUS)
def InvoiceDataExtractor(req: func.HttpRequest) -> func.HttpResponse:
    # logging.info("📄 Function triggered")
    
    # try:
    #     # Add this to handle POST body
    #     req_body = req.get_json()
    #     logging.info(f"Received payload: {req_body}")
    # except ValueError:
    #     pass  # Ignore if no body for testing
    
    # dummy_response = {
    #     "message": "Extraction successful",
    #     "data": {"dummy": "value"}
    # }
    
    # return func.HttpResponse(
    #     json.dumps(dummy_response),
    #     status_code=200,
    #     mimetype="application/json"
    # )
    logging.info("📄 [START] InvoiceDataExtractor function triggered.")

    try:
        req_body = req.get_json()
        logging.info(f"📥 Received payload: {req_body}")

        pdf_base64 = req_body.get("fileContent")

        if not pdf_base64:
            logging.error("❌ No file content provided in request.")
            return func.HttpResponse(
                json.dumps({"error": "No file content provided"}),
                status_code=400,
                mimetype="application/json"
            )

        # Decode Base64 PDF
        try:
            pdf_bytes = base64.b64decode(pdf_base64)
            logging.info("✅ Base64 decoding successful.")
        except Exception as e:
            logging.error(f"❌ Base64 decoding error: {e}")
            return func.HttpResponse(
                json.dumps({"error": "Invalid Base64 encoding"}),
                status_code=400,
                mimetype="application/json"
            )

        # Save PDF to temp file
        try:
            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp_file:
                tmp_file.write(pdf_bytes)
                tmp_file_path = tmp_file.name
            logging.info(f"📂 Temporary PDF file saved at: {tmp_file_path}")
        except Exception as e:
            logging.error(f"❌ Error saving temp file: {e}")
            return func.HttpResponse(
                json.dumps({"error": "Failed to save temp file"}),
                status_code=500,
                mimetype="application/json"
            )

        # Extract invoice data
        try:
            invoice_data = extract_invoice_data(tmp_file_path)
            logging.info(f"✅ Extracted invoice data: {invoice_data}")
        except Exception as e:
            logging.error(f"❌ Invoice extraction failed: {e}")
            return func.HttpResponse(
                json.dumps({"error": "Invoice extraction failed"}),
                status_code=500,
                mimetype="application/json"
            )

        # Cleanup temp file
        if os.path.exists(tmp_file_path):
            os.remove(tmp_file_path)
            logging.info("🧹 Temporary file deleted.")

        # ✅ Ensure function always returns a response
        response_data = {
            "message": "Extraction successful",
            "data": invoice_data
        }
        logging.info(f"📤 Sending response: {response_data}")

        return func.HttpResponse(
            json.dumps(response_data),
            status_code=200,
            mimetype="application/json"
        )

    except Exception as e:
        logging.error(f"❌ Unexpected server error: {e}")
        return func.HttpResponse(
            json.dumps({"error": "Internal Server Error"}),
            status_code=500,
            mimetype="application/json"
        )

# ✅ Explicitly define the main entry point for Azure Functions
def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("✅ [ENTRY] Main function called.")
    return InvoiceDataExtractor(req)
