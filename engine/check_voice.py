"""Timing check for the voiced option: every spoken phrase must sit inside its own scene,
with no overlaps, and the video must stay under 60 s.  Usage: python3 check_voice.py cues.json placed.json"""
import json, sys
cue = json.load(open(sys.argv[1])); ph = json.load(open(sys.argv[2]))
B = [0, cue['B1'], cue['B2'], cue['B3'], cue['B4'], cue['B5'], cue['END']]
names = ['hook', 'Level 1', 'picture', 'Level 2', 'Boss', 'ending']
bad = 0
print('line  scene     window          speech          phrases  status')
for i in range(6):
    p = [x for x in ph if x['line'] == f'L{i}']
    s, e = min(x['start'] for x in p), max(x['end'] for x in p)
    lim = B[i + 1] - (0.1 if i < 5 else 0)
    ok = s >= B[i] and e <= lim
    bad += not ok
    print(f"L{i}    {names[i]:<9} {B[i]:5.2f}-{B[i+1]:5.2f}   {s:5.2f}-{e:5.2f}   {len(p):>3}      {'ok' if ok else 'OVERRUNS ITS SCENE'}")
ph.sort(key=lambda x: x['start'])
for a, b in zip(ph, ph[1:]):
    if b['start'] < a['end'] - 0.01:
        bad += 1; print('OVERLAP:', a['text'], '|', b['text'])
print(f"END {cue['END']:.2f} s", 'ok' if cue['END'] < 60 else 'TOO LONG (must be under 60 s)')
bad += cue['END'] >= 60
if bad:
    print('Timing check failed: tighten gaps in the timeline, or add long lines to "fast_lines" in the voice settings, then re-run (no new credits).')
    sys.exit(1)
print('Timing check passed.')
