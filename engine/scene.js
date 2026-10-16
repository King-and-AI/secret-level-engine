'use strict';
const W = 1920, H = 1080;
const cv = document.getElementById('c');
const ctx = cv.getContext('2d');

const C = {
  pink: '#ff4f9a', cyan: '#36e2ff', yellow: '#ffd23f', lime: '#8dff6a', white: '#f5f7ff',
  muted: '#a3abdb', purple: '#a97cff', red: '#ff4d5e', orange: '#ffa53a', ink: '#14163d'
};

// ---------- cue sheet (absolute seconds) ----------
const CUE_DEFAULT = {
  h_title: 0.15, h_zzz: 1.3, h_quote: 1.8, h_attr: 2.0, h_skel: 3.3, h_glitch: 4.5, h_twist: 4.8, h_twist2: 5.5, B1: 7.6, l1_sign: 8.6, l1_row1: 9.1, l1_row2: 10.2, l1_cap1: 10.9, l1_label: 11.0, l1_eq1: 13.0, l1_eq2: 13.6, l1_cap2: 13.0, l1_step1: 13.0, l1_step2: 13.6, l1_step3: 14.4, l1_tags: 15.0, l1_cap3: 15.0, l1_tags2: 16.4, l1_xp: 17.4, B2: 19.2, g_title: 19.4, g_axes: 20.0, g_line1: 20.6, g_line2: 21.3, g_cap: 21.6, g_dot: 22.8, g_icons: 23.6, B3: 25.6, l2_title: 26.9, l2_cap1: 27.0, l2_ones: 27.4, l2_morph: 28.4, l2_labels: 29.8, l2_unk: 30.6, l2_cap2: 31.0, l2_chip: 31.4, l2_power: 33.8, l2_xp: 33.8, B4: 35.6, b_title: 37.1, b_food: 37.9, b_grow: 38.5, b_grow_end: 41.3, b_billions: 41.5, b_cap1: 41.6, b_partB: 43.6, b_card1: 43.9, b_card2: 45.7, b_pulse: 46.9, b_out: 48.0, b_cap2: 48.0, b_xp: 49.3, B5: 51.0, o_chip1: 51.3, o_chip2: 52.0, o_chip3: 52.7, o_yah: 53.4, o_big: 54.0, o_confirm: 55.8, o_done: 56.6, o_fade: 57.6, END: 58.2
};
// VARIANT=city turns on the optional city-skyline background (local flavour). Default: no skyline.
const LOCAL = window.VARIANT === 'city';

window.CUE = Object.assign({}, CUE_DEFAULT, window.CUE_OVERRIDE || {});
const K = () => window.CUE;

// ---------- math helpers ----------
const clamp = (x, a = 0, b = 1) => Math.max(a, Math.min(b, x));
const lerp = (a, b, t) => a + (b - a) * t;
const P = (t, a, b) => clamp((t - a) / (b - a));
const eOut = x => 1 - Math.pow(1 - x, 3);
const eIn = x => x * x * x;
const eInOut = x => x < .5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2;
const eBack = x => { const c1 = 1.9, c3 = c1 + 1; return 1 + c3 * Math.pow(x - 1, 3) + c1 * Math.pow(x - 1, 2); };
function hash(a, b = 0, c = 0) {
  let h = (Math.imul(a | 0, 374761393) + Math.imul(b | 0, 668265263) + Math.imul(c | 0, 1440662683)) | 0;
  h = Math.imul(h ^ (h >>> 13), 1274126177); h ^= h >>> 16;
  return (h >>> 0) / 4294967296;
}
function hex2rgb(h) { const n = parseInt(h.slice(1), 16); return [(n >> 16) & 255, (n >> 8) & 255, n & 255]; }
function rgba(h, a) { const [r, g, b] = hex2rgb(h); return `rgba(${r},${g},${b},${a})`; }
function mix(h1, h2, t) { const a = hex2rgb(h1), b = hex2rgb(h2); return `rgb(${a.map((v, i) => Math.round(lerp(v, b[i], t))).join(',')})`; }
function pop(t, t0, d = 0.4) {
  if (t < t0) return { a: 0, s: 0 };
  return { a: clamp((t - t0) / 0.1), s: eBack(P(t, t0, t0 + d)) };
}
const fout = (t, t1, d = 0.25) => 1 - P(t, t1, t1 + d);

// ---------- drawing helpers ----------
function F(size, weight = 700, fam = 'Fredoka', italic = false) { return `${italic ? 'italic ' : ''}${weight} ${size}px ${fam}`; }
function rr(x, y, w, h, r) {
  r = Math.min(r, w / 2, h / 2);
  ctx.beginPath(); ctx.moveTo(x + r, y); ctx.arcTo(x + w, y, x + w, y + h, r); ctx.arcTo(x + w, y + h, x, y + h, r);
  ctx.arcTo(x, y + h, x, y, r); ctx.arcTo(x, y, x + w, y, r); ctx.closePath();
}
function mw(s, o = {}) { ctx.save(); ctx.font = F(o.size || 48, o.weight || 700, o.fam || 'Fredoka', o.italic); ctx.letterSpacing = o.ls || '0px'; const w = ctx.measureText(s).width; ctx.restore(); return w; }
function txt(s, x, y, o = {}) {
  const a = o.alpha ?? 1; if (a <= 0.001) return;
  const sc = o.scale ?? 1; if (sc <= 0.001) return;
  ctx.save(); ctx.globalAlpha *= a; ctx.translate(x, y); if (o.rot) ctx.rotate(o.rot); ctx.scale(sc, sc);
  ctx.font = F(o.size || 48, o.weight || 700, o.fam || 'Fredoka', o.italic);
  ctx.letterSpacing = o.ls || '0px';
  ctx.textAlign = o.align || 'center'; ctx.textBaseline = 'middle';
  if (o.stroke) { ctx.lineWidth = o.stroke; ctx.strokeStyle = o.strokeColor || C.ink; ctx.lineJoin = 'round'; ctx.strokeText(s, 0, 0); }
  if (o.glow) { ctx.shadowColor = o.glowColor || o.color || '#fff'; ctx.shadowBlur = o.glow; }
  ctx.fillStyle = o.color || C.white; ctx.fillText(s, 0, 0);
  ctx.restore();
}
// segments: [[text,color],...]
function rich(segs, x, y, o = {}) {
  const a = o.alpha ?? 1; const sc = o.scale ?? 1;
  ctx.save(); ctx.font = F(o.size || 48, o.weight || 700, o.fam || 'Fredoka', o.italic); ctx.letterSpacing = o.ls || '0px';
  const ws = segs.map(s => ctx.measureText(s[0]).width); const tot = ws.reduce((p, q) => p + q, 0);
  if (a <= 0.001 || sc <= 0.001) { ctx.restore(); return tot; }
  ctx.globalAlpha *= a; ctx.translate(x, y); if (o.rot) ctx.rotate(o.rot); ctx.scale(sc, sc);
  ctx.textAlign = 'left'; ctx.textBaseline = 'middle';
  let sx = o.align === 'left' ? 0 : (o.align === 'right' ? -tot : -tot / 2);
  segs.forEach((s, i) => {
    if (o.stroke) { ctx.lineWidth = o.stroke; ctx.strokeStyle = o.strokeColor || C.ink; ctx.lineJoin = 'round'; ctx.strokeText(s[0], sx, 0); }
    if (o.glow) { ctx.shadowColor = s[1] || '#fff'; ctx.shadowBlur = o.glow; } else ctx.shadowBlur = 0;
    ctx.fillStyle = s[1] || C.white; ctx.fillText(s[0], sx, 0); sx += ws[i];
  });
  ctx.restore(); return tot;
}
function drawCheck(x, y, s, color, a = 1) {
  if (a <= 0 || s <= 0) return;
  ctx.save(); ctx.globalAlpha *= a; ctx.translate(x, y); ctx.scale(s, s);
  ctx.strokeStyle = color; ctx.lineWidth = 9; ctx.lineCap = 'round'; ctx.lineJoin = 'round';
  ctx.shadowColor = color; ctx.shadowBlur = 16;
  ctx.beginPath(); ctx.moveTo(-18, 0); ctx.lineTo(-5, 14); ctx.lineTo(20, -16); ctx.stroke(); ctx.restore();
}
function arrowR(x1, y, x2, color, prog = 1, a = 1) {
  if (prog <= 0) return;
  const xe = lerp(x1, x2, prog);
  ctx.save(); ctx.globalAlpha *= a; ctx.strokeStyle = color; ctx.fillStyle = color; ctx.lineWidth = 8; ctx.lineCap = 'round';
  ctx.beginPath(); ctx.moveTo(x1, y); ctx.lineTo(xe - 14, y); ctx.stroke();
  ctx.beginPath(); ctx.moveTo(xe + 6, y); ctx.lineTo(xe - 20, y - 18); ctx.lineTo(xe - 20, y + 18); ctx.closePath(); ctx.fill();
  ctx.restore();
}

// ---------- icons ----------
// drawChip: a smiling computer chip (example of an icon drawn in code). Emoji (Noto Color Emoji) work for quick extra objects.
function drawChip(x, y, s, a, t) {
  if (s <= 0.001 || a <= 0) return;
  ctx.save(); ctx.globalAlpha *= a; ctx.translate(x, y + Math.sin(t * 4) * 6); ctx.scale(s, s);
  ctx.fillStyle = '#9aa3d6';
  for (let i = -2; i <= 2; i++) { rr(i * 26 - 6, -104, 12, 22, 3); ctx.fill(); rr(i * 26 - 6, 82, 12, 22, 3); ctx.fill(); rr(-104, i * 26 - 6, 22, 12, 3); ctx.fill(); rr(82, i * 26 - 6, 22, 12, 3); ctx.fill(); }
  rr(-86, -86, 172, 172, 26); ctx.fillStyle = '#23265e'; ctx.fill(); ctx.lineWidth = 5; ctx.strokeStyle = C.cyan; ctx.shadowColor = C.cyan; ctx.shadowBlur = 20; ctx.stroke(); ctx.shadowBlur = 0;
  // heart eyes
  const heart = (hx, hy, r) => { ctx.beginPath(); ctx.moveTo(hx, hy + r * 0.9); ctx.bezierCurveTo(hx - r * 1.6, hy - r * 0.2, hx - r * 0.7, hy - r * 1.4, hx, hy - r * 0.5); ctx.bezierCurveTo(hx + r * 0.7, hy - r * 1.4, hx + r * 1.6, hy - r * 0.2, hx, hy + r * 0.9); ctx.fill(); };
  const beat = 1 + 0.12 * Math.max(0, Math.sin(t * 9));
  ctx.fillStyle = C.pink; ctx.save(); ctx.translate(-32, -18); ctx.scale(beat, beat); heart(0, 0, 18); ctx.restore();
  ctx.save(); ctx.translate(32, -18); ctx.scale(beat, beat); heart(0, 0, 18); ctx.restore();
  ctx.strokeStyle = C.white; ctx.lineWidth = 7; ctx.lineCap = 'round'; ctx.beginPath(); ctx.arc(0, 18, 26, 0.15 * Math.PI, 0.85 * Math.PI); ctx.stroke();
  ctx.restore();
}

// ---------- background ----------
const SYMS = ['·', '+', '✦', '·', '·', '+', '·', '✦'];
function bossTint(t) { const k = K(); return P(t, k.B4 - 0.2, k.B4 + 0.3) * (1 - P(t, k.B5 - 0.3, k.B5 + 0.2)); }
function bg(t) {
  const tint = bossTint(t);
  const g = ctx.createLinearGradient(0, 0, 0, H);
  g.addColorStop(0, mix('#0b0d29', '#22061a', tint)); g.addColorStop(1, mix('#1d1048', '#3a0a1c', tint));
  ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
  // glow blobs
  const blob = (bx, by, r, col, al) => { const rg = ctx.createRadialGradient(bx, by, 0, bx, by, r); rg.addColorStop(0, rgba(col, al)); rg.addColorStop(1, rgba(col, 0)); ctx.fillStyle = rg; ctx.fillRect(bx - r, by - r, 2 * r, 2 * r); };
  blob(400 + Math.sin(t * 0.4) * 200, 300 + Math.cos(t * 0.3) * 100, 700, tint > 0.5 ? '#ff2244' : '#ff4f9a', 0.10 + 0.05 * tint);
  blob(1500 + Math.cos(t * 0.35) * 200, 800 + Math.sin(t * 0.25) * 100, 750, tint > 0.5 ? '#ff7a2a' : '#36e2ff', 0.08);
  // grid
  ctx.strokeStyle = rgba(tint > 0.5 ? '#ff8c96' : '#8c96ff', 0.06); ctx.lineWidth = 1.5;
  const s = 80, ox = (t * 18) % s, oy = (t * 10) % s;
  ctx.beginPath();
  for (let x = -s + ox; x < W + s; x += s) { ctx.moveTo(x, 0); ctx.lineTo(x, H); }
  for (let y = -s + oy; y < H + s; y += s) { ctx.moveTo(0, y); ctx.lineTo(W, y); }
  ctx.stroke();
  // floating symbols
  for (let i = 0; i < 22; i++) {
    const sp = 12 + hash(i, 1) * 22;
    const x = ((hash(i, 2) * (W + 300) + t * sp) % (W + 300)) - 150;
    const y = ((((hash(i, 3) * (H + 200) - t * (6 + hash(i, 4) * 10)) % (H + 200)) + H + 200) % (H + 200)) - 100;
    txt(SYMS[i % SYMS.length], x, y, { size: 30 + hash(i, 5) * 50, fam: 'JBM', weight: 700, color: '#c8cdff', alpha: 0.07, rot: (hash(i, 6) - 0.5) * 0.6 });
  }
  if (LOCAL) skyline(t, tint);
  // vignette
  const vg = ctx.createRadialGradient(W / 2, H / 2, 400, W / 2, H / 2, 1200);
  vg.addColorStop(0, 'rgba(0,0,0,0)'); vg.addColorStop(1, 'rgba(0,0,0,0.55)');
  ctx.fillStyle = vg; ctx.fillRect(0, 0, W, H);
  if (tint > 0) {
    const pulse = 0.5 + 0.5 * Math.sin(t * 7);
    const rv = ctx.createRadialGradient(W / 2, H / 2, 450, W / 2, H / 2, 1150);
    rv.addColorStop(0, 'rgba(255,40,60,0)'); rv.addColorStop(1, `rgba(255,40,60,${0.22 * tint * (0.5 + 0.5 * pulse)})`);
    ctx.fillStyle = rv; ctx.fillRect(0, 0, W, H);
  }
}

// ---------- city skyline (optional local flavour: housing blocks with an open ground floor) ----------
function skyline(t, tint) {
  const scroll = (t * 7) % 150;
  const body = tint > 0.5 ? 'rgba(70,20,40,0.55)' : 'rgba(36,38,92,0.55)';
  for (let i = -1; i < 15; i++) {
    const id = i + Math.floor(t * 7 / 150) * 0; // stable ids
    const bw = 110 + hash(i, 21) * 70, bh = 120 + hash(i, 22) * 170;
    const x = i * 150 - scroll + (hash(i, 23) - 0.5) * 30, y = H - bh;
    ctx.fillStyle = body; ctx.fillRect(x, y, bw, bh);
    // roof detail
    ctx.fillRect(x + bw * 0.3, y - 14, bw * 0.25, 14);
    // open ground floor with pillars
    ctx.fillStyle = 'rgba(8,8,24,0.55)'; ctx.fillRect(x, H - 22, bw, 22);
    ctx.fillStyle = body; for (let p = 0; p <= 4; p++) ctx.fillRect(x + p * (bw - 8) / 4, H - 22, 8, 22);
    // windows
    for (let r = 0; y + 12 + r * 16 < H - 30; r++) for (let c = 0; 10 + c * 16 < bw - 6; c++) {
      const lit = hash(i * 50 + c, r, 9) > 0.62;
      ctx.fillStyle = lit ? `rgba(255,214,130,${0.28 + 0.12 * Math.sin(t * 0.7 + r + c)})` : 'rgba(10,10,30,0.35)';
      ctx.fillRect(x + 10 + c * 16, y + 12 + r * 16, 8, 6);
    }
  }
}

// ---------- shake ----------
function shake(t) {
  const k = K();
  const imp = [[k.h_glitch, 12], [k.h_twist, 8], [k.B1 + 0.03, 12], [k.B3 + 0.03, 12], [k.B4 + 0.03, 16], [k.b_billions, 20], [k.o_big, 9]];
  let sx = 0, sy = 0;
  for (const [ti, amp] of imp) {
    const d = t - ti; if (d < 0 || d > 0.6) continue;
    const e = amp * Math.exp(-d * 9); const f = Math.floor(t * 60);
    sx += (hash(f, 11) - 0.5) * 2 * e; sy += (hash(f, 12) - 0.5) * 2 * e;
  }
  return [sx, sy];
}

// ---------- caption ----------
function caption(t, t0, t1, segs, accent = C.cyan) {
  if (t < t0 || t > t1 + 0.2) return;
  const ain = eOut(P(t, t0, t0 + 0.22)), aout = 1 - P(t, t1, t1 + 0.18);
  const a = ain * aout; if (a <= 0) return;
  const size = 50;
  const tw = rich(segs, -9999, -9999, { size, fam: 'Nunito', weight: 900, alpha: 0 });
  const w = tw + 90, h = 96, x = W / 2 - w / 2, y = 960 - h / 2 + (1 - ain) * 24;
  ctx.save(); ctx.globalAlpha *= a;
  rr(x, y, w, h, 48); ctx.fillStyle = 'rgba(12,12,40,0.88)'; ctx.fill();
  ctx.lineWidth = 3; ctx.strokeStyle = rgba(accent, 0.9); ctx.stroke();
  ctx.restore();
  rich(segs, W / 2, y + h / 2 + 2, { size, fam: 'Nunito', weight: 900, alpha: a });
}

// ---------- level banner ----------
function banner(t, t0, big, sub, color) {
  const p = t - t0; if (p < 0 || p > 1.4) return;
  const sIn = p < 0.28 ? lerp(2.8, 1, eOut(p / 0.28)) : 1;
  const out = P(p, 1.05, 1.35);
  const a = clamp(p / 0.08) * (1 - out);
  const sc = sIn * (1 - 0.25 * eInOut(out));
  // band
  ctx.save(); ctx.globalAlpha *= a;
  ctx.fillStyle = 'rgba(8,8,30,0.75)'; ctx.fillRect(0, 380, W, 320);
  ctx.fillStyle = color; ctx.fillRect(0, 376, W * eOut(P(p, 0.2, 0.5)), 6); ctx.fillRect(W - W * eOut(P(p, 0.2, 0.5)), 698, W * eOut(P(p, 0.2, 0.5)), 6);
  ctx.restore();
  // sparks
  if (p > 0.28) {
    const q = P(p, 0.28, 0.9);
    ctx.save(); ctx.globalAlpha *= (1 - q) * a; ctx.strokeStyle = color; ctx.lineWidth = 6; ctx.lineCap = 'round';
    for (let i = 0; i < 16; i++) {
      const ang = i / 16 * Math.PI * 2 + 0.2; const r1 = 260 + q * 520, r2 = r1 + 60 * (1 - q);
      ctx.beginPath(); ctx.moveTo(W / 2 + Math.cos(ang) * r1 * 1.4, 520 + Math.sin(ang) * r1 * 0.7); ctx.lineTo(W / 2 + Math.cos(ang) * r2 * 1.4, 520 + Math.sin(ang) * r2 * 0.7); ctx.stroke();
    }
    ctx.restore();
  }
  txt(big, W / 2, 505, { size: 190, weight: 700, color, scale: sc, alpha: a, glow: 45, ls: '6px' });
  const ps = P(p, 0.25, 0.45);
  txt(sub, W / 2 + (1 - eOut(ps)) * 120, 640, { size: 54, fam: 'Nunito', weight: 900, color: C.white, alpha: a * ps, ls: '10px' });
}

// ---------- HUD ----------
function xpValue(t) {
  const k = K();
  let v = 0;
  v += 0.34 * eInOut(P(t, k.l1_xp, k.l1_xp + 0.6));
  v += 0.33 * eInOut(P(t, k.l2_xp, k.l2_xp + 0.6));
  v += 0.33 * eInOut(P(t, k.b_xp, k.b_xp + 0.6));
  return v;
}
function hud(t) {
  const k = K();
  let a = P(t, k.B1 + 1.1, k.B1 + 1.4) * (1 - P(t, k.B5 - 0.4, k.B5));
  const hide = (b) => 1 - P(t, b - 0.35, b - 0.15) * (1 - P(t, b + 1.1, b + 1.4));
  a *= hide(k.B3) * hide(k.B4);
  if (a <= 0) return;
  let label, col;
  if (t < k.B3) { label = LABELS.hud1; col = C.cyan; }
  else if (t < k.B4) { label = LABELS.hud2; col = C.purple; }
  else { label = LABELS.hud3; col = C.red; }
  ctx.save(); ctx.globalAlpha *= a;
  const w = mw(label, { size: 30, weight: 600, ls: '3px' }) + 90;
  rr(50, 38, w, 62, 31); ctx.fillStyle = 'rgba(10,10,36,0.8)'; ctx.fill(); ctx.lineWidth = 3; ctx.strokeStyle = col; ctx.stroke();
  ctx.fillStyle = col; ctx.shadowColor = col; ctx.shadowBlur = 14; ctx.beginPath(); ctx.arc(84, 69, 10, 0, Math.PI * 2); ctx.fill(); ctx.shadowBlur = 0;
  txt(label, 108, 70, { size: 30, weight: 600, align: 'left', color: C.white, ls: '3px' });
  // XP bar
  const v = xpValue(t);
  txt('XP', 1345, 70, { size: 34, weight: 700, color: C.yellow, align: 'right' });
  rr(1365, 55, 500, 30, 15); ctx.fillStyle = 'rgba(10,10,36,0.85)'; ctx.fill(); ctx.lineWidth = 3; ctx.strokeStyle = 'rgba(255,255,255,0.35)'; ctx.stroke();
  if (v > 0.001) {
    const g = ctx.createLinearGradient(1365, 0, 1865, 0); g.addColorStop(0, C.cyan); g.addColorStop(0.5, C.purple); g.addColorStop(1, C.pink);
    rr(1369, 59, Math.max(22, 492 * v), 22, 11); ctx.fillStyle = g; ctx.shadowColor = C.pink; ctx.shadowBlur = 16; ctx.fill(); ctx.shadowBlur = 0;
  }
  ctx.fillStyle = 'rgba(255,255,255,0.4)'; [0.34, 0.67].forEach(m => ctx.fillRect(1365 + 500 * m, 55, 3, 30));
  ctx.restore();
  // XP floaters
  const fl = (t0, s) => { const q = P(t, t0, t0 + 1.4); if (t < t0 || q >= 1) return; txt(s, 1615, 165 - 35 * eOut(q), { size: 44, weight: 700, color: C.lime, alpha: a * (q < 0.15 ? q / 0.15 : 1 - P(q, 0.7, 1)), glow: 20, scale: eBack(P(t, t0, t0 + 0.3)) }); };
  fl(k.l1_xp, LABELS.xp1); fl(k.l2_xp, LABELS.xp2); fl(k.b_xp, LABELS.xp3);
}

// ---------- card (rounded panel behind text) ----------
function card(x, y, w, h, col, a, s) {
  if (a <= 0) return;
  ctx.save(); ctx.globalAlpha *= a; ctx.translate(x, y); ctx.scale(s, s);
  rr(-w / 2, -h / 2, w, h, 26); ctx.fillStyle = 'rgba(12,12,40,0.9)'; ctx.fill(); ctx.lineWidth = 4; ctx.strokeStyle = col; ctx.stroke(); ctx.restore();
}

// ---------- wipes ----------
const WD = 0.3, HW = 1300, SL = 250;
function bandX(t, B) { const p = P(t, B - WD, B + WD); return lerp(-1400, W + 1400, eInOut(p)); }
function clipLeft(cx) { ctx.beginPath(); ctx.moveTo(-200, -200); ctx.lineTo(cx + SL + 40, -200); ctx.lineTo(cx - SL - 40, H + 200); ctx.lineTo(-200, H + 200); ctx.closePath(); ctx.clip(); }
function clipRight(cx) { ctx.beginPath(); ctx.moveTo(cx + SL + 40, -200); ctx.lineTo(W + 200, -200); ctx.lineTo(W + 200, H + 200); ctx.lineTo(cx - SL - 40, H + 200); ctx.closePath(); ctx.clip(); }
function drawWipes(t) {
  const k = K();
  for (const B of [k.B1, k.B2, k.B3, k.B4, k.B5]) {
    if (Math.abs(t - B) >= WD) continue;
    const cx = bandX(t, B);
    ctx.save();
    ctx.beginPath(); ctx.moveTo(cx - HW + SL, 0); ctx.lineTo(cx + HW + SL, 0); ctx.lineTo(cx + HW - SL, H); ctx.lineTo(cx - HW - SL, H); ctx.closePath();
    const g = ctx.createLinearGradient(cx - HW, 0, cx + HW, 0);
    g.addColorStop(0, '#36e2ff'); g.addColorStop(0.45, '#a97cff'); g.addColorStop(1, '#ff4f9a');
    ctx.fillStyle = g; ctx.fill();
    ctx.clip();
    ctx.strokeStyle = 'rgba(255,255,255,0.35)'; ctx.lineWidth = 26;
    for (let i = -6; i <= 6; i++) { const ox = cx + i * 190; ctx.beginPath(); ctx.moveTo(ox + SL, 0); ctx.lineTo(ox - SL, H); ctx.stroke(); }
    ctx.restore();
  }
}

// =====================================================================
// ===== END OF ENGINE CORE. Everything below is the TOPIC PART. =====
// For a new video: keep everything above, replace LABELS, CUE_DEFAULT
// (at the top) and the scene functions s0..s5 below. Keep the cue NAMES:
// audio.py keys its music and sound effects to them (see docs/CUES.md).
// Worked example below: "How do thousands of satellites avoid crashing?"
// =====================================================================
const LABELS = {
  hud1: 'LEVEL 1 · FLY LOW', hud2: 'LEVEL 2 · GET OUT OF THE WAY', hud3: 'BOSS LEVEL · LEAVE NOTHING BEHIND',
  xp1: 'Steady! +100 XP', xp2: 'Power! +100 XP', xp3: '+1,000 XP',
};
function stars(t) {
  for (let i = 0; i < 140; i++) {
    const x = hash(i, 71) * W, y = hash(i, 72) * H, r = 0.8 + hash(i, 73) * 2.2;
    ctx.fillStyle = `rgba(255,255,255,${0.25 + 0.35 * (0.5 + 0.5 * Math.sin(t * (1 + hash(i, 74) * 3) + i))})`;
    ctx.beginPath(); ctx.arc(x, y, r, 0, Math.PI * 2); ctx.fill();
  }
}
// satellite: body + two solar panels
function sat(x, y, s = 1, rot = 0, a = 1, col = C.cyan) {
  if (s <= 0.001 || a <= 0) return;
  ctx.save(); ctx.globalAlpha *= a; ctx.translate(x, y); ctx.rotate(rot); ctx.scale(s, s);
  for (const sx of [-1, 1]) {
    rr(sx > 0 ? 34 : -114, -26, 80, 52, 6); ctx.fillStyle = '#2a4fbf'; ctx.fill(); ctx.lineWidth = 3; ctx.strokeStyle = '#9fc3ff'; ctx.stroke();
    ctx.strokeStyle = 'rgba(159,195,255,0.5)'; ctx.lineWidth = 2;
    for (let i = 1; i < 4; i++) { const px = (sx > 0 ? 34 : -114) + i * 20; ctx.beginPath(); ctx.moveTo(px, -26); ctx.lineTo(px, 26); ctx.stroke(); }
    ctx.fillStyle = '#c8cdff'; ctx.fillRect(sx > 0 ? 24 : -34, -4, 10, 8);
  }
  rr(-26, -30, 52, 60, 10); ctx.fillStyle = '#e8ebff'; ctx.fill(); ctx.lineWidth = 4; ctx.strokeStyle = col; ctx.shadowColor = col; ctx.shadowBlur = 18; ctx.stroke(); ctx.shadowBlur = 0;
  ctx.fillStyle = col; ctx.beginPath(); ctx.arc(0, 0, 9, 0, Math.PI * 2); ctx.fill();
  ctx.restore();
}
// Earth seen as a big curve at the bottom
const EX = 960, EY = 2350, ER = 1600;
function earth(a = 1) {
  ctx.save(); ctx.globalAlpha *= a;
  const g = ctx.createRadialGradient(EX, EY, ER - 200, EX, EY, ER + 60);
  g.addColorStop(0, '#1b6fd1'); g.addColorStop(0.9, '#2f9cf0'); g.addColorStop(1, 'rgba(120,200,255,0)');
  ctx.fillStyle = g; ctx.beginPath(); ctx.arc(EX, EY, ER + 60, 0, Math.PI * 2); ctx.fill();
  ctx.fillStyle = '#1e64c8'; ctx.beginPath(); ctx.arc(EX, EY, ER, 0, Math.PI * 2); ctx.fill();
  ctx.save(); ctx.beginPath(); ctx.arc(EX, EY, ER, 0, Math.PI * 2); ctx.clip();
  ctx.fillStyle = '#3fae5a';
  [[500, 830, 220, 60], [1300, 810, 260, 70], [900, 900, 180, 50], [1700, 900, 160, 60], [150, 920, 140, 50]].forEach(([x, y, w, h]) => { ctx.beginPath(); ctx.ellipse(x, y, w, h, 0.1, 0, Math.PI * 2); ctx.fill(); });
  ctx.restore();
  ctx.restore();
}
function orbitArc(r, col, a, dash = null, lw = 4) {
  ctx.save(); ctx.globalAlpha *= a; ctx.strokeStyle = col; ctx.lineWidth = lw; if (dash) ctx.setLineDash(dash);
  ctx.beginPath(); ctx.arc(EX, EY, r, Math.PI * 1.12, Math.PI * 1.88); ctx.stroke(); ctx.restore();
}
function onArc(r, ang) { return [EX + Math.cos(ang) * r, EY + Math.sin(ang) * r]; }
function fire(x, y, s, a, t) {
  if (a <= 0 || s <= 0) return;
  ctx.save(); ctx.globalAlpha *= a; ctx.translate(x, y); ctx.scale(s, s);
  for (let i = 0; i < 3; i++) {
    const r = [90, 62, 36][i], col = ['#ff5a2a', '#ffa53a', '#fff1a8'][i];
    ctx.fillStyle = col; ctx.shadowColor = col; ctx.shadowBlur = 40;
    ctx.beginPath(); ctx.moveTo(0, -r * 2.2 - Math.sin(t * 20 + i) * 12);
    ctx.quadraticCurveTo(r, -r * 0.6, r * 0.8, 0); ctx.arc(0, 0, r * 0.8, 0, Math.PI); ctx.quadraticCurveTo(-r, -r * 0.6, 0, -r * 2.2 - Math.sin(t * 20 + i) * 12); ctx.fill();
  }
  ctx.restore();
}

// ---------- scene 0 : hook ----------
function s0(t) {
  const k = K();
  stars(t);
  const tp = pop(t, k.h_title, 0.5);
  const up = eInOut(P(t, k.h_quote - 0.2, k.h_quote + 0.3));
  txt('STARLINK SPACE SAFETY', 960, lerp(380, 150, up), { size: lerp(120, 70, up), weight: 700, color: C.cyan, glow: 30, scale: tp.s, alpha: tp.a, ls: '4px' });
  const zp = pop(t, k.h_zzz, 0.4);
  txt('Thousands of satellites. One sky.', 960, lerp(520, 250, up), { size: lerp(60, 46, up), fam: 'Nunito', weight: 800, color: C.white, alpha: zp.a * (1 - P(t, k.h_quote - 0.2, k.h_quote)) });
  const q = pop(t, k.h_quote, 0.4);
  rich([['"Won\'t they ', C.white], ['CRASH', C.pink], [' into each other?"', C.white]], 960, 300, { size: 72, scale: q.s, alpha: q.a * fout(t, k.h_twist - 0.1), glow: 8 });
  // gag: two satellites drift toward each other
  const d = P(t, k.h_quote, k.h_skel + 0.9);
  const bonk = t > k.h_skel + 0.9;
  const fa = fout(t, k.h_twist - 0.1);
  sat(lerp(300, 840, eIn(d)), 620, 1.2, bonk ? -0.5 : 0.1, fa * q.a, C.cyan);
  sat(lerp(1620, 1080, eIn(d)), 620, 1.2, bonk ? 0.5 : -0.1, fa * q.a, C.pink);
  if (t > k.h_skel - 0.2 && !bonk) txt('😬', 960, 470, { size: 80, alpha: fa });
  if (bonk) txt('BONK?!', 960, 470, { size: 90, weight: 700, color: C.yellow, alpha: fa, scale: eBack(P(t, k.h_skel + 0.9, k.h_skel + 1.2)), glow: 20 });
  const tw = pop(t, k.h_twist, 0.4);
  txt('Plot twist:', 960, 430, { size: 110, weight: 700, color: C.yellow, scale: tw.s, alpha: tw.a, glow: 25 });
  const t2 = pop(t, k.h_twist2, 0.4);
  rich([['they follow ', C.white], ['3 RULES', C.lime], ['.', C.white]], 960, 600, { size: 96, scale: t2.s, alpha: t2.a, glow: 10 });
}

// ---------- scene 1 : level 1 fly low ----------
function s1(t) {
  const k = K();
  stars(t); earth(1);
  banner(t, k.B1 + 0.03, 'LEVEL 1', 'RULE 1: FLY LOW', C.cyan);
  const R = ER + 420;  // the "below 600 km" shell, drawn not to scale
  const oa = P(t, k.l1_row1, k.l1_row1 + 0.4);
  orbitArc(R, C.cyan, oa * 0.9, [18, 14], 5);
  const lp_ = pop(t, k.l1_row1 + 0.1, 0.4);
  rich([['Starlink orbits ', C.white], ['below 600 km', C.cyan]], 960, 640, { size: 54, scale: lp_.s, alpha: lp_.a * fout(t, k.l1_step1 - 0.2), fam: 'Nunito', weight: 900 });
  // satellite moving on orbit, then falling
  const ang0 = Math.PI * 1.3 + (t - k.B1) * 0.03;
  let r = R, rot = 0, col = C.cyan;
  if (t > k.l1_step1) { col = C.muted; }
  const fall = eIn(P(t, k.l1_step2, k.l1_step3 + 0.4));
  r = lerp(R, ER + 40, fall);
  const [sx, sy] = onArc(r, ang0);
  const sa = P(t, k.l1_row1, k.l1_row1 + 0.3) * (1 - P(t, k.l1_step3 + 0.2, k.l1_step3 + 0.5));
  sat(sx, sy, 0.8, ang0 + Math.PI / 2 + fall * 2, sa, col);
  // drag arrows (thin air)
  const da = P(t, k.l1_row2, k.l1_row2 + 0.3) * fout(t, k.l1_tags - 0.2);
  if (da > 0) for (let i = 0; i < 3; i++) {
    const ph = ((t * 1.2 + i / 3) % 1);
    ctx.save(); ctx.globalAlpha *= da * (1 - ph); ctx.strokeStyle = C.white; ctx.lineWidth = 4; ctx.lineCap = 'round';
    ctx.beginPath(); ctx.moveTo(sx + 60 + ph * 80, sy - 20 + i * 20); ctx.lineTo(sx + 120 + ph * 80, sy - 20 + i * 20); ctx.stroke(); ctx.restore();
  }
  caption(t, k.l1_cap1, k.l1_step1 - 0.05, [['Up there, ', C.white], ['thin air', C.cyan], [' still drags satellites down.', C.white]]);
  caption(t, k.l1_step1, k.l1_tags - 0.05, [['If a satellite ', C.white], ['breaks', C.pink], ['… it sinks…', C.white]], C.pink);
  if (t > k.l1_step3 && t < k.l1_tags + 0.3) txt('🔥', sx, sy - 20, { size: 70, alpha: 1 - P(t, k.l1_step3 + 0.4, k.l1_tags + 0.3) });
  const tg = pop(t, k.l1_tags, 0.45);
  card(960, 330, 1040, 230, C.lime, tg.a, tg.s);
  txt('Gone in 5 years or less', 960, 300, { size: 76, weight: 700, color: C.lime, alpha: tg.a, scale: tg.s, glow: 14 });
  txt('even if nobody steers it', 960, 380, { size: 42, fam: 'Nunito', weight: 800, color: C.white, alpha: tg.a, scale: tg.s });
  caption(t, k.l1_cap3, k.l1_tags2 - 0.05, [['Low orbits ', C.white], ['clean themselves', C.lime], ['.', C.white]], C.lime);
  caption(t, k.l1_tags2, k.B2 - 0.3, [['No dead junk ', C.white], ['circling forever', C.yellow], ['. ', C.white], ['Steady!', C.lime]], C.lime);
  txt('Not to scale', 1820, 1050, { size: 24, fam: 'Nunito', weight: 700, color: C.muted, align: 'right', alpha: 0.8 });
}

// ---------- scene 2 : the picture (ephemeris) ----------
function s2(t) {
  const k = K();
  stars(t);
  const tp = pop(t, k.g_title, 0.4);
  rich([['Every satellite has a ', C.white], ['forecast', C.yellow], [' of where it will be', C.white]], 960, 170, { size: 60, scale: tp.s, alpha: tp.a });
  const ax = P(t, k.g_axes, k.g_axes + 0.3);
  // two paths that cross
  const path = (x1, y1, x2, y2, prog, col) => {
    if (prog <= 0) return;
    ctx.save(); ctx.strokeStyle = col; ctx.lineWidth = 6; ctx.setLineDash([20, 16]); ctx.lineDashOffset = -t * 60;
    ctx.beginPath(); ctx.moveTo(x1, y1); ctx.lineTo(lerp(x1, x2, prog), lerp(y1, y2, prog)); ctx.stroke(); ctx.restore();
  };
  path(420, 360, 1500, 820, eOut(P(t, k.g_line1, k.g_line1 + 0.6)), C.cyan);
  path(420, 820, 1500, 360, eOut(P(t, k.g_line2, k.g_line2 + 0.6)), C.pink);
  sat(330, 320, 0.9, 0.4, ax, C.cyan);
  sat(330, 860, 0.9, -0.4, ax, C.pink);
  if (t > k.g_dot) {
    const p = pop(t, k.g_dot, 0.4); const blink = 0.6 + 0.4 * Math.sin(t * 14);
    ctx.save(); ctx.globalAlpha *= p.a * blink; ctx.strokeStyle = C.red; ctx.lineWidth = 8; ctx.beginPath(); ctx.arc(960, 590, 60 * p.s, 0, Math.PI * 2); ctx.stroke(); ctx.restore();
    txt('⚠ paths cross', 960, 490, { size: 48, weight: 700, color: C.red, alpha: p.a, scale: p.s });
  }
  caption(t, k.g_cap, k.g_icons - 0.05, [['That forecast is called an ', C.white], ['EPHEMERIS', C.yellow]], C.yellow);
  caption(t, k.g_icons, k.B3 - 0.3, [['Starlink ', C.white], ['shares', C.lime], [' its forecasts publicly', C.white]], C.lime);
}

// ---------- scene 3 : level 2 dodge ----------
function s3(t) {
  const k = K();
  stars(t);
  banner(t, k.B3 + 0.03, 'LEVEL 2', 'RULE 2: GET OUT OF THE WAY', C.purple);
  const ap = P(t, k.l2_title - 0.3, k.l2_title);
  // repeat the crossing picture
  ctx.save(); ctx.globalAlpha *= ap * 0.5; ctx.setLineDash([20, 16]); ctx.lineWidth = 6;
  ctx.strokeStyle = C.pink; ctx.beginPath(); ctx.moveTo(420, 820); ctx.lineTo(1500, 360); ctx.stroke();
  ctx.restore();
  const mv = eInOut(P(t, k.l2_morph, k.l2_morph + 1.0));
  // cyan satellite's path bends up (dodge)
  ctx.save(); ctx.globalAlpha *= ap; ctx.setLineDash([20, 16]); ctx.lineDashOffset = -t * 60; ctx.lineWidth = 6; ctx.strokeStyle = C.cyan;
  ctx.beginPath(); ctx.moveTo(420, 360); ctx.quadraticCurveTo(960, lerp(590, 220, mv) * 2 - 590, 1500, lerp(820, 600, mv)); ctx.stroke(); ctx.restore();
  const along = P(t, k.l2_ones, k.l2_labels + 0.6);
  const bx = (u) => { const a = 420, c = 1500, cy = lerp(590, 220, mv) * 2 - 590, ey = lerp(820, 600, mv); return [(1 - u) * (1 - u) * a + 2 * u * (1 - u) * 960 + u * u * c, (1 - u) * (1 - u) * 360 + 2 * u * (1 - u) * cy + u * u * ey]; };
  const [cx, cy] = bx(lerp(0.05, 0.75, along));
  sat(cx, cy, 0.85, 0.2, ap, C.cyan);
  if (t > k.l2_morph && t < k.l2_morph + 1.0) txt('🔥', cx - 90, cy + 10, { size: 50 });
  sat(lerp(500, 1150, along), lerp(786, 510, along), 0.85, -0.3, ap, C.pink);
  const wp = pop(t, k.l2_ones, 0.3);
  if (t < k.l2_morph + 0.2) txt('⚠ CLOSE CALL', 960, 250, { size: 64, weight: 700, color: C.red, alpha: wp.a * (0.6 + 0.4 * Math.sin(t * 14)), scale: wp.s });
  const lb = pop(t, k.l2_labels, 0.4);
  txt('✓ Dodged', 1400, 760, { size: 70, weight: 700, color: C.lime, alpha: lb.a * fout(t, Math.min(k.l2_cap2, k.l2_unk) - 0.1), scale: lb.s, glow: 14 });
  caption(t, k.l2_cap1, Math.min(k.l2_cap2, k.l2_unk) - 0.05, [['Forecasts cross? Its ', C.white], ['thrusters', C.cyan], [' steer it clear.', C.white]], C.purple);
  // Stargaze eyes
  const sp = pop(t, k.l2_unk, 0.4);
  card(960, 470, 1180, 300, C.yellow, sp.a, sp.s);
  txt('STARGAZE', 960, 390, { size: 74, weight: 700, color: C.yellow, alpha: sp.a, scale: sp.s, ls: '6px', glow: 14 });
  txt('30,000 sensors on Starlink', 960, 475, { size: 54, fam: 'Nunito', weight: 900, color: C.white, alpha: sp.a, scale: sp.s });
  txt('watch for other objects up there', 960, 545, { size: 44, fam: 'Nunito', weight: 800, color: C.muted, alpha: sp.a, scale: sp.s });
  caption(t, k.l2_cap2, k.B4 - 0.3, [['Spot it, ', C.white], ['share it', C.yellow], [', dodge it. ', C.white], ['Power!', C.lime]], C.yellow);
}

// ---------- scene 4 : boss ----------
function s4(t) {
  const k = K();
  stars(t); earth(1);
  banner(t, k.B4 + 0.03, 'BOSS LEVEL', 'RULE 3: LEAVE NOTHING BEHIND', C.red);
  const tp = pop(t, k.b_title, 0.4);
  rich([['Old satellite? ', C.white], ['Deorbit', C.orange], [' it: steer it down on purpose.', C.white]], 960, 170, { size: 54, scale: tp.s, alpha: tp.a * fout(t, k.b_partB - 0.2), fam: 'Nunito', weight: 900 });
  const R = ER + 420;
  const fall = eIn(P(t, k.b_grow, k.b_billions));
  const ang = Math.PI * 1.40 + fall * 0.15;
  const [sx, sy] = onArc(lerp(R, ER + 60, fall), ang);
  orbitArc(R, C.cyan, P(t, k.b_food - 0.3, k.b_food) * 0.6 * fout(t, k.b_partB - 0.2), [18, 14], 5);
  const alive = 1 - P(t, k.b_billions, k.b_billions + 0.25);
  // trail
  if (t > k.b_grow) for (let i = 1; i < 14; i++) {
    const f2 = Math.max(0, fall - i * 0.03); const [tx, ty] = onArc(lerp(R, ER + 60, f2), Math.PI * 1.40 + f2 * 0.15);
    ctx.fillStyle = rgba(C.orange, 0.5 * (1 - i / 14) * fout(t, k.b_partB - 0.2)); ctx.beginPath(); ctx.arc(tx, ty, 10 - i * 0.5, 0, Math.PI * 2); ctx.fill();
  }
  sat(sx, sy, 0.8, ang + Math.PI / 2, P(t, k.b_food, k.b_food + 0.3) * alive, mix(C.cyan, C.orange, fall));
  fire(sx, sy, 0.6 + 0.6 * P(t, k.b_billions - 0.8, k.b_billions), P(t, k.b_billions - 1.2, k.b_billions) * fout(t, k.b_billions + 1.2, 0.5), t);
  const bp = pop(t, k.b_billions, 0.45);
  txt('BURN UP!', 960, 400, { size: 150, weight: 700, color: C.orange, alpha: bp.a * fout(t, k.b_partB - 0.2), scale: bp.s, glow: 40 });
  caption(t, k.b_cap1, k.b_partB - 0.05, [['Built to ', C.white], ['burn up', C.orange], [' in the air on the way down', C.white]], C.orange);
  const c1 = pop(t, k.b_card1, 0.4), c2 = pop(t, k.b_card2, 0.4);
  card(960, 330, 1100, 140, C.cyan, c1.a, c1.s);
  txt('🌊  Aimed over open ocean', 960, 333, { size: 60, weight: 700, color: C.cyan, alpha: c1.a, scale: c1.s });
  card(960, 530, 1100, 140, C.yellow, c2.a, c2.s);
  txt('🛠  Brought down early if a part might fail', 960, 533, { size: 50, weight: 700, color: C.yellow, alpha: c2.a, scale: c2.s });
  caption(t, k.b_cap2, k.B5 - 0.3, [['Safe out there ', C.white], ['and', C.pink], [' on the way down.', C.white]], C.red);
}

// ---------- scene 5 : outro ----------
function s5(t) {
  const k = K();
  stars(t);
  if (t >= k.o_done) {
    const d = t - k.o_done; const cols = [C.pink, C.cyan, C.yellow, C.lime, C.purple];
    for (let i = 0; i < 110; i++) {
      const ang = -Math.PI / 2 + (hash(i, 1) - 0.5) * 2.4; const sp = 700 + hash(i, 2) * 900;
      const px = 960 + Math.cos(ang) * sp * d * 0.9 + Math.sin(d * 3 + i) * 20;
      const py = 870 + Math.sin(ang) * sp * d + 900 * d * d;
      if (py > H + 40) continue;
      ctx.save(); ctx.translate(px, py); ctx.rotate(d * (4 + hash(i, 3) * 8) + i); ctx.fillStyle = cols[i % 5]; ctx.fillRect(-9, -5, 18, 10); ctx.restore();
    }
  }
  const chips = [['Fly low', C.cyan, k.o_chip1], ['Get out of the way', C.purple, k.o_chip2], ['Leave nothing behind', C.orange, k.o_chip3]];
  const ws = chips.map(c => mw(c[0], { size: 46, weight: 600 }) + 70);
  const gap = 100; const tot = ws.reduce((a, b) => a + b, 0) + gap * 2;
  let x = 960 - tot / 2; const y = 330; const xs = [];
  chips.forEach(([s, col, t0], i) => {
    const p = pop(t, t0, 0.4); const w = ws[i]; xs.push([x, w]);
    ctx.save(); ctx.globalAlpha *= p.a; ctx.translate(x + w / 2, y); ctx.scale(p.s, p.s);
    rr(-w / 2, -48, w, 96, 48); ctx.fillStyle = col; ctx.shadowColor = col; ctx.shadowBlur = 30; ctx.fill(); ctx.restore();
    txt(s, x + w / 2, y + 3, { size: 46, weight: 600, color: C.ink, scale: p.s, alpha: p.a });
    if (i < 2) arrowR(x + w + 18, y, x + w + gap - 18, C.white, eOut(P(t, chips[i + 1][2] - 0.25, chips[i + 1][2])), 1);
    x += w + gap;
  });
  const ya = P(t, k.o_yah, k.o_yah + 0.25);
  txt('3 RULES  ·  ALL UNLOCKED', 960, 450, { size: 40, fam: 'Nunito', weight: 900, color: C.yellow, alpha: ya, ls: '5px' });
  const bp = pop(t, k.o_big, 0.45);
  rich([['A safe sky is a ', C.white], ['shared', C.pink], [' sky.', C.white]], 800, 640, { size: 96, scale: bp.s, alpha: bp.a, glow: 10 });
  if (t >= k.o_confirm) {
    const d = t - k.o_confirm; const sc = d < 0.12 ? lerp(2.4, 1, eOut(d / 0.12)) : 1; const a = clamp(d / 0.06) * 0.92;
    ctx.save(); ctx.globalAlpha *= a; ctx.translate(1690, 640); ctx.rotate(-0.2); ctx.scale(sc, sc);
    ctx.strokeStyle = '#ff3b4e'; ctx.lineWidth = 8; rr(-190, -60, 380, 120, 16); ctx.stroke();
    ctx.restore();
    txt('SPACE SAFE', 1690, 640, { size: 56, weight: 700, color: '#ff3b4e', alpha: a, scale: sc, rot: -0.2, ls: '4px' });
  }
  const dp = pop(t, k.o_done, 0.4);
  const dw = mw('LEVEL 1 COMPLETE', { size: 50, weight: 600, ls: '6px' });
  drawCheck(960 - dw / 2 - 40, 858, dp.s * 1.2, C.lime, dp.a);
  txt('LEVEL 1 COMPLETE', 970, 860, { size: 50, weight: 600, color: C.lime, alpha: dp.a, scale: dp.s, ls: '6px', glow: 16 });
  txt('Facts: starlink.com & space-safety.starlink.com (checked Oct 2026)', 960, 1040, { size: 24, fam: 'Nunito', weight: 700, color: C.muted, alpha: dp.a });
}

function sceneList() { const k = K(); return [[-1, k.B1, s0], [k.B1, k.B2, s1], [k.B2, k.B3, s2], [k.B3, k.B4, s3], [k.B4, k.B5, s4], [k.B5, k.END + 5, s5]]; }
function drawScenes(t) {
  const L = sceneList();
  for (let i = 0; i < L.length; i++) {
    const [a, b, f] = L[i];
    if (t < a - WD || t >= b + WD) continue;
    const nearStart = i > 0 && t < a + WD;
    const nearEnd = i < L.length - 1 && t >= b - WD;
    if (!nearStart && t < a) continue;
    if (!nearEnd && t >= b) continue;
    ctx.save();
    if (nearStart) clipLeft(bandX(t, a));
    if (nearEnd) clipRight(bandX(t, b));
    f(t);
    ctx.restore();
  }
}
window.render = function (t) {
  ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.globalAlpha = 1; ctx.globalCompositeOperation = 'source-over'; ctx.shadowBlur = 0;
  bg(t);
  const [sx, sy] = shake(t);
  ctx.save(); ctx.translate(sx, sy); drawScenes(t); ctx.restore();
  hud(t); drawWipes(t);
  const fin = 1 - P(t, 0, 0.25);
  if (fin > 0) { ctx.fillStyle = `rgba(0,0,0,${fin})`; ctx.fillRect(0, 0, W, H); }
};
window.fontsReady = async function () {
  const specs = ['500 40px Fredoka', '600 40px Fredoka', '700 40px Fredoka', '600 40px Nunito', '700 40px Nunito', '800 40px Nunito', '900 40px Nunito', '500 40px JBM', '700 40px JBM', '800 40px JBM'];
  await Promise.all(specs.map(s => document.fonts.load(s, 'AbcÄ“”—’×−')));
  await document.fonts.ready;
  return specs.map(s => document.fonts.check(s));
};
