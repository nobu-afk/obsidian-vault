import pdfplumber

pdf_path = "マネージャー育成体系の整備.pdf"
output_path = "extracted_text.txt"

try:
    with pdfplumber.open(pdf_path) as pdf:
        full_text = ""
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                full_text += text + "\n\n"
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(full_text)
    
    print(f"Successfully extracted text to {output_path}")

except Exception as e:
    print(f"Error extracting text: {e}")

