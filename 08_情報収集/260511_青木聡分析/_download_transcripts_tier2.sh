#!/bin/bash
set -u
IDS_FILE="_selected_tier2_ids.txt"
OUT_DIR="transcripts_tier2"
JOBS=10

mkdir -p "$OUT_DIR"

download_one() {
    local id="$1"
    local out="$OUT_DIR/$id"
    local existing
    existing=$(find "$OUT_DIR" -maxdepth 1 -name "${id}.*.vtt" -print -quit 2>/dev/null)
    if [ -n "$existing" ]; then
        echo "[skip] $id"
        return 0
    fi
    yt-dlp \
        --skip-download \
        --write-subs \
        --write-auto-subs \
        --sub-langs "ja,ja-orig,en" \
        --sub-format "vtt" \
        --quiet --no-warnings \
        --output "${out}.%(ext)s" \
        "https://www.youtube.com/watch?v=${id}" 2>&1 | tail -1
    echo "[done] $id"
}

export -f download_one
export OUT_DIR

cat "$IDS_FILE" | xargs -P "$JOBS" -I{} bash -c 'download_one "$@"' _ {} 2>&1 | tail -60
echo "=== Files downloaded ==="
ls -1 "$OUT_DIR"/*.vtt 2>/dev/null | wc -l
echo "=== Unique videos with at least one subtitle ==="
ls -1 "$OUT_DIR"/*.vtt 2>/dev/null | sed -E 's|.*/||; s/\..*//' | sort -u | wc -l
