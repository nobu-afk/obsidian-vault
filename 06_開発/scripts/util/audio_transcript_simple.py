#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
音声ファイルの文字起こしスクリプト（OpenAI Whisper API使用）
ffmpeg不要で動作します
"""

import sys
import os
from pathlib import Path

def transcribe_with_openai_whisper_api(audio_path, api_key=None):
    """
    OpenAI Whisper APIを使用して文字起こし
    ffmpeg不要で動作します
    """
    try:
        from openai import OpenAI
        
        if not api_key:
            api_key = os.environ.get("OPENAI_API_KEY")
            if not api_key:
                print("❌ エラー: OpenAI APIキーが必要です")
                print("\n設定方法:")
                print("1. 環境変数に設定:")
                print("   export OPENAI_API_KEY='your-api-key'")
                print("2. または、引数で指定:")
                print("   python audio_transcript_simple.py <ファイル> --api-key YOUR_KEY")
                print("\nAPIキーの取得方法:")
                print("  https://platform.openai.com/api-keys で取得できます")
                return None
        
        client = OpenAI(api_key=api_key)
        
        print(f"🔄 OpenAI Whisper APIで文字起こし中...")
        print(f"   ファイル: {os.path.basename(audio_path)}")
        
        with open(audio_path, 'rb') as audio_file:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                language="ja",
                response_format="verbose_json"  # セグメント情報も取得
            )
        
        # セグメント情報を整形
        segments = []
        if hasattr(transcript, 'segments'):
            for seg in transcript.segments:
                segments.append({
                    "start": seg.start,
                    "end": seg.end,
                    "text": seg.text
                })
        
        return {
            "text": transcript.text,
            "segments": segments
        }
        
    except ImportError:
        print("❌ エラー: openaiライブラリがインストールされていません")
        print("   インストール: pip3 install openai")
        return None
    except Exception as e:
        print(f"❌ エラー: {str(e)}")
        if "api_key" in str(e).lower() or "authentication" in str(e).lower():
            print("   APIキーが正しく設定されているか確認してください")
        return None

def format_transcript_markdown(result, audio_file_path):
    """文字起こし結果をMarkdown形式に整形"""
    markdown = f"""# 音声ファイルの文字起こし

**ファイル名**: {os.path.basename(audio_file_path)}
**言語**: 日本語

---

## 文字起こし

"""
    
    # セグメントごとにタイムスタンプ付きで整形
    if result and "segments" in result and len(result["segments"]) > 0:
        for segment in result["segments"]:
            start_time = segment["start"]
            end_time = segment["end"]
            text = segment["text"]
            
            # 時間を分:秒形式に変換
            start_minutes = int(start_time // 60)
            start_seconds = int(start_time % 60)
            end_minutes = int(end_time // 60)
            end_seconds = int(end_time % 60)
            
            start_timestamp = f"{start_minutes:02d}:{start_seconds:02d}"
            end_timestamp = f"{end_minutes:02d}:{end_seconds:02d}"
            
            markdown += f"**[{start_timestamp} - {end_timestamp}]** {text}\n\n"
    else:
        # セグメント情報がない場合は全文を表示
        if result and "text" in result:
            markdown += result["text"]
        else:
            markdown += "文字起こし結果が取得できませんでした。"
    
    return markdown

def main():
    if len(sys.argv) < 2:
        print("使用方法:")
        print("  python audio_transcript_simple.py <音声ファイルのパス> [--api-key API_KEY]")
        print("\n例:")
        print("  export OPENAI_API_KEY='your-api-key'")
        print("  python audio_transcript_simple.py マーケ講座広告レクチャー-audio.mp4")
        print("\nまたは:")
        print("  python audio_transcript_simple.py audio.mp3 --api-key YOUR_API_KEY")
        print("\n対応ファイル形式:")
        print("  MP4, MP3, WAV, M4A, WEBM など")
        print("\nAPIキーの取得:")
        print("  https://platform.openai.com/api-keys")
        sys.exit(1)
    
    audio_file_path = sys.argv[1]
    api_key = None
    
    # 引数の解析
    if "--api-key" in sys.argv:
        idx = sys.argv.index("--api-key")
        if idx + 1 < len(sys.argv):
            api_key = sys.argv[idx + 1]
    
    # ファイルの存在確認
    if not os.path.exists(audio_file_path):
        print(f"❌ エラー: ファイルが見つかりません: {audio_file_path}")
        sys.exit(1)
    
    # ファイルサイズ確認（25MB制限）
    file_size_mb = os.path.getsize(audio_file_path) / (1024 * 1024)
    if file_size_mb > 25:
        print(f"⚠️  警告: ファイルサイズが25MBを超えています ({file_size_mb:.1f}MB)")
        print("   OpenAI Whisper APIは25MB以下のファイルのみ対応しています")
        print("   ファイルを分割するか、圧縮してください")
    
    try:
        result = transcribe_with_openai_whisper_api(audio_file_path, api_key)
        
        if not result:
            sys.exit(1)
        
        # 出力ファイル名を生成
        base_name = Path(audio_file_path).stem
        output_file = f"{base_name}_transcript.md"
        
        # Markdown形式で保存
        markdown_content = format_transcript_markdown(result, audio_file_path)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        print(f"\n✅ 文字起こしを完了しました！")
        print(f"📄 保存先: {output_file}")
        if result and "text" in result:
            print(f"📊 文字数: {len(result['text'])}文字")
        if result and "segments" in result:
            print(f"📝 セグメント数: {len(result['segments'])}個")
        
    except Exception as e:
        print(f"❌ エラー: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()






