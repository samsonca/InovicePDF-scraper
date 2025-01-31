import pdfplumber
import re

def extract_invoice_data(pdf_stream):
    """Extract invoice details from a PDF stream."""
    with pdfplumber.open(pdf_stream) as pdf:
        text = "\n".join(page.extract_text() for page in pdf.pages if page.extract_text())

    # Extract Date
    date_match = re.search(r'Date:\s*(\d{4}-\d{2}-\d{2})', text)
    date = date_match.group(1) if date_match else "Not Found"

    # Extract Invoice No
    invoice_match = re.search(r'Invoice No:\s*(\d+)', text)
    invoice_number = invoice_match.group(1) if invoice_match else "Not Found"

    return {"date": date, "invoice_number": invoice_number, "raw_text": text}
