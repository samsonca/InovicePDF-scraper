# import sys
# import os
# project_root = os.path.abspath(os.path.join(os.getcwd(), "..")) 

# # Add `src` folder to Python's module search path
# sys.path.append(os.path.join(project_root, "src"))

# from extraction.pdf_parser import extract_invoice_data
# from database.excel_writer import save_to_excel

# def process_invoice():
#     """Extract invoice data from PDF and save it to Excel."""
#     pdf_path = r"C:\Users\SamsonC\Documents\Accounting\Accounting_AR\invoice_pdf\8713.pdf"
#     invoice_data = extract_invoice_data(pdf_path)

#     save_to_excel(invoice_data, "invoices.xlsx")
#     print("✅ Invoice data processed and saved to Excel!")

# if __name__ == "__main__":
#     process_invoice()
import sys
import os
import time

# Set up the project path to include the 'src' folder
project_root = os.path.abspath(os.path.join(os.getcwd(), ".."))
sys.path.append(os.path.join(project_root, "src"))

from extraction.RN_Scraper import extract_rn_invoice_data
from database.excel_writer import save_to_excel  # Optional, for validation before SQL

# Folder containing PDF invoices
INVOICE_FOLDER = r"C:\Users\SamsonC\Documents\Accounting\Accounting_AR\RN"

def process_invoices():
    """Extract data from multiple PDFs in a folder and log processing times."""
    total_start = time.time()
    invoice_count = 0

    for filename in os.listdir(INVOICE_FOLDER):
        if filename.endswith(".pdf"):
            invoice_count += 1
            file_start = time.time()
            pdf_path = os.path.join(INVOICE_FOLDER, filename)
            print(f"📄 Processing: {filename}")

            # Extract data
            invoice_data = extract_rn_invoice_data(pdf_path)
            
            # Save to Excel (optional, for validation before SQL)
            save_to_excel(invoice_data, "rn_invoices.xlsx")
            file_end = time.time()
            
            print(f"✅ Extracted data from {filename} and saved to Excel in {file_end - file_start:.2f} seconds")

    total_end = time.time()
    print(f"🎉 Processed {invoice_count} invoice(s) in {total_end - total_start:.2f} seconds!")

if __name__ == "__main__":
    process_invoices()
