#!/usr/bin/env bash
# Pull frames from the FINISHED video for checking (some problems only show in the encoded file).
# Usage: ./frames_qa.sh final.mp4 qa_dir   -> full-size frames at 1 per second + 2x2 contact grids
set -e
IN=$1; D=${2:-qa}
mkdir -p "$D/full"
ffmpeg -hide_banner -loglevel error -y -i "$IN" -vf fps=1 "$D/full/f%03d.png"
python3 "$(dirname "$0")/grid.py" "$D/full/f*.png" "$D/grid" 4
echo "frames in $D/full, grids in $D/grid*.png"
