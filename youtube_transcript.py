#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YouTube動画の文字起こしを取得するスクリプト
youtube-transcript-apiを使用して字幕データを取得します
"""

from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter
import sys
import re
from urllib.parse import urlparse, parse_qs

def extract_video_id(url):
    """YouTubeのURLから動画IDを抽出"""
    # URLから動画IDを抽出
    parsed_url = urlparse(url)
    
    # 通常のURL形式: https://www.youtube.com/watch?v=VIDEO_ID
    if parsed_url.hostname in ['www.youtube.com', 'youtube.com']:
        query_params = parse_qs(parsed_url.query)
        if 'v' in query_params:
            return query_params['v'][0]
    
    # 短縮URL形式: https://youtu.be/VIDEO_ID
    if parsed_url.hostname == 'youtu.be':
        return parsed_url.path[1:]
    
    # URLが動画IDそのものの場合
    if len(url) == 11 and re.match(r'^[a-zA-Z0-9_-]{11}$', url):
        return url
    
    return None

def get_transcript(video_id, languages=['ja', 'en']):
    """
    YouTube動画の文字起こしを取得
    
    Args:
        video_id: YouTube動画ID
        languages: 優先する言語のリスト（デフォルト: 日本語、英語）
    
    Returns:
        str: 文字起こしテキスト
    """
    try:
        # YouTubeTranscriptApiのインスタンスを作成
        yt_api = YouTubeTranscriptApi()
        
        # 字幕データを取得
        transcript_list = yt_api.list(video_id)
        
        # 利用可能な字幕を確認
        print(f"📋 利用可能な字幕:")
        available_transcripts = []
        for transcript in transcript_list:
            lang = transcript.language
            lang_code = transcript.language_code
            is_generated = transcript.is_generated
            
            status = "自動生成" if is_generated else "手動"
            print(f"  - {lang} ({lang_code}) [{status}]")
            available_transcripts.append({
                'code': lang_code,
                'name': lang,
                'is_generated': is_generated,
                'transcript': transcript
            })
        
        # 優先言語で字幕を取得
        transcript = None
        for lang_code in languages:
            for avail in available_transcripts:
                if avail['code'] == lang_code:
                    transcript = avail['transcript']
                    print(f"\n✅ 使用する字幕: {avail['name']} ({lang_code})")
                    break
            if transcript:
                break
        
        # 優先言語が見つからない場合、最初の利用可能な字幕を使用
        if not transcript:
            print(f"\n⚠️  優先言語が見つかりませんでした。最初の利用可能な字幕を使用します。")
            transcript = available_transcripts[0]['transcript']
        
        # 字幕データを取得
        transcript_data = transcript.fetch()
        
        # テキストフォーマッターを使用して整形
        formatter = TextFormatter()
        text = formatter.format_transcript(transcript_data)
        
        return text, transcript_data
        
    except Exception as e:
        error_msg = str(e)
        if "No transcripts were found" in error_msg:
            print(f"❌ エラー: この動画には字幕がありません")
            print(f"   動画の投稿者が字幕を有効にしていない可能性があります。")
        elif "TranscriptsDisabled" in error_msg:
            print(f"❌ エラー: この動画では字幕が無効になっています")
        elif "VideoUnavailable" in error_msg:
            print(f"❌ エラー: 動画が見つかりませんでした")
        else:
            print(f"❌ エラー: {error_msg}")
        
        return None, None

def format_transcript_markdown(transcript_data, video_id, video_url):
    """文字起こしをMarkdown形式に整形"""
    markdown = f"""# YouTube動画の文字起こし

**動画URL**: {video_url}
**動画ID**: {video_id}

---

## 文字起こし

"""
    
    # タイムスタンプ付きで整形
    for entry in transcript_data:
        # オブジェクトの属性としてアクセス
        start_time = entry.start
        duration = entry.duration
        text = entry.text
        
        # 時間を分:秒形式に変換
        minutes = int(start_time // 60)
        seconds = int(start_time % 60)
        timestamp = f"{minutes:02d}:{seconds:02d}"
        
        markdown += f"**[{timestamp}]** {text}\n\n"
    
    return markdown

def main():
    if len(sys.argv) < 2:
        print("使用方法:")
        print("  python youtube_transcript.py <YouTube_URLまたは動画ID>")
        print("\n例:")
        print("  python youtube_transcript.py https://www.youtube.com/watch?v=XZWoYL1asRE")
        print("  python youtube_transcript.py XZWoYL1asRE")
        sys.exit(1)
    
    url_or_id = sys.argv[1]
    
    # 動画IDを抽出
    video_id = extract_video_id(url_or_id)
    
    if not video_id:
        print(f"❌ エラー: 有効なYouTube URLまたは動画IDを指定してください")
        print(f"   入力値: {url_or_id}")
        sys.exit(1)
    
    print(f"🎬 動画ID: {video_id}")
    print(f"📥 字幕を取得中...\n")
    
    # 字幕を取得
    text, transcript_data = get_transcript(video_id)
    
    if not text:
        print("\n❌ 文字起こしの取得に失敗しました")
        sys.exit(1)
    
    # 出力ファイル名を生成
    output_file = f"youtube_transcript_{video_id}.md"
    
    # Markdown形式で保存
    video_url = url_or_id if url_or_id.startswith('http') else f"https://www.youtube.com/watch?v={video_id}"
    markdown_content = format_transcript_markdown(transcript_data, video_id, video_url)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(markdown_content)
    
    print(f"\n✅ 文字起こしを取得しました！")
    print(f"📄 保存先: {output_file}")
    print(f"📊 文字数: {len(text)}文字")
    print(f"📝 行数: {len(transcript_data)}行")

if __name__ == "__main__":
    main()

