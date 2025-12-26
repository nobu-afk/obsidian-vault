import re

def count_japanese_chars(text):
    # Remove markdown syntax to get a rough content count
    # This is a simple approximation
    text = re.sub(r'#+ ', '', text) # Headings
    text = re.sub(r'\*\*', '', text) # Bold
    text = re.sub(r'\[.*?\]\(.*?\)', '', text) # Links
    text = re.sub(r'> ', '', text) # Blockquotes
    
    # Remove whitespace
    text = text.replace(' ', '').replace('\n', '').replace('\t', '').replace('\u3000', '')
    
    return len(text)

file_path = '採用ダッシュボード_Note記事.md'
try:
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    count = count_japanese_chars(content)
    print(f"Current character count: {count}")
    
except FileNotFoundError:
    print(f"File not found: {file_path}")
