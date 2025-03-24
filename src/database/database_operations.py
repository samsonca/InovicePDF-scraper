# import pyodbc
from datetime import datetime

# Database Connection Setup
# def get_database_connection():
#     try:
#         conn = pyodbc.connect(
#             "DRIVER={ODBC Driver 18 for SQL Server};"
#             "SERVER=tpgazsqlcadvault.database.windows.net;"
#             "DATABASE=timesheet;"
#             "UID=CADVaultAdmin;"
#             "PWD=y2RF2*Yk5\\;"
#             "Encrypt=yes;TrustServerCertificate=no;"
#         )
#         return conn
#     except Exception as e:
#         print("❌ Database Connection Failed:", e)
#         return None

# Insert Client
def insert_client(cursor, client_data):
    select_query = "SELECT Id FROM AR_Clients WHERE Name = ? AND Address = ?"
    cursor.execute(select_query, (client_data["Name"], client_data["Address"]))
    row = cursor.fetchone()
    if row:
        return row[0]
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
    return cursor.fetchone()[0]

# Insert Invoice
def insert_invoice(cursor, invoice_data, client_id):
    select_query = "SELECT Id FROM AR_Invoices WHERE InvoiceNumber = ? AND ClientId = ?"
    cursor.execute(select_query, (invoice_data["InvoiceNumber"], client_id))
    row = cursor.fetchone()
    if row:
        print("Invoice already exists, skipping insertion.")
        return row[0]

    # Ensure InvoiceDate is not null (should be a string)
    invoice_date = invoice_data.get("InvoiceDate") or '1900-01-01'
    
    insert_query = """
        INSERT INTO AR_Invoices (ClientId, InvoiceNumber, ProjectNumber, InvoiceDate, Terms, TotalAmount, Status)
        OUTPUT INSERTED.Id
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """
    print("Inserting Invoice with values:")
    print("InvoiceNumber:", invoice_data["InvoiceNumber"])
    print("ProjectNumber:", invoice_data["ProjectNumber"])
    print("InvoiceDate:", invoice_date)
    print("Terms:", invoice_data["Terms"])
    print("TotalAmount:", invoice_data["TotalAmount"])
    print("Status:", invoice_data["Status"])
    
    cursor.execute(insert_query, (
        client_id,
        invoice_data["InvoiceNumber"],
        invoice_data["ProjectNumber"],
        invoice_date,
        invoice_data["Terms"],
        invoice_data["TotalAmount"],
        invoice_data["Status"]
    ))
    return cursor.fetchone()[0]

# Insert Invoice Items
def insert_invoice_items(cursor, invoice_items, invoice_id):
    insert_query = """
        INSERT INTO AR_Invoice_Items (InvoiceId, Description, Quantity, Rate, Amount)
        VALUES (?, ?, ?, ?, ?)
    """
    select_query = """
        SELECT COUNT(1) FROM AR_Invoice_Items 
        WHERE InvoiceId = ? AND Description = ? AND Quantity = ? AND Rate = ? AND Amount = ?
    """
    for item in invoice_items:
        quantity = clean_numeric(item["Quantity"])
        rate = clean_numeric(item["Rate"])
        amount = clean_numeric(item["Amount"])

        print("Inserting Invoice Item with values:")
        print("Description:", item["Description"])
        print("Quantity:", quantity)
        print("Rate:", rate)
        print("Amount:", amount)

        cursor.execute(select_query, (invoice_id, item["Description"], quantity, rate, amount))
        row = cursor.fetchone()
        if row and row[0] > 0:
            print("Invoice item already exists, skipping insertion.")
            continue

        cursor.execute(insert_query, (
            invoice_id,
            item["Description"],
            quantity,
            rate,
            amount
        ))

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
    """
    Cleans a numeric string by removing commas, percentage symbols, and currency symbols,
    then converts it to a float.
    Returns 0.0 if conversion fails.
    """
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        cleaned = value.replace(',', '').replace('$', '').replace('%', '').strip()
        try:
            return float(cleaned)
        except ValueError:
            return 0.0
    return 0.0

def format_invoice_date(raw_date):
    """
    Parses the raw date string and returns a formatted date string (YYYY-MM-DD).
    Returns a default date '1900-01-01' if parsing fails.
    """
    if raw_date:
        try:
            date_obj = datetime.strptime(raw_date, '%Y-%m-%d')
        except ValueError:
            try:
                date_obj = datetime.strptime(raw_date, '%d/%m/%Y')
            except ValueError:
                date_obj = None
    else:
        date_obj = None

    if date_obj:
        return date_obj.strftime('%Y-%m-%d')
    else:
        return '1900-01-01'

def clean_date(date_str):
    try:
        return datetime.strptime(date_str, '%Y-%m-%d').date()
    except (ValueError, TypeError):
        return None
