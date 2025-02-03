import pandas as pd
import os

def save_to_excel(invoice_data, filename="invoices.xlsx"):
    """
    Saves extracted invoice data into an Excel file in table format.
    Appends data if the file already exists.
    """
    # Define the updated columns based on extracted data structure
    columns = [
        "Invoice No", "Date", "Client Name", "Address", "Unit", "City", "Province", "Postal Code",
        "Agreement No", "Client Project", "Description", "Qty", "Rate", "Price"
    ]

    # Convert invoice_data dictionary into a DataFrame
    invoice_records = []
    
    # Process each item in the invoice
    for description, qty, rate, price in invoice_data["items"]:
        invoice_records.append([
            invoice_data["invoice_number"], invoice_data["date"], invoice_data["client_name"],
            invoice_data["address"], invoice_data["unit"], invoice_data["city"],
            invoice_data["province"], invoice_data["postal_code"],
            invoice_data["agreement_number"], invoice_data["client_project"],
            description, qty, rate, price
        ])

    df_new = pd.DataFrame(invoice_records, columns=columns)

    # Check if the file exists, if so, append instead of overwriting
    if os.path.exists(filename):
        df_existing = pd.read_excel(filename)
        df_combined = pd.concat([df_existing, df_new], ignore_index=True)
    else:
        df_combined = df_new

    # Save to Excel
    df_combined.to_excel(filename, index=False)
    print(f"✅ Data successfully saved to {filename}")
