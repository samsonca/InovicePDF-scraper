import pyodbc
from config.settings import AZURE_DB_CONNECTION_STRING

def insert_invoice_data(invoice_data):
    """Insert extracted invoice data into Azure SQL."""
    conn = pyodbc.connect(AZURE_DB_CONNECTION_STRING)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO Invoices (Date, InvoiceNo)
        VALUES (?, ?)
    """, invoice_data["date"], invoice_data["invoice_number"])

    conn.commit()
    cursor.close()
    conn.close()
