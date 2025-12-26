#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
2022年以降 TerminalHill記事 完全再取得・分割スクリプト
"""

import re
import os
import time
import requests
from datetime import datetime
from bs4 import BeautifulSoup
import random

class Post2022FullRescraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
        self.articles = []
        self.start_part_num = 16
        self.max_chars = 500_000

    def get_correct_encoding_content(self, url):
        """正しいエンコーディングで記事内容を取得"""
        encodings = ['euc-jp', 'utf-8', 'shift_jis', 'iso-2022-jp']
        
        for encoding in encodings:
            try:
                response = self.session.get(url, timeout=30)
                response.raise_for_status()
                
                if encoding == 'utf-8':
                    text = response.text
                else:
                    text = response.content.decode(encoding, errors='ignore')
                
                if self.has_valid_japanese(text):
                    return text, encoding
                    
            except Exception:
                continue
        
        return None, None

    def has_valid_japanese(self, text):
        """日本語妥当性チェック"""
        if not text:
            return False
        
        japanese_chars = re.findall(r'[あ-んア-ンー一-龯]', text)
        japanese_count = len(japanese_chars)
        
        garbled_patterns = ['�', '縺', '繝', '繧']
        has_garbled = any(pattern in text for pattern in garbled_patterns)
        
        return japanese_count > 50 and not has_garbled

    def extract_article_data(self, url, html_content):
        """記事データを抽出"""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # タイトル抽出
        title = ""
        title_selectors = ['h1.title', '.entry-title', 'h1', 'title']
        for selector in title_selectors:
            element = soup.select_one(selector)
            if element:
                title_text = element.get_text(strip=True)
                if self.has_valid_japanese(title_text) or len(title_text) > 10:
                    title = title_text
                    break
        
        # 日付抽出
        date = ""
        date_patterns = [
            r'(\d{4})\.(\d{2})\.(\d{2})',
            r'(\d{4})-(\d{2})-(\d{2})',
            r'(\d{4})/(\d{2})/(\d{2})'
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, html_content)
            if match:
                y, m, d = match.groups()
                date = f"{y}-{m}-{d}"
                break
        
        # 本文抽出
        content = ""
        content_selectors = ['.entry', '.post-content', '.content', 'article']
        for selector in content_selectors:
            element = soup.select_one(selector)
            if element:
                # 不要な要素を削除
                for tag in element.find_all(['script', 'style', 'nav', 'footer', 'aside']):
                    tag.decompose()
                
                content_text = element.get_text(separator='\n', strip=True)
                if len(content_text) > 200:
                    content = content_text
                    break
        
        return {
            'url': url,
            'title': title,
            'date': date,
            'content': content,
            'char_count': len(content)
        }

    def scrape_post2022_articles(self):
        """2022年以降の記事を再取得"""
        print("🔄 2022年以降記事の完全再取得開始")
        
        # eid範囲を設定（テスト結果から2022年以降は5700以降）
        start_eid = 5637  # 2021-11-30 from previous data
        end_eid = 7000    # 推定上限
        
        success_count = 0
        processed_count = 0
        
        for eid in range(start_eid, end_eid + 1):
            url = f"https://terminalhill.jugem.jp/?eid={eid}"
            processed_count += 1
            
            try:
                print(f"[{processed_count}/{end_eid-start_eid+1}] EID:{eid}")
                
                html_content, encoding = self.get_correct_encoding_content(url)
                if not html_content:
                    print(f"  ❌ 取得失敗")
                    continue
                
                article_data = self.extract_article_data(url, html_content)
                
                # 日付フィルタ（2022年以降のみ）
                if article_data['date']:
                    try:
                        year = int(article_data['date'][:4])
                        if year < 2022:
                            print(f"  ⏭️ 2022年未満: {article_data['date']}")
                            continue
                    except:
                        pass
                else:
                    print(f"  ❌ 日付不明")
                    continue
                
                if article_data['content'] and len(article_data['content']) > 200:
                    article_data['encoding'] = encoding
                    self.articles.append(article_data)
                    success_count += 1
                    print(f"  ✅ 成功: {article_data['date']} - {article_data['title'][:30]}... ({article_data['char_count']}文字)")
                else:
                    print(f"  ❌ コンテンツ不足")
                
                # レート制限
                time.sleep(random.uniform(0.3, 0.8))
                
            except Exception as e:
                print(f"  ❌ エラー: {e}")
                continue
            
            # 進捗表示
            if processed_count % 50 == 0:
                print(f"📊 進捗: {processed_count}/{end_eid-start_eid+1} 処理済み, {success_count}記事取得")
        
        print(f"\n✅ 再取得完了: {success_count}記事 (処理: {processed_count}URL)")
        return success_count > 0

    def split_and_save_articles(self):
        """記事を500K文字以内で分割保存"""
        if not self.articles:
            print("❌ 分割対象記事がありません")
            return
        
        # 日付順でソート
        self.articles.sort(key=lambda x: x['date'])
        
        print(f"🔄 {len(self.articles)}記事を500,000文字以内で分割開始")
        print(f"📅 期間: {self.articles[0]['date']} 〜 {self.articles[-1]['date']}")
        
        part_num = self.start_part_num
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        header_tpl = """TerminalHill記事データセット - Part {part:02d}
分割日時: {now}
最大文字数: {max:,}文字 (2022年以降記事 - 正しいエンコーディング)
期間: {start_date} 〜 {end_date}
================================================================================\n\n"""
        
        current_articles = []
        buf_chars = 0
        stats = []
        
        for art in self.articles:
            article_text = f"""URL: {art['url']}
タイトル: {art['title']}
日付: {art['date']}
エンコーディング: {art['encoding']}
文字数: {art['char_count']}
================================================================================

{art['content']}

"""
            art_chars = len(article_text)
            
            # ヘッダー込みで500K以内かチェック
            header_chars = 200  # ヘッダーの概算文字数
            
            if buf_chars + art_chars + header_chars <= self.max_chars:
                current_articles.append(art)
                buf_chars += art_chars
            else:
                # 現在ファイル保存
                if current_articles:
                    self.save_file(current_articles, part_num, timestamp, stats)
                    part_num += 1
                
                # 新ファイル開始
                current_articles = [art]
                buf_chars = art_chars
        
        # 最終ファイル保存
        if current_articles:
            self.save_file(current_articles, part_num, timestamp, stats)
        
        # サマリー
        total_articles = sum(s['articles'] for s in stats)
        total_chars = sum(s['chars'] for s in stats)
        print(f"\n=== 2022年以降記事分割完了 ===")
        print(f"総ファイル数: {len(stats)}")
        print(f"総記事数: {total_articles:,}")
        print(f"総文字数: {total_chars:,}")
        
        for s in stats:
            size_mb = round(s['chars'] / 1024 / 1024, 2)
            print(f"  {s['filename']}: {s['articles']}記事, {s['chars']:,}文字 ({size_mb}MB)")

    def save_file(self, articles, part_num, timestamp, stats):
        """ファイル保存"""
        start_date = articles[0]['date']
        end_date = articles[-1]['date']
        
        header = f"""TerminalHill記事データセット - Part {part_num:02d}
分割日時: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}
最大文字数: {self.max_chars:,}文字 (2022年以降記事 - 正しいエンコーディング)
期間: {start_date} 〜 {end_date}
記事数: {len(articles)}
================================================================================\n\n"""
        
        content = header
        for i, art in enumerate(articles, 1):
            article_text = f"""記事 {i}/{len(articles)}: {art['title']}
URL: {art['url']}
日付: {art['date']}
エンコーディング: {art['encoding']}
文字数: {art['char_count']}
================================================================================

{art['content']}

"""
            content += article_text + "\n"
        
        filename = f"terminalhill_500K_part{part_num:02d}_{timestamp}.txt"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        
        stats.append({
            'filename': filename, 
            'articles': len(articles), 
            'chars': len(content),
            'start_date': start_date,
            'end_date': end_date
        })
        print(f"✅ {filename}: {len(articles)}記事, {len(content):,}文字 ({start_date}〜{end_date})")

if __name__ == "__main__":
    scraper = Post2022FullRescraper()
    
    if scraper.scrape_post2022_articles():
        scraper.split_and_save_articles()
    else:
        print("❌ 記事取得に失敗しました") 