"""Optional word check (needs openai-whisper): transcribe the narration and compare it with the lines file.
Usage: python3 check_words.py voice_track.wav lines.json [cues.json]"""
import json, re, sys, difflib, whisper
audio, lines = sys.argv[1], json.load(open(sys.argv[2]))
cue = json.load(open(sys.argv[3])) if len(sys.argv) > 3 else None
norm = lambda s: re.sub(r"[^a-z0-9' ]", ' ', s.lower().replace('-', ' ')).split()
res = whisper.load_model('small.en').transcribe(audio, word_timestamps=True, language='en')
heard = [(w['word'], w['start'], w['end']) for seg in res['segments'] for w in seg['words']]
hw = [norm(w)[0] if norm(w) else '' for w, _, _ in heard]
exp = [(n, k) for k in sorted(lines) for n in norm(lines[k])]
sm = difflib.SequenceMatcher(a=[e[0] for e in exp], b=hw, autojunk=False)
print('expected words', len(exp), 'heard', len(hw), 'match ratio', round(sm.ratio(), 3))
for op, a0, a1, b0, b1 in sm.get_opcodes():
    if op != 'equal':
        print(f"  {op}: expected '{' '.join(e[0] for e in exp[a0:a1])}' heard '{' '.join(hw[b0:b1])}' at {heard[b0][1] if b0 < len(heard) else '-'} s")
if cue:
    B = [0, cue['B1'], cue['B2'], cue['B3'], cue['B4'], cue['B5'], cue['END']]
    for op, a0, a1, b0, b1 in sm.get_opcodes():
        if op == 'equal':
            for j in range(a1 - a0):
                k = int(exp[a0 + j][1][1]); t = heard[b0 + j][1]
                if not (B[k] - 0.05 <= t <= B[k + 1]):
                    print(f"  word '{exp[a0+j][0]}' of {exp[a0+j][1]} heard at {t:.2f} s, outside its scene {B[k]:.2f}-{B[k+1]:.2f}")
