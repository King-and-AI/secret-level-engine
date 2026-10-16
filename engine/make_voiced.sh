#!/usr/bin/env bash
# Voiced build. First: tts.py (needs a key) and ./prepare_voice.sh VDIR.
# Usage: TEMPO_PER='{"L1":1.09}' ./make_voiced.sh out.mp4 VDIR timeline_x.py
set -e
cd "$(dirname "$0")"
OUT=$1; VD=$2; TL=$3
VDIR=$VD VTRACK=voice_track.wav CUES=cues.json python3 "$TL"
CUES=cues.json VTRACK=voice_track.wav python3 audio.py audio_v.wav --voice
./loudnorm.sh audio_v.wav audio_v_norm.wav
VARIANT=${VARIANT:-base} CUES=cues.json python3 render.py video video_v_noaudio.mp4
./mux.sh video_v_noaudio.mp4 audio_v_norm.wav "$OUT"
