from pdf2image import convert_from_path
import pytesseract
import re
import cv2
import numpy as np
import os

# ← adjust these to your installation paths
POPPLER_PATH = r"C:\Users\SamsonC\poppler\poppler-24.08.0\Library\bin"
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def extract_invoice_ocr(pdf_path, debug_dir="debug"):
    os.makedirs(debug_dir, exist_ok=True)

    # 1. Convert PDF → images
    try:
        pages = convert_from_path(pdf_path, dpi=300, poppler_path=POPPLER_PATH)
    except Exception as e:
        print(f"[ERROR] PDF→images conversion: {e}")
        return {}

    # 2. OCR each page
    full_text = ""
    for i, pil in enumerate(pages, start=1):
        gray = cv2.cvtColor(np.array(pil), cv2.COLOR_RGB2GRAY)
        _, bw = cv2.threshold(gray, 180, 255, cv2.THRESH_BINARY_INV)
        clean = cv2.medianBlur(bw, 3)
        cv2.imwrite(os.path.join(debug_dir, f"page_{i:02d}.png"), clean)
        full_text += pytesseract.image_to_string(clean, lang="eng") + "\n"

    # 3. Split into lines for block parsing
    lines = [l.strip() for l in full_text.splitlines()]

    # 4. Date & Invoice #
    m = re.search(r'(\d{4}-\d{2}-\d{2})\s+(\d+)', full_text)
    date, invoice_no = (m.group(1), m.group(2)) if m else (None, None)

    # 5. “Invoice To” block
    client_name = address = unit = city = province = postal = None
    idx = next((i for i, l in enumerate(lines) if l.lower() == "invoice to"), None)
    if idx is not None:
        # client name
        j = idx + 1
        while j < len(lines) and not lines[j]: j += 1
        if j < len(lines):
            client_name = lines[j]; j += 1
        # street address + unit
        while j < len(lines) and not lines[j]: j += 1
        if j < len(lines):
            addr_line = lines[j]; j += 1
            address = addr_line.split(',', 1)[0].strip()
            um = re.search(r'(?i)(Suite|Unit)\s*\d+', addr_line)
            unit = um.group(0) if um else None
        # city, province
        while j < len(lines) and not lines[j]: j += 1
        if j < len(lines):
            parts = [p.strip() for p in lines[j].split(',', 1)]
            city = parts[0]
            province = parts[1] if len(parts) > 1 else None
            j += 1
        # postal code
        while j < len(lines) and not lines[j]: j += 1
        if j < len(lines):
            postal = lines[j]

    # fallback postal if still None
    if not postal:
        fm = re.search(r'([A-Z]\d[A-Z]\s*\d[A-Z]\d)', full_text)
        postal = fm.group(1) if fm else None

    # 6. Agreement No & Client Project
    m = re.search(r'#([A-Z0-9]+)\s*-\s*([^|\n]+)', full_text)
    agreement_number = m.group(1).strip() if m else None
    client_project   = m.group(2).strip() if m else None

    # 7. Line-item: rate, amount & qty
    m = re.search(
        r'([\d,]+\.\d{2})\s+([\d,]+\.\d{2}).*?\(([\d.]+)\s*hours\)',
        full_text, re.S
    )
    rate, amount, qty = (m.group(1), m.group(2), m.group(3)) if m else (None, None, None)

    # 8. GST/HST & Total
    gm = re.search(r'GST/HST.*?\$?([\d,]+\.\d{2})', full_text)
    tm = re.search(r'Total\s*\$?([\d,]+\.\d{2})', full_text)
    gst   = gm.group(1) if gm else None
    total = tm.group(1) if tm else None

    return {
        "date":               date,
        "invoice_number":     invoice_no,
        "client_name":        client_name,
        "address":            address,
        "unit":               unit,
        "city":               city,
        "province":           province,
        "postal_code":        postal,
        "agreement_number":   agreement_number,
        "client_project":     client_project,
        "rate":               rate,
        "amount":             amount,
        "qty":                qty,
        "gst":                gst,
        "total":              total,
    }

if __name__ == "__main__":
    result = extract_invoice_ocr("7020.pdf")
    print("Extracted data:", result)
