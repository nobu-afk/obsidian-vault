import re

input_path = "extracted_text.txt"
output_path = "マネージャー育成体系の整備.md"

def is_page_footer(line):
    # ページ番号 + Enablement Consulting のパターン
    return re.search(r'^\d+\s+Enablement\s+Consulting', line) or re.search(r'Enablement\s+Consulting', line)

def format_line(line):
    line = line.strip()
    if not line:
        return ""
    
    # 記号の変換
    if line.startswith('◼'):
        # 文脈によっては見出し、あるいはリスト
        # ここではリストの親要素、あるいは小見出しとして扱う
        return '\n### ' + line.replace('◼', '').strip() + '\n'
    
    if line.startswith('●') or line.startswith('・'):
        return '- ' + line.replace('●', '').replace('・', '').strip()
    
    # 特定のキーワードで始まる行を見出しにする（簡易的な判定）
    if re.match(r'^（参考）', line):
        return '\n## ' + line + '\n'
    
    return line

def process_text(text):
    lines = text.split('\n')
    formatted_lines = ["# マネージャー育成体系の整備\n"]
    
    is_new_page = True
    
    for line in lines:
        stripped = line.strip()
        
        # ページフッター/ヘッダーのスキップ
        if is_page_footer(stripped):
            is_new_page = True
            continue
            
        if not stripped:
            continue
            
        # 新しいページの最初の行はセクションタイトル（##）とする可能性が高い
        if is_new_page:
            formatted_lines.append(f"\n## {stripped}\n")
            is_new_page = False
            continue
            
        formatted_lines.append(format_line(stripped))

    return "\n".join(formatted_lines)

try:
    with open(input_path, "r", encoding="utf-8") as f:
        text = f.read()
    
    markdown_content = process_text(text)
    
    # 連続する空行を整理
    markdown_content = re.sub(r'\n{3,}', '\n\n', markdown_content)
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(markdown_content)
        
    print(f"Successfully converted to {output_path}")

except Exception as e:
    print(f"Error formatting markdown: {e}")

