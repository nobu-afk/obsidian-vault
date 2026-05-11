#!/usr/bin/env python3
"""VTT字幕ファイルからプレーンテキストを抽出 (Tier 2 版)"""
import re, os, glob

IN_DIR = "transcripts_tier2"
OUT_DIR = "transcripts_tier2_clean"
os.makedirs(OUT_DIR, exist_ok=True)

videos = {}
for vtt in sorted(glob.glob(f"{IN_DIR}/*.vtt")):
    fname = os.path.basename(vtt)
    m = re.match(r"^(.+?)\.(ja-orig|ja|en)\.vtt$", fname)
    if not m:
        continue
    vid, lang = m.group(1), m.group(2)
    if vid not in videos:
        videos[vid] = {}
    videos[vid][lang] = vtt

def vtt_to_text(vtt_path):
    with open(vtt_path, encoding="utf-8") as f:
        lines = f.readlines()
    out = []
    prev = ""
    for line in lines:
        line = line.rstrip()
        if not line:
            continue
        if line.startswith("WEBVTT") or line.startswith("Kind:") or line.startswith("Language:"):
            continue
        if "-->" in line:
            continue
        if re.match(r"^\d+$", line):
            continue
        clean = re.sub(r"<[^>]+>", "", line)
        clean = re.sub(r"\s+", " ", clean).strip()
        if not clean:
            continue
        if clean == prev:
            continue
        out.append(clean)
        prev = clean
    return "\n".join(out)

summary = []
for vid in sorted(videos.keys()):
    chosen = videos[vid].get("ja-orig") or videos[vid].get("ja") or videos[vid].get("en")
    if not chosen:
        continue
    text = vtt_to_text(chosen)
    out_path = f"{OUT_DIR}/{vid}.txt"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(text)
    summary.append((vid, len(text), chosen.split("/")[-1]))

print(f"Processed {len(summary)} videos")
print(f"Total chars: {sum(s[1] for s in summary):,}")
print(f"Avg chars/video: {sum(s[1] for s in summary)//len(summary):,}")
print("Top 5 longest:")
for vid, n, src in sorted(summary, key=lambda x: -x[1])[:5]:
    print(f"  {vid}: {n:,} chars ({src})")
