import pdfplumber

pdf_path = "マネージャー育成体系の整備.pdf"
output_path = "extracted_tables.txt"

def tables_to_markdown(tables):
    md_output = ""
    for page_i, table in enumerate(tables):
        if not table:
            continue
        md_output += f"\n\n### Page {page_i + 1} Tables\n"
        for row in table:
            # Noneを空文字に変換し、改行をスペースに置換
            cleaned_row = [str(cell).replace('\n', ' ') if cell is not None else "" for cell in row]
            md_output += "| " + " | ".join(cleaned_row) + " |\n"
            # ヘッダーの区切り線を追加（1行目の後）
            if row == table[0]:
                md_output += "| " + " | ".join(["---"] * len(row)) + " |\n"
    return md_output

try:
    with pdfplumber.open(pdf_path) as pdf:
        all_tables_text = ""
        for i, page in enumerate(pdf.pages):
            tables = page.extract_tables()
            if tables:
                print(f"Found {len(tables)} tables on page {i+1}")
                # 各テーブルをMarkdown形式に変換
                for table in tables:
                    md_table = ""
                    # ヘッダー行
                    if table:
                        header = table[0]
                        md_table += "| " + " | ".join([str(c).replace('\n', ' ') if c else '' for c in header]) + " |\n"
                        md_table += "| " + " | ".join(["---"] * len(header)) + " |\n"
                        # データ行
                        for row in table[1:]:
                            md_table += "| " + " | ".join([str(c).replace('\n', '<br>') if c else '' for c in row]) + " |\n"
                        all_tables_text += f"\n### Page {i+1} Table\n{md_table}\n"
            else:
                print(f"No tables found on page {i+1}")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(all_tables_text)
    
    print(f"Successfully extracted tables to {output_path}")

except Exception as e:
    print(f"Error extracting tables: {e}")

