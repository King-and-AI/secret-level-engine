#!/usr/bin/env bash
# OPTION 2: WITH VOICEOVER. Needs your own ElevenLabs API key (secret ELEVENLABS_API_KEY) the first time;
# re-runs reuse the saved clips and cost nothing.
# Usage: ./make_voiced.sh out.mp4 lines.json timeline.py [voice.json] [voice_dir]
# Example: ./make_voiced.sh example-voiced.mp4 lines_example.json timeline_example.py voice_example.json voice_example
set -e
cd "$(dirname "$0")"
OUT=$1; LN=$2; TL=$3; VS=${4:-voice_example.json}; VD=${5:-voice}
if [ -z "$OUT" ] || [ ! -f "$LN" ] || [ ! -f "$TL" ] || [ ! -f "$VS" ]; then
  echo "Usage: ./make_voiced.sh out.mp4 lines.json timeline.py [voice.json] [voice_dir]"
  echo "Needs: a lines file (six lines L0-L5), a timeline script (copy timeline_example.py) and voice settings (voice_example.json)."
  exit 2
fi
# 1. narration (skips lines that already have a clip; stops with a plain message if there is no key)
LINES=$LN VOICE=$VS VDIR=$VD python3 tts.py || { rc=$?; [ $rc -eq 3 ] && exit 3; exit $rc; }
# 2. tempo lift, per the voice settings
eval "$(python3 -c "
import json; s=json.load(open('$VS')); f=s.get('fast_lines',[])
print('export TEMPO=%s FAST_TEMPO=%s FAST=\"%s\"' % (s['tempo'], s['fast_tempo'], ' '.join(f)))
print(\"export TEMPO_PER='%s'\" % json.dumps({k: s['fast_tempo'] for k in f}))")"
./prepare_voice.sh "$VD"
# 3. cue sheet from the word timings, then the timing check
VDIR=$VD VTRACK=voice_track.wav CUES=cues.json PLACED=placed.json python3 "$TL"
python3 check_voice.py cues.json placed.json
# 4. music + effects ducked under the voice, loudness, picture, join
CUES=cues.json VTRACK=voice_track.wav python3 audio.py audio_v.wav --voice
./loudnorm.sh audio_v.wav audio_v_norm.wav
VARIANT=${VARIANT:-base} CUES=cues.json python3 render.py video video_v_noaudio.mp4
./mux.sh video_v_noaudio.mp4 audio_v_norm.wav "$OUT"
