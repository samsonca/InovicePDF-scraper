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
    extracted_address, unit, building,city, province, postal_code = "N/A", "N/A", "N/A", "N/A", "N/A", "N/A"

    for i, line in enumerate(lines):
        if "Client:" in line:
            if i + 1 < len(lines):
                next_line = lines[i + 1].strip()
                # Take only street address before the comma
                extracted_address = next_line.split(',')[0].strip()
            break
    # print(f"Addres: {extracted_address if extracted_address else 'No address found'}")

    # Extract Unit
    unit_match = re.search(r"(?i)(?:Unit|Suite)\s*\d+", text, re.MULTILINE)
    if unit_match:
        unit = unit_match.group(0).strip()

    # Extract Building
    building_match = re.search(r"(?i)(?:Bldg\.?|Building)\s*[A-Za-z0-9]+", text)
    if building_match:
        building = building_match.group(0).strip()
        # print("Building:", building_field)
    # else:
    #     print("Building not found.")

    # Extract City
    city_match = re.search(r"(?m)^\s*[A-Za-z\s]+(?=,\s*[Oo][Nn])", text)
    if city_match:
        city = city_match.group(0)
    else:
        # print("City not matched.")
        if not re.search(r"(?m)^[A-Za-z\s]+(?=, ON)", text):
            for line in lines:
                # Check if the line contains a postal code pattern (Canadian format) and "Canada"
                if re.search(r"[A-Z]\d[A-Z]\s*\d[A-Z]\d", line) and "Canada" in line:
                    parts = line.split(',')
                    if len(parts) >= 2:
                        city_test = parts[0].strip()
                    break
                    

    # Extract Province
    province_match = re.search(r"(?i)[A-Za-z]{2}", text)
    if province_match:
        if province_match.group(0).upper() == "HS":
            if re.search(r"[A-Z]\d[A-Z]\s*\d[A-Z]\d", line) and "Canada" in line:
                parts = line.split(',')
                if len(parts) >= 2:
                    province_tokens = parts[1].strip().split()
                    if province_tokens:
                        province = province_tokens[0].strip()
        else:
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
    header_match = re.search(r'(?:Re:\s*)?#([A-Z0-9-]+)\s*-\s*([A-Za-z\s]+)\s*(Qty\s+Rate\s+Price)', text)
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
        "building": building,
        "city": city,
        "province": province,
        "postal_code": postal_code,
        "agreement_number": agreement_number,
        "client_project": client_project,
        "items": table_data
    }
