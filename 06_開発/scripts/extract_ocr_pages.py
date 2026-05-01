import fitz
from PIL import Image
import io
import sys

try:
    import pytesseract
    OCR_AVAILABLE = True
except ImportError:
    print('pytesseractがインストールされていません。インストールします...')
    import subprocess
    subprocess.run([sys.executable, '-m', 'pip', 'install', 'pytesseract', 'pillow', '--quiet'])
    import pytesseract
    OCR_AVAILABLE = True

pdf_path = 'CoachDM_クロージングテンプレート.pdf'
doc = fitz.open(pdf_path)

print('OCRでテキスト抽出できないページを処理します...')
print('=' * 80)

ocr_pages = [7, 8, 9, 10, 11, 12, 21]  # 0-indexed
all_ocr_text = []

for page_num in ocr_pages:
    try:
        page = doc[page_num]
        pix = page.get_pixmap(matrix=fitz.Matrix(3, 3))  # 高解像度
        img_data = pix.tobytes('png')
        img = Image.open(io.BytesIO(img_data))
        
        # OCR実行
        text = pytesseract.image_to_string(img, lang='jpn')
        if text.strip():
            all_ocr_text.append(f'=== Page {page_num + 1} (OCR) ===\n{text}\n')
            print(f'Page {page_num + 1}: OCRでテキスト抽出成功')
        else:
            all_ocr_text.append(f'=== Page {page_num + 1} (OCR) ===\n[OCRでもテキスト抽出不可]\n')
            print(f'Page {page_num + 1}: OCRでもテキスト抽出不可')
    except Exception as e:
        print(f'Page {page_num + 1}: OCRエラー - {e}')
        all_ocr_text.append(f'=== Page {page_num + 1} (OCR) ===\n[OCRエラー: {e}]\n')

full_ocr_text = '\n'.join(all_ocr_text)

# キーワード検索
keywords = ['ファネルクロージング', 'ファネルクローザー', 'マインドセット', 'セールスマン', '説得', '切り上げる', '抜け出したい', '適切な人', 'あなたは', '課題を解決']
print('\nキーワード検索結果 (OCR抽出):')
found_any = False
for kw in keywords:
    if kw in full_ocr_text:
        print(f'  ✓ {kw} が見つかりました')
        found_any = True
        idx = full_ocr_text.find(kw)
        start = max(0, idx - 150)
        end = min(len(full_ocr_text), idx + 300)
        context = full_ocr_text[start:end].replace('\n', ' ')
        print(f'    前後: ...{context}...')
        print()

if not found_any:
    print('  検索キーワードは見つかりませんでした')

# ファイルに保存
with open('CoachDM_クロージングテンプレート_OCR抽出.txt', 'w', encoding='utf-8') as f:
    f.write(full_ocr_text)

print(f'\nOCR抽出結果を CoachDM_クロージングテンプレート_OCR抽出.txt に保存しました')
doc.close()
