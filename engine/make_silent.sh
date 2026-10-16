#!/usr/bin/env bash
# OPTION 1: SILENT (music + sound effects + captions). No account, no key, no cost.
# Usage: ./make_silent.sh out.mp4            (cue times = CUE_DEFAULT in scene.js)
#        VARIANT=city ./make_silent.sh out.mp4  (adds the optional city skyline)
set -e
cd "$(dirname "$0")"
OUT=${1:-silent.mp4}
rm -f cues.json   # a voiced build leaves cues.json behind; the silent cut uses the hand-set times in scene.js
python3 audio.py audio.wav
./loudnorm.sh audio.wav audio_norm.wav
VARIANT=${VARIANT:-base} python3 render.py video video_noaudio.mp4
./mux.sh video_noaudio.mp4 audio_norm.wav "$OUT"
