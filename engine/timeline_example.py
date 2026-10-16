"""Worked example (voiced path): place each spoken phrase on the timeline and derive every visual cue from word timings.
For a new video, copy this file and rewrite the place(...) calls for your own lines; keep the cue names.
Normally run for you by make_voiced.sh."""
import json, os, numpy as np
from scipy.io import wavfile
from phrases import words

SR = 44100
V = {}
for k in ['L0', 'L1', 'L2', 'L3', 'L4', 'L5']:
    sr, x = wavfile.read(f"{os.environ.get('VDIR', 'voice')}/{k}_t.wav"); V[k] = (x.astype(np.float32) / 32768.0, words(k))

placed = []   # (abs_time, line, i0, i1)  word index ranges
W = {}        # word lookup: (line, text, occurrence) -> abs start/end
track_len = 0

def seg(line, first, last=None, occ=1):
    """return word index range [i0, i1] from first word text to last word text (inclusive)"""
    ws = V[line][1]; n = 0; i0 = None
    for i, w in enumerate(ws):
        if w[0] == first:
            n += 1
            if n == occ: i0 = i; break
    assert i0 is not None, (line, first)
    if last is None: return i0, len(ws) - 1
    for j in range(i0, len(ws)):
        if ws[j][0] == last: return i0, j
    raise AssertionError((line, last))

def place(t, line, first, last=None, occ=1):
    """place phrase so that its first word starts at time t; returns (start, end) absolute"""
    i0, i1 = seg(line, first, last, occ)
    ws = V[line][1]; off = t - ws[i0][1]
    placed.append((off, line, i0, i1))
    for i in range(i0, i1 + 1):
        key = (line, ws[i][0]); c = 1
        while (line, ws[i][0], c) in W: c += 1
        W[(line, ws[i][0], c)] = (ws[i][1] + off, ws[i][2] + off)
    return ws[i0][1] + off, ws[i1][2] + off

def w(line, text, occ=1, which=0): return W[(line, text, occ)][which]

cue = {}
G = 0.22
# hook
s, e = place(0.35, 'L0', 'Thousands', 'sky.')
cue['h_title'] = 0.15; cue['h_zzz'] = s - 0.05
s, e = place(e + 0.3, 'L0', "Won't", 'other?')
cue['h_quote'] = s - 0.1; cue['h_attr'] = s; cue['h_skel'] = w('L0', 'crash') - 0.9 + 0.2
cue['h_glitch'] = e + 0.15
s, e = place(cue['h_skel'] + 1.2 + 0.25 if cue['h_skel'] + 1.45 > e + 0.3 else e + 0.3, 'L0', 'Plot', 'twist:')
cue['h_twist'] = s - 0.05; cue['h_glitch'] = s - 0.3
s, e = place(e + 0.15, 'L0', 'they', 'rules.', occ=2)
cue['h_twist2'] = s - 0.05
cue['B1'] = e + 0.35
# level 1
B = cue['B1']
s, e = place(B + 0.1, 'L1', 'Level', 'low.')
s, e = place(max(e + 0.3, B + 1.45), 'L1', 'Starlink', 'kilometres.')
cue['l1_sign'] = s - 0.4; cue['l1_row1'] = s - 0.15
s, e = place(e + G, 'L1', 'Up', 'down.')
cue['l1_row2'] = s; cue['l1_cap1'] = s - 0.1; cue['l1_label'] = s
s, e = place(e + 0.25, 'L1', 'If', 'sinks.')
cue['l1_step1'] = s - 0.1; cue['l1_cap2'] = s - 0.1; cue['l1_eq1'] = s - 0.1
cue['l1_step2'] = w('L1', 'sinks.') - 0.3; cue['l1_eq2'] = cue['l1_step2']; cue['l1_step3'] = cue['l1_step2'] + 0.8
s, e = place(max(e + 0.3, cue['l1_step3'] + 0.5), 'L1', 'Gone', 'it.')
cue['l1_tags'] = s - 0.1
s, e = place(e + 0.25, 'L1', 'Low', 'themselves.')
cue['l1_cap3'] = s - 0.1
s, e = place(e + G, 'L1', 'No', 'forever.')
cue['l1_tags2'] = s - 0.1
s, e = place(e + 0.15, 'L1', 'Steady!', 'Steady!')
cue['l1_xp'] = s - 0.05
cue['B2'] = e + 0.3
# picture
B = cue['B2']
s, e = place(B + 0.25, 'L2', 'Every', 'be.')
cue['g_title'] = s - 0.1; cue['g_axes'] = s + 0.4; cue['g_line1'] = s + 0.9; cue['g_line2'] = s + 1.4
s, e = place(e + 0.25, 'L2', 'That', 'ephemeris.')
cue['g_cap'] = s - 0.1; cue['g_dot'] = e
s, e = place(e + 0.3, 'L2', 'Starlink', 'publicly.')
cue['g_icons'] = s - 0.1
cue['B3'] = e + 0.35
# level 2
B = cue['B3']
s, e = place(B + 0.1, 'L3', 'Level', 'way.')
s, e = place(max(e + 0.3, B + 1.45), 'L3', 'Forecasts', 'cross?')
cue['l2_title'] = s - 0.3; cue['l2_cap1'] = s - 0.1; cue['l2_ones'] = s
s, e = place(e + G, 'L3', 'Its', 'clear.')
cue['l2_morph'] = w('L3', 'steer') - 0.1; cue['l2_labels'] = cue['l2_morph'] + 1.3
s, e = place(max(e + 0.25, cue['l2_labels'] + 0.4), 'L3', 'Stargaze:', 'Stargaze:')
cue['l2_unk'] = s - 0.1; cue['l2_cap2'] = 0
s, e = place(e + G, 'L3', 'thirty', 'there.')
s, e = place(e + 0.25, 'L3', 'Spot', 'it.', occ=1)
cue['l2_cap2'] = s - 0.1; cue['l2_chip'] = s
s, e = place(e + 0.15, 'L3', 'Power!', 'Power!')
cue['l2_power'] = s - 0.03; cue['l2_xp'] = s
cue['B4'] = e + 0.3
# boss
B = cue['B4']
s, e = place(B + 0.1, 'L4', 'Boss', 'behind.')
s, e = place(max(e + 0.25, B + 1.45), 'L4', 'Old', 'satellite?')
cue['b_title'] = s - 0.1; cue['b_food'] = s
s, e = place(e + G, 'L4', 'Deorbit', 'purpose.')
cue['b_grow'] = s
s, e = place(e + 0.3, 'L4', 'Built', 'down.')
cue['b_billions'] = w('L4', 'burn') - 0.05; cue['b_grow_end'] = cue['b_billions'] - 0.15; cue['b_cap1'] = s - 0.1
s, e = place(max(e + 0.25, cue['b_billions'] + 1.6), 'L4', 'Aimed', 'ocean.')
cue['b_partB'] = s - 0.3; cue['b_card1'] = s - 0.1
s, e = place(e + G, 'L4', 'Brought', 'fail.')
cue['b_card2'] = s - 0.1; cue['b_pulse'] = s
s, e = place(e + 0.25, 'L4', 'Safe', 'down.', occ=1)
cue['b_out'] = s - 0.1; cue['b_cap2'] = s - 0.1; cue['b_xp'] = e - 0.3
cue['B5'] = e + 0.3
# outro
B = cue['B5']
s, e = place(B + 0.25, 'L5', 'Fly', 'low.')
cue['o_chip1'] = s - 0.1
s, e = place(e + 0.15, 'L5', 'Get', 'way.')
cue['o_chip2'] = s - 0.1
s, e = place(e + 0.15, 'L5', 'Leave', 'behind.')
cue['o_chip3'] = s - 0.1; cue['o_yah'] = e + 0.05
s, e = place(e + 0.25, 'L5', 'A', 'sky.', occ=1)
cue['o_big'] = s - 0.05
s, e = place(e + 0.2, 'L5', 'Space', 'safe!')
cue['o_confirm'] = w('L5', 'safe!') - 0.03
cue['o_done'] = e + 0.15
cue['o_fade'] = cue['o_done'] + 0.75
cue['END'] = round(cue['o_fade'] + 0.45, 2)

# ---------------- build voice track ----------------
N = int((cue['END'] + 2) * SR)
track = np.zeros(N, np.float32)
for off, line, i0, i1 in placed:
    x, ws = V[line]
    a = ws[i0][1] - 0.04
    if i0 > 0: a = max(a, (ws[i0 - 1][2] + ws[i0][1]) / 2)
    b = ws[i1][2] + 0.18
    if i1 < len(ws) - 1: b = min(b, ws[i1][2] + max(0.03, (ws[i1 + 1][1] - ws[i1][2]) * 0.7))
    a = max(0, a); b = min(len(x) / SR, b)
    sig = x[int(a * SR):int(b * SR)].copy()
    nf = int(0.006 * SR); sig[:nf] *= np.linspace(0, 1, nf); nr = int(0.03 * SR); sig[-nr:] *= np.linspace(1, 0, nr)
    i = int(round((a + off) * SR)); track[i:i + len(sig)] += sig[:max(0, N - i)]
wavfile.write(os.environ.get('VTRACK', 'voice_track.wav'), SR, (np.clip(track, -1, 1) * 32767).astype(np.int16))
cue = {k: round(v, 3) for k, v in cue.items()}
json.dump(cue, open(os.environ.get('CUES', 'cues.json'), 'w'), indent=1)
print('END', cue['END'])
for k in ['B1', 'B2', 'B3', 'B4', 'B5', 'END']: print(k, cue[k])
# phrase list for check_voice.py
json.dump([{'line': line, 'start': round(V[line][1][i0][1] + off, 3), 'end': round(V[line][1][i1][2] + off, 3),
            'text': ' '.join(x[0] for x in V[line][1][i0:i1 + 1])} for off, line, i0, i1 in placed],
          open(os.environ.get('PLACED', 'placed.json'), 'w'), indent=1)
