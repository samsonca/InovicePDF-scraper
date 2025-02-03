import pdfplumber
import re

def extract_invoice_data(pdf_path):
    """Extracts structured invoice details from a given PDF file."""
    with pdfplumber.open(pdf_path) as pdf:
        text = "\n".join(page.extract_text() for page in pdf.pages if page.extract_text())

    lines = text.split("\n")  # Split text into lines for processing

    # Extract Invoice Header Data
    date_match = re.search(r'Date:\s*(\d{4}-\d{2}-\d{2})', text)
    invoice_match = re.search(r'Invoice No:\s*(\d+)', text)
    client_match = re.search(r'Client:\s*([A-Za-z\s.,-]+)', text)

    date = date_match.group(1) if date_match else "Date not found"
    invoice_number = invoice_match.group(1) if invoice_match else "Invoice No not found"
    client_name = client_match.group(1).strip() if client_match else "Client not found"

    # Extract Address Details (Unit, City, Province, Postal Code)
    extracted_address, unit, city, province, postal_code = "N/A", "N/A", "N/A", "N/A", "N/A"

    for i, line in enumerate(lines):
        if client_name in line and i + 1 < len(lines):
            next_line = lines[i + 1].strip()
            if re.match(r"^\d{1,5}\s[\w\s]+[,\s]*$", next_line):  # Address validation
                extracted_address = next_line
                break

    # Extract Unit
    unit_match = re.search(r"^\s*Unit\s*\d+", text, re.MULTILINE)           # Strictly match unit lines
    if unit_match:
        unit = unit_match.group(0).strip()

    # Extract City
    city_match = re.search(r"(?m)^\s*[A-Za-z\s]+(?=, ON)", text)
    if city_match:
        city = city_match.group(0)

    # Extract Province
    province_match = re.search(r"[A-Z]{2}", text)
    if province_match:
        province = province_match.group(0)

    # Extract Postal Code
    postal_match = re.search(r"[A-Z]\d[A-Z]\s*\d[A-Z]\d", text)
    if postal_match:
        postal_code = postal_match.group(0)
        # print("Postal Code:", postal_match.group(0))
    else:
        print("Postal code not matched.")

    # Extract Agreement No & Client from Header
    agreement_number, client_project = "N/A", "N/A"
    header_match = re.search(r'Re: #([A-Z0-9]+) - ([A-Za-z\s]+)\s*(Qty\s+Rate\s+Price)', text)
    if header_match:
        agreement_number = header_match.group(1).strip()
        client_project = header_match.group(2).strip()

    # Extract only the relevant table section (from "Terms: Net 30" to "HST On Sales")
    start_idx = next((i for i, line in enumerate(lines) if "Terms: Net 30" in line), None)
    end_idx = next((i for i, line in enumerate(lines) if "HST On Sales" in line), None)

    if start_idx is not None and end_idx is not None:
        table_rows = lines[start_idx:end_idx]  # Extract relevant section
    else:
        table_rows = []

        # Process Table Data
    table_data = []
    i = 0

    while i < len(table_rows):
        row = table_rows[i].strip()

        # Match rows where numbers (Qty, Rate, Price) appear at the end
        match = re.search(r'(.+?)\s+(\d*\.?\d+)\s+([\d,.]+)\s+([\d,.]+)-?', row)
        if match:
            description = match.group(1).strip()
            qty = match.group(2)
            rate = match.group(3)
            price = match.group(4)

            # Check if the next line continues the description (not a new row)
            next_line_index = i + 1
            while next_line_index < len(table_rows):
                next_line = table_rows[next_line_index].strip()
                if not re.search(r'^\d*\.?\d+\s+[\d,.]+\s+[\d,.]+-?$', next_line):  # If next line is NOT a new row
                    description += f" {next_line}"
                    next_line_index += 1
                else:
                    break

            table_data.append((description, qty, rate, price))
            i = next_line_index  # Skip processed lines
        else:
            i += 1  # Continue searching

    hst_match = re.search(r'HST On Sales\s+([\d.]+%)\s+([\d,.]+)', text)
    if hst_match:
        hst_rate = hst_match.group(1)
        hst_price = hst_match.group(2)
        table_data.append(("HST On Sales", "-", hst_rate, hst_price))  # No qty
    # Extract Tax Information
    # tax_match = re.search(r'HST On Sales\s+([\d.]+%)\s+([\d,.]+)', text)
    # tax_rate = tax_match.group(1) if tax_match else "-"
    # tax_amount = tax_match.group(2) if tax_match else "0.00"
    # table_data.append(("HST On Sales", "-", tax_rate, tax_amount))  # Tax row

    # Return Structured Data
    return {
        "invoice_number": invoice_number,
        "date": date,
        "client_name": client_name,
        "address": extracted_address if extracted_address else "No address found",
        "unit": unit,
        "city": city,
        "province": province,
        "postal_code": postal_code,
        "agreement_number": agreement_number,
        "client_project": client_project,
        "items": table_data
    }
