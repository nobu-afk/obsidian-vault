#!/usr/bin/env python3
"""
MP3（または任意の音声ファイル）から文字起こしするスクリプト
faster-whisper を使用。日本語対応。

必要なパッケージ: pip install faster-whisper

使い方:
  python transcribe_mp3.py <音声ファイルのパス> [--model small] [--lang ja]
  python transcribe_mp3.py ./audio.mp3
  python transcribe_mp3.py "/path/to/audio.m4a" --model base
"""

import argparse
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
VAULT_ROOT = os.path.dirname(SCRIPT_DIR)
OUTPUT_DIR = os.path.join(VAULT_ROOT, "transcripts")


def transcribe(audio_path: str, model_size: str = "small", language: str = "ja"):
    """faster-whisper で音声を文字起こし。セグメントのリストを返す。"""
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        print("faster-whisper がインストールされていません。")
        print("実行: pip install faster-whisper")
        sys.exit(1)

    # CPU では compute_type="int8" が軽い。GPU なら "float16"
    device = "cuda" if _has_cuda() else "cpu"
    compute_type = "float16" if device == "cuda" else "int8"

    model = WhisperModel(model_size, device=device, compute_type=compute_type)
    segments, info = model.transcribe(
        audio_path,
        language=language if language else None,
        beam_size=5,
        vad_filter=True,
    )
    # ジェネレータをリストに
    return list(segments), info


def _has_cuda():
    try:
        import torch
        return torch.cuda.is_available()
    except Exception:
        return False


def main():
    parser = argparse.ArgumentParser(description="MP3/音声ファイルを文字起こし")
    parser.add_argument("audio_path", help="音声ファイルのパス（mp3, wav, m4a 等）")
    parser.add_argument(
        "--model",
        default="small",
        choices=["tiny", "base", "small", "medium", "large-v3"],
        help="Whisper モデルサイズ（大きいほど精度向上、遅くなる）",
    )
    parser.add_argument("--lang", default="ja", help="言語コード（ja, en 等）。空で自動検出")
    parser.add_argument("-o", "--output-dir", default=OUTPUT_DIR, help="出力フォルダ")
    args = parser.parse_args()

    audio_path = os.path.abspath(args.audio_path)
    if not os.path.isfile(audio_path):
        print(f"ファイルが見つかりません: {audio_path}")
        sys.exit(1)

    base_name = os.path.splitext(os.path.basename(audio_path))[0]
    # ファイル名に使えない文字を除去
    safe_name = "".join(c for c in base_name if c.isalnum() or c in "._- ").strip() or "transcript"
    output_md = os.path.join(args.output_dir, f"{safe_name}_文字起こし.md")
    output_txt = os.path.join(args.output_dir, f"{safe_name}_文字起こし.txt")

    print(f"文字起こし中: {audio_path} (モデル: {args.model})")
    segments, info = transcribe(audio_path, model_size=args.model, language=args.lang or None)
    detected = getattr(info, "language", "") or "?"

    lines = []
    full_text = []
    for seg in segments:
        start = seg.start
        text = (seg.text or "").strip()
        if not text:
            continue
        lines.append(f"- [{start:.1f}s] {text}")
        full_text.append(text)

    os.makedirs(args.output_dir, exist_ok=True)

    md_content = f"""# 音声文字起こし

- 元ファイル: `{os.path.basename(audio_path)}`
- 検出言語: {detected}
- モデル: {args.model}

## タイムスタンプ付き

"""
    md_content += "\n".join(lines)
    md_content += "\n\n## 全文\n\n"
    md_content += " ".join(full_text)

    with open(output_md, "w", encoding="utf-8") as f:
        f.write(md_content)
    with open(output_txt, "w", encoding="utf-8") as f:
        f.write("\n".join(full_text))

    print(f"Markdown: {output_md}")
    print(f"テキスト: {output_txt}")
    return output_md, output_txt


if __name__ == "__main__":
    main()
