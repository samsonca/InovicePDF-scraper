from src.extraction.sharepoint_reader import get_pdf_files
from src.extraction.pdf_parser import extract_invoice_data
from src.database.azure_db import insert_invoice_data

def process_invoices():
    """Full process: Fetch PDFs, extract data, save to Azure SQL."""
    pdf_files = get_pdf_files()
    
    for filename, pdf_stream in pdf_files:
        print(f"Processing {filename}...")
        invoice_data = extract_invoice_data(pdf_stream)
        insert_invoice_data(invoice_data)
    
    print("All invoices processed successfully!")

if __name__ == "__main__":
    process_invoices()
