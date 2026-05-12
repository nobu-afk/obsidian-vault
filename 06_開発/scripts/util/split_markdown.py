import re
import os

input_path = "マネージャー育成体系の整備_v2.md"
output_dir = "マネージャー育成体系の整備_Markdown"

if not os.path.exists(output_dir):
    os.makedirs(output_dir)

def split_markdown(path):
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    matches = list(re.finditer(r'\n## (.*?)\n', content))
    
    # 0番目のファイル（最初の見出しまで）
    first_end = matches[0].start() if matches else len(content)
    with open(os.path.join(output_dir, "00_表紙・はじめに.md"), "w", encoding="utf-8") as f:
        f.write(content[:first_end].strip())
        
    for i, match in enumerate(matches):
        start = match.start()
        end = matches[i+1].start() if i + 1 < len(matches) else len(content)
        
        section_content = content[start:end].strip()
        title_line = match.group(1).strip()
        
        # ファイル名決定ロジック
        if "マネージャーの発展段階" == title_line:
            filename = "01_マネージャーの発展段階.md"
        elif "マネージャーの発展段階および必要な支援" in title_line:
            filename = "02_マネージャーの発展段階および必要な支援.md"
        elif "運用イメージ" in title_line:
            filename = "03_マネージャーの学習プロセスの運用イメージ.md"
        elif "行動変容につながる" in title_line:
            filename = "04_行動変容につながる学習プロセス.md"
        elif "サンドイッチ型" in title_line:
            filename = "05_サンドイッチ型のマネジメント研修.md"
        elif "学習プロセスの整理" in title_line:
            filename = "06_マネージャーの学習プロセスの整理.md"
        elif "マイクロラーニングコンテンツ事例" in title_line:
            filename = "07_GLOBIS学び放題_マイクロラーニングコンテンツ事例.md"
        elif "導入研修事例" in title_line:
            filename = "08_GLOBIS学び放題_導入研修事例.md"
        elif "研修企画の考え方" == title_line:
             filename = "09_研修企画の考え方.md"
        elif "人事制度起点の" in title_line:
             filename = "10_人事制度起点の研修設計の考え方.md"
        elif "発生する壁の整理" in title_line:
             filename = "11_発生する壁の整理.md"
        elif "寺子屋" in title_line:
             filename = "12_参考_寺子屋によるサポート.md"
        elif "メンバーケア" in title_line:
             filename = "13_参考_メンバーケアの仕組み.md"
        elif "マネジメントコンピテンシー詳細" in title_line:
             filename = "14_参考_マネジメントコンピテンシー詳細.md"
        elif "経営幹部職のコンピテンシー" in title_line:
             filename = "15_参考_経営幹部職のコンピテンシー.md"
        elif title_line.startswith("http"):
             filename = "16_参考リンク.md"
        else:
             # フォールバック
             clean_title = re.sub(r'[\\/*?:"<>|]', "", title_line)[:20]
             filename = f"99_{clean_title}.md"
        
        with open(os.path.join(output_dir, filename), "w", encoding="utf-8") as f:
            f.write(section_content)
            print(f"Created {filename}")

try:
    split_markdown(input_path)
    print(f"Successfully split markdown files to {output_dir}/")
except Exception as e:
    print(f"Error splitting markdown: {e}")
