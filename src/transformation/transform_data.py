def transform_extracted_data(extracted):
    """
    Map the raw extracted JSON to a format that matches your database schema.
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

    # Map fields for AR_Invoices
    invoice_data = {
        "InvoiceNumber": extracted.get("invoice_number"),  
        "ProjectNumber": extracted.get("agreement_number"), 
        "InvoiceDate": extracted.get("date"),
        "Terms": extracted.get("term", "Net 30"),  
        "TotalAmount": round(sum(float(item[3]) for item in extracted.get("items", [])), 2),
        "Project": extracted.get("client_project"),
        "Status": "Pending"  # Default Status
    }

    # Map line items for AR_Invoice_Items
    invoice_items = []
    for item in extracted.get("items", []):
        # Assuming item format: [Description, Qty, Rate, Amount]
        invoice_items.append({
            "Description": item[0],
            "Quantity": item[1],
            "Rate": item[2],
            "Amount": item[3]
        })

    return client_data, invoice_data, invoice_items
