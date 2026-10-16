#!/usr/bin/env bash
# Two-pass loudness normalise to -14 LUFS (true peak -1.5 dB). Usage: ./loudnorm.sh in.wav out.wav
set -e
IN=$1; OUT=$2
J=$(ffmpeg -hide_banner -nostats -i "$IN" -af loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json -f null - 2>&1 | sed -n '/^{/,/^}/p')
g() { echo "$J" | python3 -c "import json,sys;print(json.load(sys.stdin)['$1'])"; }
ffmpeg -hide_banner -loglevel error -y -i "$IN" -af "loudnorm=I=-14:TP=-1.5:LRA=11:measured_I=$(g input_i):measured_TP=$(g input_tp):measured_LRA=$(g input_lra):measured_thresh=$(g input_thresh):offset=$(g target_offset):linear=true" -ar 48000 "$OUT"
