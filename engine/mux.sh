#!/usr/bin/env bash
# Join picture + sound into the final MP4 (H.264 + AAC, standard TV colour range, fast start), then report.
set -e
V=$1; A=$2; OUT=$3
ffmpeg -hide_banner -loglevel error -y -i "$V" -i "$A" -map 0:v -map 1:a \
  -vf "scale=in_range=full:out_range=limited,format=yuv420p" -color_range tv \
  -c:v libx264 -preset slow -crf 22 -c:a aac -b:a 192k -shortest -movflags +faststart "$OUT"
D=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$OUT")
L=$(ffmpeg -hide_banner -nostats -i "$OUT" -af ebur128=peak=true -f null - 2>&1 | grep -E "^\s+I:" | tail -1 | awk '{print $2}')
S=$(du -m "$OUT" | cut -f1)
echo "done: $OUT  length ${D}s  loudness ${L} LUFS  size ${S} MB"
awk "BEGIN{exit !($D < 60)}" || echo "WARNING: 60 s or longer - tighten the cues"
