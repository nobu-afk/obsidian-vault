import re

md_path = "マネージャー育成体系の整備.md"
tables_path = "extracted_tables.txt"
output_path = "マネージャー育成体系の整備_v2.md"

def load_tables(path):
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    
    tables = {}
    current_page = None
    current_table = []
    
    for line in content.split('\n'):
        if line.strip().startswith("### Page"):
            if current_page and current_table:
                tables[current_page] = "\n".join(current_table)
            
            match = re.search(r'Page (\d+) Table', line)
            if match:
                current_page = int(match.group(1))
                current_table = []
        else:
            if current_page is not None:
                current_table.append(line)
                
    if current_page and current_table:
        tables[current_page] = "\n".join(current_table)
        
    return tables

def replace_section(content, header_regex, new_content):
    pattern = re.compile(rf'({header_regex})(.*?)(?=\n## |\Z)', re.DOTALL)
    match = pattern.search(content)
    if match:
        # ヘッダーは残し、その後の内容を置換
        return content.replace(match.group(0), f"{match.group(1)}\n{new_content}\n")
    return content

try:
    tables = load_tables(tables_path)
    
    with open(md_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # 不要な行の削除
    content = re.sub(r'^## 株式会社イネーブルメント・コンサルティング\n', '', content, flags=re.MULTILINE)
    content = re.sub(r'^\s*Enablement Consulting\s*$', '', content, flags=re.MULTILINE)
    
    # テーブルの差し替え
    
    # Page 8: マイクロラーニングコンテンツ事例
    if 8 in tables:
        content = replace_section(content, r'## GLOBIS学び放題 マイクロラーニングコンテンツ事例', tables[8])

    # Page 9: 導入研修事例
    if 9 in tables:
        content = replace_section(content, r'## インプット \| GLOBIS学び放題 導入研修事例', tables[9])
        
    # Page 15: マネジメントコンピテンシー詳細
    if 15 in tables:
        content = replace_section(content, r'## （参考）マネジメントコンピテンシー詳細', tables[15])

    # Page 12: 発生する壁の整理 (M3, M2, M1)
    # テキスト抽出では崩れていたのでテーブルを採用
    if 12 in tables:
        # Page 12のテーブルは一部空行や不要な行があるのでクリーニング
        table_content = tables[12]
        # 「発生する壁の整理」セクションの一部として挿入したいが、セクション名がPage 10にある
        # Page 12の内容は等級定義に近いので、「人事制度起点の研修設計の考え方」の後ろあたり、あるいは独立させる
        # ここでは元のテキストの「発生する壁の整理」セクションを丸ごとこのテーブルで置き換えてみる（実験的）
        
        # まずPage 10の「発生する壁の整理」セクションを探す
        content = replace_section(content, r'## 発生する壁の整理', tables[12])

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)
        
    print(f"Successfully merged tables to {output_path}")

except Exception as e:
    print(f"Error merging tables: {e}")

