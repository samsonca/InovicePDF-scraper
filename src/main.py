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
project_root = os.path.abspath(os.path.join(os.getcwd(), "..")) 

# Add `src` folder to Python's module search path
sys.path.append(os.path.join(project_root, "src"))

from extraction.pdf_parser import extract_invoice_data
from database.excel_writer import save_to_excel  # Optional, for review

# Folder containing PDF invoices
# INVOICE_FOLDER = r"C:\Users\SamsonC\Documents\Accounting\Accounting_AR\invoice_pdf"
INVOICE_FOLDER =  r"C:\Users\SamsonC\Documents\Accounting\Accounting_AR\Selfish\Misc"
#     pdf_path = r"C:\Users\SamsonC\Documents\Accounting\Accounting_AR\invoice_pdf\8713.pdf"


def process_invoices():
    """Extract data from multiple PDFs in a folder."""
    for filename in os.listdir(INVOICE_FOLDER):
        if filename.endswith(".pdf"):
            pdf_path = os.path.join(INVOICE_FOLDER, filename)
            print(f"📄 Processing: {filename}")

            # Extract data
            invoice_data = extract_invoice_data(pdf_path)

            # Save to Excel (optional, for validation before SQL)
            save_to_excel(invoice_data, "invoices.xlsx")  
            print(f"✅ Extracted data from {filename} and saved to Excel")

    print("🎉 All invoices processed successfully!")

if __name__ == "__main__":
    process_invoices()
