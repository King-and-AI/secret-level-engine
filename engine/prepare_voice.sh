#!/usr/bin/env bash
# Turn the ElevenLabs MP3s into the WAV files the timeline needs, with a small tempo lift.
# Usage: ./prepare_voice.sh voice_x            (tempo 1.06 for every line)
#        FAST="L1 L4" ./prepare_voice.sh voice_x   (tempo 1.09 for the long lines named in FAST)
set -e
cd "$(dirname "$0")"
D=${1:-voice}
for k in L0 L1 L2 L3 L4 L5; do
  ffmpeg -loglevel error -y -i "$D/$k.mp3" -ar 44100 -ac 1 "$D/$k.wav"
  T=1.06; [ -n "$FAST" ] && echo " $FAST " | grep -q " $k " && T=1.09
  ffmpeg -loglevel error -y -i "$D/$k.wav" -af "rubberband=tempo=$T:transients=crisp:formant=preserved" -ar 44100 -ac 1 "$D/${k}_t.wav"
done
echo "voice ready in $D"
