#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
サイト構造分析ツール
ブログサイトの構造を調査し、記事抽出のための情報を取得
"""

import requests
from bs4 import BeautifulSoup
import sys
from urllib.parse import urljoin, urlparse

def analyze_site(url):
    """サイト構造を分析する"""
    print(f"サイト構造分析開始: {url}")
    print("=" * 60)
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        response.encoding = 'utf-8'
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        print("1. ページタイトル:")
        title = soup.find('title')
        if title:
            print(f"   {title.get_text().strip()}")
        
        print("\n2. 主要な見出し構造:")
        for i, tag in enumerate(['h1', 'h2', 'h3'], 1):
            headers = soup.find_all(tag)
            print(f"   {tag.upper()}: {len(headers)}個")
            for j, header in enumerate(headers[:3]):  # 最初の3つを表示
                text = header.get_text().strip()[:50]
                print(f"     - {text}...")
        
        print("\n3. リンク分析:")
        all_links = soup.find_all('a', href=True)
        print(f"   総リンク数: {len(all_links)}")
        
        # ドメイン内リンクを抽出
        base_domain = urlparse(url).netloc
        internal_links = []
        for link in all_links:
            href = link['href']
            full_url = urljoin(url, href)
            link_domain = urlparse(full_url).netloc
            if link_domain == base_domain:
                internal_links.append((full_url, link.get_text().strip()[:30]))
        
        print(f"   ドメイン内リンク: {len(internal_links)}個")
        
        # リンクパターンを分析
        print("\n4. リンクパターン分析:")
        patterns = {}
        for link_url, link_text in internal_links[:20]:  # 最初の20個
            path = urlparse(link_url).path
            if '?' in link_url:
                query = urlparse(link_url).query
                pattern = f"?{query.split('=')[0]}=" if '=' in query else f"?{query}"
            else:
                pattern = path
            
            if pattern not in patterns:
                patterns[pattern] = []
            patterns[pattern].append((link_url, link_text))
        
        for pattern, links in list(patterns.items())[:10]:
            print(f"   パターン '{pattern}': {len(links)}個")
            for link_url, link_text in links[:2]:
                print(f"     - {link_text} ({link_url})")
        
        print("\n5. 可能性のある記事リンク:")
        article_candidates = []
        
        # 一般的な記事パターンをチェック
        article_patterns = [
            ('?eid=', 'エントリーID'),
            ('/entry/', 'エントリーパス'),
            ('/post/', 'ポストパス'),
            ('/archives/', 'アーカイブ'),
            ('/20', '年付きパス'),
        ]
        
        for pattern, description in article_patterns:
            matching_links = [link for link in internal_links if pattern in link[0]]
            if matching_links:
                print(f"   {description} ({pattern}): {len(matching_links)}個")
                article_candidates.extend(matching_links[:5])
                for link_url, link_text in matching_links[:3]:
                    print(f"     - {link_text} ({link_url})")
        
        print("\n6. 特殊なHTML構造:")
        
        # 記事コンテナの候補
        container_selectors = [
            '.entry', '.post', '.article', 'article',
            '.content', '.main', '#main', '.blog-entry'
        ]
        
        for selector in container_selectors:
            elements = soup.select(selector)
            if elements:
                print(f"   {selector}: {len(elements)}個発見")
        
        # 日付情報の候補
        date_selectors = [
            '.date', '.entry-date', '.post-date', 'time',
            '.published', '.datetime'
        ]
        
        print("\n7. 日付情報:")
        for selector in date_selectors:
            elements = soup.select(selector)
            if elements:
                print(f"   {selector}: {len(elements)}個")
                for elem in elements[:2]:
                    print(f"     - {elem.get_text().strip()}")
        
        print("\n8. 推奨される抽出戦略:")
        if article_candidates:
            print("   ✓ 記事リンクが検出されました")
            print("   推奨アプローチ:")
            print("   1. 検出されたパターンでリンクを抽出")
            print("   2. 各記事ページから本文を抽出")
        else:
            print("   ⚠ 明確な記事リンクが検出されませんでした")
            print("   推奨アプローチ:")
            print("   1. アーカイブページを探索")
            print("   2. ページネーション（次のページ）を確認")
            print("   3. サイトマップを確認")
        
        return article_candidates
        
    except Exception as e:
        print(f"エラー: {e}")
        return []

def main():
    if len(sys.argv) != 2:
        print("使用方法: python site_analyzer.py <URL>")
        sys.exit(1)
    
    url = sys.argv[1]
    analyze_site(url)

if __name__ == "__main__":
    main() 