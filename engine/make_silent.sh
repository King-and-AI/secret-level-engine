#!/usr/bin/env bash
# Silent build (music + sound effects + captions, no narration, no credits).
# Usage: ./make_silent.sh out.mp4            (cue times = CUE_DEFAULT in scene.js, plus cues.json if present)
#        VARIANT=city ./make_silent.sh out.mp4  (adds the optional city skyline)
set -e
cd "$(dirname "$0")"
OUT=${1:-silent.mp4}
python3 audio.py audio.wav
./loudnorm.sh audio.wav audio_norm.wav
VARIANT=${VARIANT:-base} python3 render.py video video_noaudio.mp4
./mux.sh video_noaudio.mp4 audio_norm.wav "$OUT"
