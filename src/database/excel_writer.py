import pandas as pd
import os

def save_to_excel(invoice_data, filename="invoices.xlsx"):
    """
    Saves extracted invoice data in Excel format.
    - Checks if Invoice No already exists before appending.
    - Stores invoice metadata in "Invoices" sheet.
    - Stores line items in "Line_Items" sheet.
    """

    invoice_columns = [
        "Invoice No", "Date", "Client Name", "Address", "Unit", "Building", "City", "Province", "Postal Code",
        "Agreement No", "Client Project"
    ]

    line_item_columns = [
        "Invoice No", "Description", "Qty", "Rate", "Price"
    ]

    # Create DataFrame for invoice metadata
    invoice_df = pd.DataFrame([[
        invoice_data["invoice_number"], invoice_data["date"], invoice_data["client_name"],
        invoice_data["address"], invoice_data["unit"], invoice_data["building"], invoice_data["city"],
        invoice_data["province"], invoice_data["postal_code"],
        invoice_data["agreement_number"], invoice_data["client_project"]
    ]], columns=invoice_columns)

    # Create DataFrame for line items
    line_item_records = [
        [invoice_data["invoice_number"], description, qty, rate, price]
        for description, qty, rate, price in invoice_data["items"]
    ]
    line_item_df = pd.DataFrame(line_item_records, columns=line_item_columns)

    # Check if the file exists
    if os.path.exists(filename):
        with pd.ExcelWriter(filename, mode="a", engine="openpyxl", if_sheet_exists="overlay") as writer:
            # Load existing data
            existing_invoices = pd.read_excel(filename, sheet_name="Invoices")

            # **Check if Invoice No already exists**
            if invoice_data["invoice_number"] in existing_invoices["Invoice No"].values:
                print(f"🚨 Invoice {invoice_data['invoice_number']} already exists. Skipping.")
                return  # Stop processing this invoice
            
            # Append new invoice data
            invoice_df.to_excel(writer, sheet_name="Invoices", index=False, header=False, startrow=len(existing_invoices)+1)
            
            # Append new line items
            existing_items = pd.read_excel(filename, sheet_name="Line_Items")
            line_item_df.to_excel(writer, sheet_name="Line_Items", index=False, header=False, startrow=len(existing_items)+1)

    else:
        # Create new Excel file with both sheets
        with pd.ExcelWriter(filename, engine="openpyxl") as writer:
            invoice_df.to_excel(writer, sheet_name="Invoices", index=False)
            line_item_df.to_excel(writer, sheet_name="Line_Items", index=False)

    print(f"✅ New invoice {invoice_data['invoice_number']} saved to {filename}")
