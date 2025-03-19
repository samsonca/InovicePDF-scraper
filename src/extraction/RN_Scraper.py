import pdfplumber
import re

def extract_rn_invoice_data(pdf_path):
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

    # Extract Address Details (Address, Unit, City, Province, Postal Code)
    extracted_address, unit, building, city, province, postal_code = "N/A", "N/A", "N/A", "N/A", "N/A", "N/A"
    
    # Locate the "BILL TO" block to extract address details
    bill_to_idx = next((i for i, line in enumerate(lines) if "BILL TO" in line.upper()), None)
    if bill_to_idx is not None:
        # Assumed layout based on your invoice:
        # bill_to_idx+1: Client Name
        # bill_to_idx+2: Full street address (e.g., "331 Cityview Blvd., Suite 201")
        # bill_to_idx+3: "City, Province" line
        # bill_to_idx+4: Postal Code
        if bill_to_idx + 2 < len(lines):
            full_address_line = lines[bill_to_idx + 2].strip()  # e.g., "331 Cityview Blvd., Suite 201"
            # Extract the unit (e.g., "Suite 201") from the full address line
            unit_match = re.search(r"(?i)(Suite|Unit)\s*\d+", full_address_line)
            if unit_match:
                unit = unit_match.group(0).strip()
            # Extract the street address (portion before the comma)
            extracted_address = full_address_line.split(',')[0].strip()
        if bill_to_idx + 3 < len(lines):
            city_prov_line = lines[bill_to_idx + 3].strip()
            if ',' in city_prov_line:
                parts = city_prov_line.split(',')
                city = parts[0].strip()
                province = parts[1].strip()
            else:
                city = city_prov_line
        if bill_to_idx + 4 < len(lines):
            postal_code = lines[bill_to_idx + 4].strip()

    # Extract Building (if available)
    building_match = re.search(r"(?i)(?:Bldg\.?|Building)\s*[A-Za-z0-9]+", text)
    if building_match:
        building = building_match.group(0).strip()

    # Extract City (alternative method if not found above)
    if city == "N/A":
        city_match = re.search(r"(?m)^\s*[A-Za-z\s]+(?=,\s*[Oo][Nn])", text)
        if city_match:
            city = city_match.group(0)
        else:
            for line in lines:
                if re.search(r"[A-Z]\d[A-Z]\s*\d[A-Z]\d", line) and "Canada" in line:
                    parts = line.split(',')
                    if len(parts) >= 2:
                        city = parts[0].strip()
                    break

    # Extract Province (from a matching pattern)
    province_match = re.search(
        r",\s*([A-Za-z]+(?:\s+[A-Za-z]+)*)(?=\s+(?:Canada|[A-Z]\d[A-Z]\s*\d[A-Z]\d|Agreement No:)|\s*$)",
        text,
        re.IGNORECASE
    )
    if province_match:
        province_extracted = province_match.group(1).strip()
        province_extracted_upper = province_extracted.upper()
        if province_extracted_upper in ("ONTARIO", "ONTARIO CANADA"):
            province = "ON"
        else:
            province = province_extracted_upper

    # Extract Postal Code
    postal_match = re.search(r"[A-Z]\d[A-Z]\s*\d[A-Z]\d", text)
    if postal_match:
        postal_code = postal_match.group(0)
    else:
        print("Postal code not matched.")

    # Extract Agreement No & Client Project from Header (using the RE: line)
    agreement_number, client_project = "N/A", "N/A"
    header_match = re.search(
        r'(?:Re:\s*)?#([A-Z0-9-]+)\s*-\s*([A-Za-z0-9\s-]+?)(?=\s+Qty\s+Rate\s+Price|\s*$)',
        text
    )
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
                if not re.search(r'^\d*\.?\d+\s+[\d,.]+\s+[\d,.]+-?$', next_line):
                    description += f" {next_line}"
                    next_line_index += 1
                else:
                    break
            table_data.append((description, qty, rate, price))
            i = next_line_index  # Skip processed lines
        else:
            i += 1

    hst_match = re.search(r'HST On Sales\s+([\d.]+%)\s+([\d,.]+)', text)
    if hst_match:
        hst_rate = hst_match.group(1)
        hst_price = hst_match.group(2)
        table_data.append(("HST On Sales", "-", hst_rate, hst_price))

    # Prepare the return data
    data = {
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
    
    # Print the extracted data for debugging purposes
    print("Extracted data:", data)
    
    return data
