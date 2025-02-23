import pyodbc

# Database Connection Setup
def get_database_connection():
    try:
        conn = pyodbc.connect(
            "DRIVER={ODBC Driver 18 for SQL Server};"
            "SERVER=tpgazsqlcadvault.database.windows.net;"
            "DATABASE=timesheet;"
            "UID=CADVaultAdmin;"
            "PWD=y2RF2*Yk5\\;"
            "Encrypt=yes;TrustServerCertificate=no;"
        )
        return conn
    except Exception as e:
        print("❌ Database Connection Failed:", e)
        return None


# Insert Client
def insert_client(cursor, client_data):
    select_query = "SELECT Id FROM AR_Clients WHERE Name = ? AND Address = ?"
    cursor.execute(select_query, (client_data["Name"], client_data["Address"]))
    row = cursor.fetchone()

    if row:
        return row[0]  # Existing client found

    insert_query = """
        INSERT INTO AR_Clients (Name, Address, City, Province, PostalCode)
        OUTPUT INSERTED.Id
        VALUES (?, ?, ?, ?, ?)
    """
    cursor.execute(insert_query, (
        client_data["Name"],
        client_data["Address"],
        client_data["City"],
        client_data["Province"],
        client_data["Postal"]
    ))
    return cursor.fetchone()[0]  #  Return new ClientId


# Insert Invoice
def insert_invoice(cursor, invoice_data, client_id):
    """
    Insert invoice data into AR_Invoices and return the generated InvoiceId.
    """
    insert_query = """
        INSERT INTO AR_Invoices (ClientId, InvoiceNumber, ProjectNumber, InvoiceDate, Terms, TotalAmount, Status)
        OUTPUT INSERTED.Id
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """
    # For invoice insertion
    print("Inserting Invoice with values:")
    print("InvoiceNumber:", invoice_data["InvoiceNumber"])
    print("ProjectNumber:", invoice_data["ProjectNumber"])
    print("InvoiceDate:", invoice_data["InvoiceDate"])
    print("Terms:", invoice_data["Terms"])
    print("TotalAmount:", invoice_data["TotalAmount"])
    print("Status:", invoice_data["Status"])

    cursor.execute(insert_query, (
        client_id,
        invoice_data["InvoiceNumber"], 
        invoice_data["ProjectNumber"], 
        invoice_data["InvoiceDate"],
        invoice_data["Terms"],
        invoice_data["TotalAmount"],
        invoice_data["Status"]
    ))
    return cursor.fetchone()[0]  # Get inserted InvoiceId



# Insert Invoice Items
def insert_invoice_items(cursor, invoice_items, invoice_id):
    insert_query = """
        INSERT INTO AR_Invoice_Items (InvoiceId, Description, Quantity, Rate, Amount)
        VALUES (?, ?, ?, ?, ?)
    """
    for item in invoice_items:
        print("Inserting Invoice Item with values:")
        print("Description:", item["Description"])
        print("Quantity:", item["Quantity"])
        print("Rate:", item["Rate"])
        print("Amount:", item["Amount"])

    for item in invoice_items:
        quantity = clean_numeric(item["Quantity"])
        rate = clean_numeric(item["Rate"])
        amount = clean_numeric(item["Amount"])
        cursor.execute(insert_query, (
            invoice_id,
            item["Description"],
            quantity,
            rate,
            amount
        ))

    # for item in invoice_items:
    #     cursor.execute(insert_query, (
    #         invoice_id,
    #         item["Description"],
    #         item["Quantity"],
    #         item["Rate"],
    #         item["Amount"]
    #     ))


# Insert Payment (if applicable)
def insert_payment(cursor, payment_data, invoice_id):
    insert_query = """
        INSERT INTO AR_Payments (InvoiceId, PaymentDate, AmountPaid, PaymentMethod, ReferenceNumber)
        VALUES (?, ?, ?, ?, ?)
    """
    cursor.execute(insert_query, (
        invoice_id,
        payment_data["PaymentDate"],
        payment_data["AmountPaid"],
        payment_data["PaymentMethod"],
        payment_data["ReferenceNumber"]
    ))

def clean_numeric(value):
    if isinstance(value, str):
        # Remove percentage symbols and extra spaces
        value = value.replace("%", "").strip()
        try:
            return float(value)
        except ValueError:
            # Return 0 or handle as needed if conversion fails
            return 0.0
    return float(value)