import numpy as np, scipy.signal as sg, sys, os
from scipy.io import wavfile
import cues

SR = 44100
K = cues.load()
END = K['END']
N = int((END + 2.0) * SR)
rng = np.random.default_rng(7)
VOICE = '--voice' in sys.argv   # quieter, sparser mix under narration

bus = {k: np.zeros((2, N)) for k in ['drums', 'duck', 'mel', 'sfx', 'rev']}
kick_times = []

NAMES = {'C': 0, 'C#': 1, 'Db': 1, 'D': 2, 'D#': 3, 'Eb': 3, 'E': 4, 'F': 5, 'F#': 6, 'G': 7, 'G#': 8, 'Ab': 8, 'A': 9, 'Bb': 10, 'B': 11}
def m(s): return 12 * (int(s[-1]) + 1) + NAMES[s[:-1]]
def hz(n): return 440.0 * 2 ** ((n - 69) / 12)
def tt(d): return np.arange(max(1, int(d * SR))) / SR

def add(name, t0, sig, gain=1.0, pan=0.0, send=0.0):
    i = int(round(t0 * SR))
    if sig.ndim == 1:
        gl, gr = np.cos((pan + 1) * np.pi / 4) * 1.41, np.sin((pan + 1) * np.pi / 4) * 1.41
        st = np.vstack([sig * gl, sig * gr])
    else:
        st = sig
    if i < 0: st = st[:, -i:]; i = 0
    n = min(st.shape[1], N - i)
    if n <= 0: return
    bus[name][:, i:i + n] += st[:, :n] * gain
    if send: bus['rev'][:, i:i + n] += st[:, :n] * gain * send

# ---------- oscillators ----------
def phase(f, n):
    f = np.broadcast_to(np.asarray(f, float), (n,))
    return np.cumsum(f / SR) % 1.0, f / SR
def blep(ph, dt):
    out = np.zeros_like(ph)
    a = ph < dt; x = ph[a] / dt[a]; out[a] = x + x - x * x - 1
    b = ph > 1 - dt; x = (ph[b] - 1) / dt[b]; out[b] = x * x + x + x + 1
    return out
def saw(f, d):
    n = len(tt(d)); ph, dt = phase(f, n); return 2 * ph - 1 - blep(ph, dt)
def pulse(f, d, w=0.5):
    n = len(tt(d)); ph, dt = phase(f, n); ph2 = (ph + w) % 1
    return (2 * ph - 1 - blep(ph, dt)) - (2 * ph2 - 1 - blep(ph2, dt))
def sine(f, d):
    n = len(tt(d)); f = np.broadcast_to(np.asarray(f, float), (n,)); return np.sin(2 * np.pi * np.cumsum(f) / SR)
def noise(d): return rng.uniform(-1, 1, len(tt(d)))
def lp(x, fc, order=2): return sg.sosfilt(sg.butter(order, min(fc, SR * 0.45), 'low', fs=SR, output='sos'), x)
def hp(x, fc, order=2): return sg.sosfilt(sg.butter(order, fc, 'high', fs=SR, output='sos'), x)
def bp(x, f1, f2, order=2): return sg.sosfilt(sg.butter(order, [f1, min(f2, SR * 0.45)], 'band', fs=SR, output='sos'), x)
def fade(x, a=0.003, r=0.01):
    n = len(x); e = np.ones(n); na, nr = int(a * SR), int(r * SR)
    if na: e[:na] = np.linspace(0, 1, na)
    if nr: e[-nr:] *= np.linspace(1, 0, nr)
    return x * e
def svf_sweep(x, fc, q=2.0):
    """time-varying band-pass (state variable filter), fc array per sample"""
    y = np.zeros_like(x); low = band = 0.0; damp = 1.0 / q
    fcoef = 2 * np.sin(np.pi * np.clip(fc, 20, SR / 6) / SR)
    for i in range(len(x)):
        f = fcoef[i]; high = x[i] - low - damp * band; band += f * high; low += f * band; y[i] = band
    return y

# ---------- instruments ----------
def kick():
    t = tt(0.45); f = 45 + 115 * np.exp(-t * 28)
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 6.5)
    s += lp(rng.uniform(-1, 1, len(t)), 4000) * np.exp(-t * 300) * 0.4
    return np.tanh(1.6 * s) * 0.9
def clap():
    t = tt(0.3); e = np.zeros_like(t)
    for k in range(3): d = k * 0.011; e += (t >= d) * np.exp(-np.clip(t - d, 0, None) * 160)
    e += (t >= 0.022) * np.exp(-np.clip(t - 0.022, 0, None) * 16) * 0.7
    return bp(rng.uniform(-1, 1, len(t)), 900, 4200) * e * 1.6
def snare():
    t = tt(0.2)
    return bp(rng.uniform(-1, 1, len(t)), 1500, 8000) * np.exp(-t * 24) + sine(190, 0.2) * np.exp(-t * 30) * 0.5
def hat(open_=False):
    d = 0.3 if open_ else 0.06; t = tt(d)
    return hp(rng.uniform(-1, 1, len(t)), 7000) * np.exp(-t * (13 if open_ else 85))
def crash(d=2.6):
    t = tt(d); x = rng.uniform(-1, 1, len(t))
    return (hp(x, 3500) * 0.8 + bp(x, 5000, 12000) * 0.5) * np.exp(-t * 1.8) * fade(np.ones_like(t), 0.002, 0.2)
def bass(n, d, drive=1.0):
    t = tt(d); f = hz(n)
    s = saw(f, d) * 0.6 + sine(f, d) * 0.8
    s = lp(s, 700 * drive)
    s = np.tanh(s * (1.4 + drive)) * (0.65 + 0.35 * np.exp(-t * 9))
    return fade(s, 0.004, 0.03)
def stab(notes, d=0.24, bright=2800):
    t = tt(d); s = sum(saw(hz(n) * r, d) for n in notes for r in (0.996, 1.004)) / (2 * len(notes))
    return fade(lp(s, bright) * np.exp(-t * 12), 0.003, 0.03)
def pad(notes, d, bright=1100):
    t = tt(d); s = sum(saw(hz(n) * r, d) for n in notes for r in (0.993, 1.0, 1.007)) / (3 * len(notes))
    e = np.minimum(1, t / 0.25) * np.minimum(1, (d - t) / 0.3)
    return lp(s, bright) * e
def chip(n, d, w=0.25, vib=True):
    t = tt(d); f = hz(n) * (1 + (0.006 * np.sin(2 * np.pi * 6 * t) * np.minimum(1, t / 0.15) if vib else 0))
    s = pulse(f, d, w) * (0.35 + 0.65 * np.exp(-t * 7))
    return fade(lp(s, 6000), 0.003, 0.02)
def rhodes(n, d):
    t = tt(d); f = hz(n)
    s = (sine(f, d) + 0.28 * sine(2 * f, d) * np.exp(-t * 3) + 0.08 * sine(3 * f, d) * np.exp(-t * 6)) * np.exp(-t * 1.2)
    return fade(s * (1 + 0.15 * np.sin(2 * np.pi * 4.5 * t)), 0.006, 0.2)
def musicbox(n, d=1.2):
    t = tt(d); f = hz(n)
    return fade((sine(f, d) + 0.25 * sine(4 * f, d) * np.exp(-t * 8)) * np.exp(-t * 3.5), 0.002, 0.1)

# ---------- sfx ----------
def s_pop(p=1.0):
    t = tt(0.14); f = 380 * p + 700 * p * (1 - np.exp(-t * 60))
    return fade(sine(f, 0.14) * np.exp(-t * 32), 0.001, 0.02)
def s_tick():
    t = tt(0.03); return bp(rng.uniform(-1, 1, len(t)), 2500, 7000) * np.exp(-t * 200)
def s_whoosh(d=0.6, f0=250, f1=4000):
    t = tt(d); x = rng.uniform(-1, 1, len(t)); u = t / d
    fc = f0 * (f1 / f0) ** u
    e = np.sin(np.pi * u) ** 1.5
    return svf_sweep(x, fc, 1.2) * e * 1.4
def s_coin(p=1.0):
    a = pulse(988 * p, 0.07, 0.5) * 0.8
    t = tt(0.32); b = pulse(1319 * p, 0.32, 0.5) * np.exp(-t * 9)
    return fade(lp(np.concatenate([a, b]), 7000), 0.001, 0.03) * 0.5
def s_ding(f=1047, d=1.4):
    t = tt(d); s = sum(a * sine(f * r, d) * np.exp(-t * k) for r, a, k in [(1, 1, 3), (2.4, 0.5, 5), (3.9, 0.3, 8), (5.4, 0.2, 11)])
    return fade(s, 0.001, 0.1) * 0.5
def s_zip(d=0.8):
    t = tt(d); f = 300 * (1500 / 300) ** (t / d)
    return fade(sine(f, d) * 0.5 + pulse(f, d, 0.3) * 0.1, 0.01, 0.1) * np.sin(np.pi * t / d) ** 0.5
def s_blip(f=1200, d=0.05): return fade(pulse(f, d, 0.5), 0.001, 0.01) * 0.45
def s_impact(big=1.0):
    t = tt(1.6); f = 38 + 70 * np.exp(-t * 9)
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * (2.2 / big))
    s += lp(rng.uniform(-1, 1, len(t)), 1800) * np.exp(-t * 12) * 0.7
    return np.tanh(s * 1.8) * 0.9
def s_scratch():
    d = 0.4; t = tt(d); u = t / d
    fc = 400 + 2200 * np.abs(np.sin(np.pi * 2.6 * u)) * (1 - u * 0.7)
    x = svf_sweep(rng.uniform(-1, 1, len(t)), fc, 3.0) * 2.2
    s = saw(120 + 500 * np.abs(np.sin(np.pi * 2.6 * u)), d) * 0.25
    return fade((x + s) * (1 - u) ** 0.5, 0.002, 0.05)
def s_riser(d):
    t = tt(d); u = t / d; x = rng.uniform(-1, 1, len(t))
    s = svf_sweep(x, 300 * (7000 / 300) ** u, 1.5) * 0.9 + sine(180 * (1400 / 180) ** (u ** 1.3), d) * 0.25
    return s * u ** 2
def s_boing():
    t = tt(0.45); f = 260 * (1 + 0.45 * np.sin(2 * np.pi * 14 * t) * np.exp(-t * 7)) * (1 + t)
    return fade(sine(f, 0.45) * np.exp(-t * 6), 0.002, 0.05) * 0.8
def s_boop(f0=360, f1=220):
    t = tt(0.35); f = f0 + (f1 - f0) * (t / 0.35)
    return fade(sine(f, 0.35) * np.exp(-t * 7), 0.01, 0.05) * 0.6
def s_arp(notes, step=0.055, last=0.35, w=0.5):
    parts = [chip(n, step, w, vib=False) for n in notes[:-1]] + [chip(notes[-1], last, w)]
    return np.concatenate(parts)
def s_siren():
    parts = [chip(m(n), 0.17, 0.5, vib=False) for n in ['E5', 'C5', 'E5', 'C5']]
    return np.concatenate(parts) * 0.8
def s_type(): return s_tick() * 0.6

# =====================================================================
# MUSIC
# =====================================================================
MAJOR = [(m('C2'), [m('E4'), m('G4'), m('C5')]), (m('G1'), [m('D4'), m('G4'), m('B4')]),
         (m('A1'), [m('E4'), m('A4'), m('C5')]), (m('F1'), [m('F4'), m('A4'), m('C5')])]
MINOR = [(m('A1'), [m('E4'), m('A4'), m('C5')]), (m('F1'), [m('F4'), m('A4'), m('C5')]),
         (m('G1'), [m('D4'), m('G4'), m('B4')]), (m('E1'), [m('E4'), m('G#4'), m('B4')])]
LEAD = {  # per chord index: (eighth index, note, length in eighths)
    0: [(0, 'G5', 1), (1, 'E5', 1), (2, 'G5', 1), (3, 'C6', 2), (6, 'B5', 1), (7, 'G5', 1)],
    1: [(0, 'B5', 1), (1, 'G5', 1), (2, 'D5', 1), (3, 'G5', 2), (6, 'A5', 1), (7, 'B5', 1)],
    2: [(0, 'C6', 1), (1, 'A5', 1), (2, 'E5', 1), (3, 'A5', 2), (6, 'B5', 1), (7, 'C6', 1)],
    3: [(0, 'A5', 1), (1, 'F5', 1), (2, 'C5', 1), (3, 'F5', 2), (5, 'G5', 1), (6, 'A5', 2)],
}

def groove(start, end, prog, kick_on=True, clap_on=True, hats='8', stabs=True, arp=False, lead=False, padv=0.0,
           bass_style='bounce', drive=1.0, nokick=None):
    b0 = start; i = 0
    while b0 < end - 0.05:
        root, ch = prog[i % len(prog)]
        for j in range(4):
            bt = b0 + j * 0.5
            if bt >= end - 0.02: break
            if kick_on and not (nokick and nokick[0] <= bt < nokick[1]):
                add('drums', bt, kick(), 1.0); kick_times.append(bt)
            if clap_on and j in (1, 3): add('drums', bt, clap(), 0.42, 0.0, 0.25)
            if hats == '8':
                if bt + 0.25 < end: add('drums', bt + 0.25, hat(j == 3), 0.22 if j != 3 else 0.14, 0.25)
            elif hats == '16':
                for q in range(4):
                    ht = bt + q * 0.125
                    if ht < end: add('drums', ht, hat(), [0.12, 0.08, 0.2, 0.08][q], -0.2 if q % 2 else 0.25)
            if stabs and bt + 0.25 < end: add('duck', bt + 0.25, stab(ch), 0.30, 0.0, 0.3)
        # bass
        if bass_style == 'bounce':
            pat = [(0, 0, 0.2), (1, 0, 0.12), (3, 0, 0.2), (5, 0, 0.2), (6, 12, 0.2), (7, 0, 0.12)]
        else:  # drive: all eighths with octave jumps
            pat = [(e, 12 if e % 2 else 0, 0.2) for e in range(8)]
        for e, off, dur in pat:
            et = b0 + e * 0.25
            if et < end - 0.02: add('duck', et, bass(root + 12 + off, dur, drive), 0.55)
        if padv > 0: add('duck', b0, pad(ch, min(2.0, end - b0) + 0.05), padv, 0.0, 0.4)
        if arp:
            notes = [n - 12 for n in ch] + ch + [ch[0] + 12]
            for s in range(16):
                st = b0 + s * 0.125
                if st < end - 0.02: add('mel', st, chip(notes[s % len(notes)], 0.11, 0.25, vib=False), 0.10, 0.35 if s % 2 else -0.35, 0.3)
        if lead:
            for e, nn, ln in LEAD[i % 4]:
                et = b0 + e * 0.25
                if et < end - 0.02: add('mel', et, chip(m(nn), ln * 0.25 * 0.95, 0.25), 0.16, 0.0, 0.35)
        b0 += 2.0; i += 1

# --- intro (sleepy lo-fi) with tape stop ---
def intro():
    g = K['h_glitch']
    L = int((g + 0.1) * SR); buf = np.zeros((2, L))
    def put(t0, sig, gain, pan=0.0):
        i = int(t0 * SR); n = min(len(sig), L - i)
        if n > 0:
            buf[0, i:i + n] += sig[:n] * gain * np.cos((pan + 1) * np.pi / 4) * 1.41
            buf[1, i:i + n] += sig[:n] * gain * np.sin((pan + 1) * np.pi / 4) * 1.41
    for n in ['F3', 'A3', 'C4', 'E4']: put(0.0, rhodes(m(n), 1.6), 0.12)
    for n in ['E3', 'G3', 'B3', 'D4']: put(1.5, rhodes(m(n), 1.8), 0.12)
    for t0, n in [(0.25, 'E5'), (0.75, 'C5'), (1.25, 'A4'), (1.75, 'B4'), (2.25, 'G4'), (2.6, 'D5')]: put(t0, musicbox(m(n)), 0.10, 0.2)
    for t0 in np.arange(0.0, g, 0.5): put(t0, lp(kick(), 300), 0.25)   # soft heartbeat
    crack = (rng.uniform(0, 1, L) > 0.9993) * rng.uniform(-1, 1, L); put(0, lp(crack, 5000) + lp(rng.uniform(-1, 1, L), 3000) * 0.012, 0.5)
    # tape stop over last 0.4s
    ts = g - 0.4; t = np.arange(L) / SR
    speed = np.where(t < ts, 1.0, np.clip(1 - (t - ts) / 0.4, 0, 1) ** 1.5)
    tau = np.cumsum(speed) / SR
    out = np.vstack([np.interp(tau, t, buf[c]) for c in range(2)]) * np.where(t < g, 1.0, 0.0)
    fade_in = np.minimum(1, t / 0.3)
    bus['mel'][:, :L] += out * fade_in

def build_music():
    k = K
    intro()
    # build-up after plot twist
    t = k['h_twist2']; b1 = k['B1']
    times = list(np.arange(t, b1 - 0.8, 0.25)) + list(np.arange(b1 - 0.8, b1 - 0.4, 0.125)) + list(np.arange(b1 - 0.4, b1 - 0.02, 0.0625))
    for x in times:
        g = 0.18 + 0.5 * (x - t) / (b1 - t); add('drums', x, snare(), g, 0.0, 0.2)
    add('sfx', t, s_riser(b1 - t), 0.30, 0.0, 0.3)
    # sections
    groove(k['B1'], k['B2'], MAJOR, padv=0.12 if not VOICE else 0.08)
    groove(k['B2'], k['B3'], MAJOR, stabs=False, arp=True, padv=0.12)
    groove(k['B3'], k['B4'], MAJOR, lead=not VOICE, arp=VOICE, padv=0.12)
    groove(k['B4'], k['B5'], MINOR, hats='16', bass_style='drive', drive=1.6, padv=0.16, arp=True,
           nokick=(k['b_billions'] - 1.0, k['b_billions']), clap_on=True)
    # outro: C (bar), F G (half bars), then final chord
    o = k['B5']; done = k['o_done']
    OUT = [(m('C2'), [m('E4'), m('G4'), m('C5')]), (m('F1'), [m('F4'), m('A4'), m('C5')]), (m('G1'), [m('D4'), m('G4'), m('B4')])]
    groove(o, min(o + 2, done), OUT[:1], padv=0.14, lead=False)
    if o + 2 < done:
        groove(o + 2, min(o + 3, done), OUT[1:2], padv=0.14)
        groove(min(o + 3, done), done, OUT[2:3], padv=0.14)
    fin = [m('C4'), m('E4'), m('G4'), m('C5'), m('E5')]
    add('duck', done, pad(fin, END - done + 1.0, 1800), 0.30, 0.0, 0.5)
    add('duck', done, stab(fin, 0.6, 3500), 0.45, 0.0, 0.5)
    add('duck', done, bass(m('C2'), 1.6), 0.7)
    add('drums', done, kick(), 1.0); add('drums', done, crash(), 0.35, 0.0, 0.2)

def build_sfx():
    k = K; S = lambda t0, sig, g, pan=0.0, send=0.15: add('sfx', t0, sig, g, pan, send)
    lv = 0.6 if VOICE else 1.0
    # hook
    S(k['h_title'], s_pop(1.0), 0.35 * lv)
    for i in range(3): S(k['h_zzz'] + i * 0.25, s_boop(330 - i * 40, 220 - i * 40), 0.28 * lv, 0.5)
    for j in range(0, 28, 2): S(k['h_quote'] + j * 0.8 / 28, s_type(), 0.35 * lv, 0.1)
    S(k['h_glitch'], s_scratch(), 0.55)
    S(k['h_twist'], s_impact(0.8), 0.55, 0, 0.3)
    S(k['h_twist2'], s_pop(1.3), 0.3 * lv)
    # wipes
    for B in ['B1', 'B2', 'B3', 'B4', 'B5']: S(k[B] - 0.35, s_whoosh(0.6), 0.38)
    # level banners
    for B, sig in [('B1', 'lvl'), ('B3', 'lvl'), ('B4', 'boss')]:
        t0 = k[B] + 0.03
        S(t0, s_impact(1.0), 0.6, 0, 0.3)
        if sig == 'lvl': S(t0 + 0.05, s_arp([m('C6'), m('E6'), m('G6'), m('C7')], 0.05, 0.4), 0.22, 0, 0.3)
        else: S(t0 + 0.05, s_siren(), 0.18, 0, 0.3)
    if 'h_skel' in k:   # skeleton 'still waiting' beat: fast clock ticks
        for j in range(12): S(k['h_skel'] + 0.1 + j * 0.12, s_tick(), 0.35 * lv * (0.6 + 0.4 * (j % 2)), 0.5)
    if 'l2_power' in k:
        S(k['l2_power'], s_impact(0.5), 0.35, 0, 0.3); S(k['l2_power'], s_arp([m('C6'), m('G6'), m('C7')], 0.04, 0.25), 0.16, 0.5, 0.3)
    if 'o_confirm' in k:
        S(k['o_confirm'] + 0.1, s_impact(0.6), 0.55, 0.4, 0.2)
    if 'l2_unk' in k:
        S(k['l2_unk'], s_pop(1.3), 0.22 * lv, 0.1); S(k['l2_unk'] + 0.2, s_pop(1.45), 0.2 * lv, 0.3)
    if 'b_food' in k:
        S(k['b_food'] + 0.25, s_blip(1320, 0.05), 0.2 * lv, -0.2); S(k['b_food'] + 0.33, s_blip(1760, 0.07), 0.2 * lv, -0.2)
    # level 1
    if 'l1_sign' in k:
        S(k['l1_sign'], s_ding(2093, 0.8), 0.14 * lv, -0.5, 0.3); S(k['l1_sign'] + 0.15, s_pop(1.1), 0.2 * lv, -0.6)
    for base, idxs in [(k['l1_row1'], [0, 1, 3]), (k['l1_row2'], [0, 2, 3])]:
        for i in idxs: S(base + i * 0.08, s_pop(0.9 + i * 0.08), 0.22 * lv, -0.3)
        S(base + 5 * 0.08, s_blip(1568, 0.06), 0.2 * lv, -0.3)
    S(k['l1_eq1'], s_pop(1.2), 0.25 * lv, 0.3); S(k['l1_eq2'], s_pop(1.25), 0.25 * lv, 0.3)
    for c in ['l1_step1', 'l1_step2', 'l1_step3']: S(k[c], s_blip(900, 0.04), 0.25 * lv, 0.3)
    for i in range(3): S(k['l1_tags'] + i * 0.06, s_coin(1.0 + i * 0.03), 0.30 * lv, -0.2)
    for i in range(3): S(k['l1_tags2'] + i * 0.06, s_coin(1.1 + i * 0.03), 0.30 * lv, -0.2)
    S(k['l1_tags2'] + 0.45, s_ding(1319, 1.0), 0.25 * lv, -0.2, 0.3)
    S(k['l1_xp'], s_arp([m('G5'), m('C6'), m('E6'), m('G6')], 0.05, 0.3), 0.18, 0.4, 0.3)
    # graph
    S(k['g_title'], s_pop(1.0), 0.25 * lv)
    S(k['g_axes'], s_whoosh(0.5, 400, 2000), 0.15 * lv)
    S(k['g_line1'], s_zip(0.8), 0.18 * lv, -0.2); S(k['g_line2'], s_zip(0.8), 0.18 * lv, 0.0)
    S(k['g_dot'], s_ding(1568, 1.4), 0.32, -0.1, 0.35)
    S(k['g_icons'], s_pop(1.3), 0.2 * lv, 0.4); S(k['g_icons'] + 0.12, s_pop(1.4), 0.2 * lv, 0.4)
    # level 2
    S(k['l2_title'], s_pop(1.0), 0.25 * lv)
    S(k['l2_ones'], s_blip(1400, 0.04), 0.22 * lv); S(k['l2_ones'] + 0.08, s_blip(1870, 0.05), 0.22 * lv)
    S(k['l2_morph'], s_whoosh(0.9, 300, 3000), 0.3 * lv)
    for i in range(6): S(k['l2_morph'] + 0.2 + i * 0.14, s_blip(1000 + i * 160, 0.035), 0.12 * lv)
    for i in range(3): S(k['l2_labels'] + i * 0.15, s_pop(1.0 + i * 0.15), 0.22 * lv)
    S(k['l2_chip'], s_boing(), 0.3 * lv, 0.5)
    S(k['l2_xp'], s_arp([m('G5'), m('C6'), m('E6'), m('G6')], 0.05, 0.3), 0.18, 0.4, 0.3)
    # boss
    S(k['b_title'], s_pop(0.8), 0.25 * lv)
    S(k['b_grow'], s_riser(k['b_billions'] - k['b_grow']), 0.42, 0, 0.3)
    S(k['b_billions'], s_impact(1.6), 0.85, 0, 0.4)
    S(k['b_billions'], crash(), 0.3, 0, 0.3)
    S(k['b_card1'], s_pop(1.1), 0.25 * lv, -0.3); S(k['b_card2'], s_pop(1.2), 0.25 * lv, -0.3)
    for d in [0, 0.3, 0.6]:
        for li, lx in enumerate([780, 960, 1140]):
            q = (lx - 580) / 780.0; S(k['b_pulse'] + d + q * 1.3 * 0.5 + 0.2, s_blip(1200 + 300 * li, 0.04), 0.10 * lv, -0.4 + li * 0.4)
    for j in range(0, 24, 2): S(k['b_out'] + 0.1 + j * 0.7 / 24, s_type(), 0.3 * lv, 0.5)
    S(k['b_xp'], s_arp([m('C6'), m('E6'), m('G6'), m('C7'), m('E7')], 0.045, 0.45), 0.2, 0.4, 0.3)
    # outro
    for i, c in enumerate(['o_chip1', 'o_chip2', 'o_chip3']): S(k[c], s_pop(1.0 + 0.2 * i), 0.3 * lv, -0.4 + 0.4 * i)
    S(k['o_yah'], s_boop(500, 700), 0.25 * lv, -0.4)
    S(k['o_big'], s_impact(0.9), 0.5, 0, 0.3)
    S(k['o_done'], s_arp([m('G5'), m('C6'), m('E6'), m('G6'), m('E6'), m('G6')], 0.11, 0.7, 0.25), 0.22, 0, 0.4)

build_music(); build_sfx()

# sidechain duck from kicks
t = np.arange(N) / SR; sc = np.ones(N)
for kt in kick_times:
    i = int(kt * SR); n = min(int(0.35 * SR), N - i); u = np.arange(n) / SR
    sc[i:i + n] = np.minimum(sc[i:i + n], 1 - 0.55 * np.exp(-u * 12))
bus['duck'] *= sc

# reverb
def ir(d=1.8, seed=0):
    r = np.random.default_rng(seed); u = np.arange(int(d * SR)) / SR
    x = r.uniform(-1, 1, len(u)) * np.exp(-u * 3.2); x = lp(x, 6000); x[:int(0.02 * SR)] = 0; return x / np.sqrt(np.sum(x ** 2))
rv = np.vstack([sg.fftconvolve(bus['rev'][c], ir(1.8, c + 1))[:N] for c in range(2)]) * 0.9

music = bus['drums'] * 0.85 + bus['duck'] + bus['mel'] + rv * 0.6
if VOICE:
    bed = music * 0.55 + bus['sfx']
    _, v = wavfile.read(os.environ.get('VTRACK', 'voice_track.wav')); v = v.astype(float) / 32768
    v = hp(v, 75); v = np.pad(v, (0, max(0, N - len(v))))[:N]
    env = lp(np.abs(v), 4.0); env = np.clip(env / (0.35 * env.max()), 0, 1)
    duck = 1 - 0.4 * env
    act = env > 0.15
    v_rms = np.sqrt(np.mean(v[act] ** 2)); b_rms = np.sqrt(np.mean(bed.mean(0) ** 2))
    g_bed = v_rms * 10 ** (-8 / 20) / b_rms
    print('voice rms', 20 * np.log10(v_rms), 'bed rms', 20 * np.log10(b_rms), 'bed gain dB', 20 * np.log10(g_bed))
    mix = bed * g_bed * duck + np.vstack([v, v])
else:
    mix = music + bus['sfx']
# fade out at end
fo = np.clip((END - t) / (END - K['o_fade']), 0, 1); mix *= fo
mix = np.tanh(mix * 0.9) / 0.9 if np.max(np.abs(mix)) > 0.9 else mix
mix /= max(1e-9, np.max(np.abs(mix))) / 0.89
out = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith('--') else 'audio.wav'
wavfile.write(out, SR, (mix.T * 32767).astype(np.int16))
print('wrote', out, mix.shape[1] / SR, 's')
