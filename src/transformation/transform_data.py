from database.database_operations import format_invoice_date

def transform_extracted_data(extracted):
    """
    Maps raw extracted JSON to a format that matches your database schema.
    Returns dictionaries for clients, invoices, and invoice items.
    """
    # Map fields for AR_Clients
    client_data = {
        "Name": extracted.get("client_name"),
        "Address": extracted.get("address"),
        "City": extracted.get("city"),
        "Province": extracted.get("province"),
        "Postal": extracted.get("postal_code")
    }

    # Use the shared function to process and format InvoiceDate.
    invoice_date = format_invoice_date(extracted.get("date"))

    # Process TotalAmount by cleaning each numeric string in items.
    total_amount = 0.0
    for item in extracted.get("items", []):
        try:
            cleaned = item[3].replace(',', '').replace('$', '').replace('%', '').strip()
            total_amount += float(cleaned)
        except Exception:
            continue

    invoice_data = {
        "InvoiceNumber": extracted.get("invoice_number"),
        "ProjectNumber": extracted.get("agreement_number"),
        "InvoiceDate": invoice_date,
        "Terms": extracted.get("term", "Net 30"),
        "TotalAmount": total_amount,
        "Project": extracted.get("client_project"),
        "Status": "Pending"
    }

    invoice_items = []
    for item in extracted.get("items", []):
        invoice_items.append({
            "Description": item[0],
            "Quantity": item[1],
            "Rate": item[2],
            "Amount": item[3]
        })

    return client_data, invoice_data, invoice_items
