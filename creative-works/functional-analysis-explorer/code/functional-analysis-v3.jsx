import { useState, useEffect, useRef, useCallback, useMemo } from "react";

const C = {
  bg: "#0a0b0f", panel: "#12131a", panelDeep: "#0d0e14", border: "#1e2030",
  text: "#c8cad0", textDim: "#6b6e7a", accent: "#e8a44a", accentDim: "#e8a44a44",
  curve1: "#5b9bd5", curve2: "#e06c75", curve3: "#98c379", curve4: "#c678dd",
  curve5: "#56b6c2", gridLine: "#252738", highlight: "#ffffff", mathBg: "#0e0f16",
};
const FONT = "'EB Garamond', Georgia, serif";
const MONO = "'IBM Plex Mono', monospace";

const TABS = [
  { id: "lp", label: "Lᵖ Geometry" },
  { id: "fourier", label: "Fourier" },
  { id: "spectra", label: "Spectra" },
  { id: "banach", label: "Contraction" },
  { id: "projection", label: "Projection" },
  { id: "weakstrong", label: "Weak vs Strong" },
  { id: "compact", label: "Compact Ops" },
];

// ═══════════════════════════════════════════════
//  SHARED COMPONENTS
// ═══════════════════════════════════════════════
function MathBlock({ children }) {
  return (<div style={{ background: C.mathBg, borderLeft: `2px solid ${C.accent}`, padding: "8px 14px", margin: "10px 0", fontFamily: FONT, fontSize: 15, color: C.text, fontStyle: "italic", lineHeight: 1.8, borderRadius: "0 4px 4px 0" }}>{children}</div>);
}
function M({ children }) { return <span style={{ fontFamily: FONT, fontStyle: "italic", color: C.accent }}>{children}</span>; }

function Slider({ label, value, onChange, min, max, step = 0.01, format }) {
  return (<div style={{ marginBottom: 10 }}>
    <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 3 }}>
      <span style={{ color: C.text, fontSize: 13, fontFamily: FONT }}>{label}</span>
      <span style={{ color: C.accent, fontSize: 13, fontFamily: MONO, fontWeight: 500 }}>{format ? format(value) : value.toFixed(2)}</span>
    </div>
    <input type="range" min={min} max={max} step={step} value={value} onChange={(e) => onChange(parseFloat(e.target.value))} style={{ width: "100%", accentColor: C.accent }} />
  </div>);
}

function PlayControls({ playing, onToggle, onStep, onReset, label }) {
  const btn = (text, onClick, hl) => (<button onClick={onClick} style={{ padding: "4px 12px", borderRadius: 4, fontSize: 12, fontFamily: MONO, border: `1px solid ${hl ? C.accent : C.border}`, background: hl ? C.accentDim : "transparent", color: hl ? C.accent : C.textDim, cursor: "pointer" }}>{text}</button>);
  return (<div style={{ display: "flex", gap: 6, alignItems: "center", marginBottom: 10 }}>
    {btn(playing ? "⏸ pause" : "▶ play", onToggle, playing)}
    {onStep && btn("→ step", onStep, false)}
    {onReset && btn("↺ reset", onReset, false)}
    {label && <span style={{ color: C.textDim, fontSize: 11, fontFamily: MONO, marginLeft: 6 }}>{label}</span>}
  </div>);
}

function Chip({ active, onClick, children }) {
  return (<button onClick={onClick} style={{ padding: "5px 12px", borderRadius: 4, fontSize: 12, fontFamily: MONO, border: `1px solid ${active ? C.accent : C.border}`, background: active ? C.accentDim : "transparent", color: active ? C.accent : C.textDim, cursor: "pointer" }}>{children}</button>);
}

function useCanvas(draw, deps) {
  const ref = useRef(null);
  useEffect(() => {
    const canvas = ref.current; if (!canvas) return;
    const ctx = canvas.getContext("2d");
    const dpr = window.devicePixelRatio || 1;
    const rect = canvas.getBoundingClientRect();
    canvas.width = rect.width * dpr; canvas.height = rect.height * dpr;
    ctx.scale(dpr, dpr); ctx.clearRect(0, 0, rect.width, rect.height);
    draw(ctx, rect.width, rect.height);
  }, deps);
  return ref;
}

function drawGrid(ctx, w, h, opts = {}) {
  const { xRange: xR = [-2, 2], yRange: yR = [-2, 2], step = 0.5 } = opts;
  const xS = w / (xR[1] - xR[0]), yS = h / (yR[1] - yR[0]);
  ctx.strokeStyle = C.gridLine; ctx.lineWidth = 0.5;
  for (let x = Math.ceil(xR[0] / step) * step; x <= xR[1]; x += step) { const px = (x - xR[0]) * xS; ctx.beginPath(); ctx.moveTo(px, 0); ctx.lineTo(px, h); ctx.stroke(); }
  for (let y = Math.ceil(yR[0] / step) * step; y <= yR[1]; y += step) { const py = h - (y - yR[0]) * yS; ctx.beginPath(); ctx.moveTo(0, py); ctx.lineTo(w, py); ctx.stroke(); }
  ctx.strokeStyle = C.textDim; ctx.lineWidth = 1;
  const ox = (0 - xR[0]) * xS, oy = h - (0 - yR[0]) * yS;
  ctx.beginPath(); ctx.moveTo(ox, 0); ctx.lineTo(ox, h); ctx.stroke();
  ctx.beginPath(); ctx.moveTo(0, oy); ctx.lineTo(w, oy); ctx.stroke();
}

function toS(x, y, w, h, xR, yR) {
  return [((x - xR[0]) / (xR[1] - xR[0])) * w, h - ((y - yR[0]) / (yR[1] - yR[0])) * h];
}

// ═══════════════════════════════════════════════
//  TAB 1: Lp GEOMETRY
// ═══════════════════════════════════════════════
function LpGeometry() {
  const [p, setP] = useState(2);
  const xR = [-1.6, 1.6], yR = [-1.6, 1.6];
  const canvasRef = useCanvas((ctx, w, h) => {
    drawGrid(ctx, w, h, { xRange: xR, yRange: yR, step: 0.5 });
    const N = 600;
    const drawBall = (pp, color, lw, dash) => {
      ctx.beginPath(); ctx.strokeStyle = color; ctx.lineWidth = lw;
      if (dash) ctx.setLineDash(dash);
      for (let i = 0; i <= N; i++) {
        const t = (i / N) * 2 * Math.PI, ct = Math.cos(t), st = Math.sin(t);
        let r; if (pp >= 50) r = 1 / Math.max(Math.abs(ct), Math.abs(st));
        else { const d = Math.pow(Math.abs(ct), pp) + Math.pow(Math.abs(st), pp); r = d > 0 ? Math.pow(d, -1 / pp) : 0; }
        const [sx, sy] = toS(r * ct, r * st, w, h, xR, yR);
        i === 0 ? ctx.moveTo(sx, sy) : ctx.lineTo(sx, sy);
      }
      ctx.closePath(); ctx.stroke(); if (dash) ctx.setLineDash([]);
    };
    if (Math.abs(p - 1) > 0.1) drawBall(1, C.curve2 + "35", 1, [4, 4]);
    if (Math.abs(p - 2) > 0.1) drawBall(2, C.curve3 + "35", 1, [4, 4]);
    if (p < 18) drawBall(50, C.curve4 + "35", 1, [4, 4]);
    ctx.shadowColor = C.curve1; ctx.shadowBlur = 8;
    drawBall(p, C.curve1, 2.5, null); ctx.shadowBlur = 0;
    ctx.beginPath();
    for (let i = 0; i <= N; i++) {
      const t = (i / N) * 2 * Math.PI, ct = Math.cos(t), st = Math.sin(t);
      let r; if (p >= 50) r = 1 / Math.max(Math.abs(ct), Math.abs(st));
      else { const d = Math.pow(Math.abs(ct), p) + Math.pow(Math.abs(st), p); r = d > 0 ? Math.pow(d, -1 / p) : 0; }
      const [sx, sy] = toS(r * ct, r * st, w, h, xR, yR);
      i === 0 ? ctx.moveTo(sx, sy) : ctx.lineTo(sx, sy);
    }
    ctx.closePath(); ctx.fillStyle = C.curve1 + "12"; ctx.fill();
  }, [p]);

  return (<div>
    <p style={{ color: C.text, fontSize: 14, lineHeight: 1.6, fontFamily: FONT, marginBottom: 8 }}>
      The unit ball in <M>ℓ<sup>{p >= 20 ? "∞" : p.toFixed(1)}</sup></M> — norm choice reshapes geometry itself.
    </p>
    <MathBlock>‖<M>x</M>‖<sub>p</sub> = (∑ |x<sub>i</sub>|<sup>p</sup>)<sup>1/p</sup>,{"  "}B<sub>p</sub> = {"{"} x : ‖x‖<sub>p</sub> ≤ 1 {"}"}</MathBlock>
    <Slider label="p" value={p} onChange={setP} min={0.3} max={20} step={0.1} format={(v) => v >= 20 ? "∞" : v.toFixed(1)} />
    <div style={{ background: C.bg, borderRadius: 8, border: `1px solid ${C.border}`, overflow: "hidden", aspectRatio: "1" }}>
      <canvas ref={canvasRef} style={{ width: "100%", height: "100%", display: "block" }} />
    </div>
  </div>);
}

// ═══════════════════════════════════════════════
//  TAB 2: FOURIER (animated)
// ═══════════════════════════════════════════════
const TARGETS = {
  square: { label: "Square", fn: (x) => (x >= 0 ? 1 : -1) },
  sawtooth: { label: "Sawtooth", fn: (x) => x / Math.PI },
  triangle: { label: "Triangle", fn: (x) => 1 - (2 * Math.abs(x)) / Math.PI },
};

function fourierCoeffs(target, n) {
  const M = 1000, coeffs = [];
  for (let k = 0; k <= n; k++) {
    let ak = 0, bk = 0;
    for (let i = 0; i < M; i++) {
      const x = -Math.PI + ((2 * Math.PI) / M) * (i + 0.5), fv = target(x);
      if (k === 0) ak += fv; else { ak += fv * Math.cos(k * x); bk += fv * Math.sin(k * x); }
    }
    ak *= 2 / M; bk *= 2 / M; if (k === 0) ak /= 2;
    coeffs.push({ a: ak, b: bk });
  }
  return coeffs;
}
function evalFourier(coeffs, x, n) {
  let v = coeffs[0].a / 2;
  for (let k = 1; k <= n && k < coeffs.length; k++) v += coeffs[k].a * Math.cos(k * x) + coeffs[k].b * Math.sin(k * x);
  return v;
}

function FourierConvergence() {
  const [nTerms, setNTerms] = useState(1);
  const [targetKey, setTargetKey] = useState("square");
  const [playing, setPlaying] = useState(false);
  const maxN = 50;
  const target = TARGETS[targetKey];
  const coeffs = useMemo(() => fourierCoeffs(target.fn, maxN), [targetKey]);

  useEffect(() => {
    if (!playing) return;
    const id = setInterval(() => { setNTerms((n) => { if (n >= maxN) { setPlaying(false); return n; } return n + 1; }); }, 280);
    return () => clearInterval(id);
  }, [playing]);

  const errors = useMemo(() => {
    const errs = [], M = 400;
    for (let n = 1; n <= maxN; n++) {
      let ss = 0;
      for (let i = 0; i < M; i++) { const x = -Math.PI + ((2 * Math.PI) / M) * (i + 0.5); const d = target.fn(x) - evalFourier(coeffs, x, n); ss += d * d; }
      errs.push(Math.sqrt(ss / M));
    }
    return errs;
  }, [coeffs, targetKey]);

  const xR = [-Math.PI - 0.3, Math.PI + 0.3], yR = [-1.8, 1.8];
  const canvasRef = useCanvas((ctx, w, h) => {
    const splitY = h * 0.62, gapY = 28;
    drawGrid(ctx, w, splitY, { xRange: xR, yRange: yR, step: 1 });
    const N = 700;
    ctx.beginPath(); ctx.strokeStyle = C.textDim; ctx.lineWidth = 1.5; ctx.setLineDash([3, 3]);
    for (let i = 0; i <= N; i++) { const x = xR[0] + ((xR[1] - xR[0]) * i) / N; const y = x >= -Math.PI && x <= Math.PI ? target.fn(x) : 0; const [sx, sy] = toS(x, y, w, splitY, xR, yR); i === 0 ? ctx.moveTo(sx, sy) : ctx.lineTo(sx, sy); }
    ctx.stroke(); ctx.setLineDash([]);
    if (nTerms >= 2) {
      ctx.beginPath(); ctx.strokeStyle = C.curve4 + "50"; ctx.lineWidth = 1.5;
      const k = nTerms;
      for (let i = 0; i <= N; i++) { const x = xR[0] + ((xR[1] - xR[0]) * i) / N; const harm = coeffs[k].a * Math.cos(k * x) + coeffs[k].b * Math.sin(k * x); const prev = evalFourier(coeffs, x, nTerms - 1); const [sx, sy] = toS(x, prev + harm * 0.5, w, splitY, xR, yR); i === 0 ? ctx.moveTo(sx, sy) : ctx.lineTo(sx, sy); }
      ctx.stroke();
    }
    ctx.beginPath(); ctx.strokeStyle = C.accent; ctx.lineWidth = 2; ctx.shadowColor = C.accent; ctx.shadowBlur = 6;
    for (let i = 0; i <= N; i++) { const x = xR[0] + ((xR[1] - xR[0]) * i) / N; const y = evalFourier(coeffs, x, nTerms); const [sx, sy] = toS(x, y, w, splitY, xR, yR); i === 0 ? ctx.moveTo(sx, sy) : ctx.lineTo(sx, sy); }
    ctx.stroke(); ctx.shadowBlur = 0;
    ctx.font = `11px ${MONO}`; ctx.fillStyle = C.textDim; ctx.fillText("— target", 8, 16);
    ctx.fillStyle = C.accent; ctx.fillText(`— S${nTerms}(x)`, 8, 30);
    // error
    const eTop = splitY + gapY, eH = h - eTop - 4;
    const maxErr = Math.max(...errors, 0.01), eYR = [0, maxErr * 1.15];
    ctx.fillStyle = C.textDim; ctx.font = `11px ${MONO}`; ctx.fillText("L² error", 8, eTop - 6);
    ctx.beginPath(); ctx.strokeStyle = C.curve2; ctx.lineWidth = 2;
    for (let i = 0; i < errors.length; i++) { const ex = ((i + 1) / (maxN + 1)) * w; const ey = eTop + eH - (errors[i] / eYR[1]) * eH; i === 0 ? ctx.moveTo(ex, ey) : ctx.lineTo(ex, ey); }
    ctx.stroke();
    const cx = (nTerms / (maxN + 1)) * w, cy = eTop + eH - (errors[nTerms - 1] / eYR[1]) * eH;
    ctx.beginPath(); ctx.arc(cx, cy, 5, 0, Math.PI * 2); ctx.fillStyle = C.accent; ctx.fill();
    ctx.fillText(`ε = ${errors[nTerms - 1].toFixed(4)}`, cx + 10, cy - 6);
  }, [nTerms, targetKey, coeffs, errors]);

  return (<div>
    <p style={{ color: C.text, fontSize: 14, lineHeight: 1.6, fontFamily: FONT, marginBottom: 8 }}>
      Watch harmonics land one by one. Gibbs overshoots persist at ~9% — pointwise failure amid L² success.
    </p>
    <MathBlock>S<sub>N</sub>(x) = <M>a</M><sub>0</sub>/2 + ∑<sub>k=1</sub><sup>N</sup> (<M>a</M><sub>k</sub> cos <M>kx</M> + <M>b</M><sub>k</sub> sin <M>kx</M>){"  →  "}‖f − S<sub>N</sub>‖₂ → 0</MathBlock>
    <div style={{ display: "flex", gap: 8, marginBottom: 10, flexWrap: "wrap" }}>
      {Object.entries(TARGETS).map(([k, v]) => <Chip key={k} active={k === targetKey} onClick={() => { setTargetKey(k); setNTerms(1); setPlaying(false); }}>{v.label}</Chip>)}
    </div>
    <PlayControls playing={playing} onToggle={() => { if (nTerms >= maxN) setNTerms(1); setPlaying(!playing); }} onStep={() => setNTerms(n => Math.min(n + 1, maxN))} onReset={() => { setNTerms(1); setPlaying(false); }} label={`harmonic ${nTerms}/${maxN}`} />
    <Slider label="Terms" value={nTerms} onChange={(v) => setNTerms(Math.round(v))} min={1} max={maxN} step={1} format={(v) => v.toString()} />
    <div style={{ background: C.bg, borderRadius: 8, border: `1px solid ${C.border}`, overflow: "hidden", height: 420 }}>
      <canvas ref={canvasRef} style={{ width: "100%", height: "100%", display: "block" }} />
    </div>
  </div>);
}

// ═══════════════════════════════════════════════
//  TAB 3: SPECTRA
// ═══════════════════════════════════════════════
const OP_TYPES = {
  selfadjoint: { label: "Self-adjoint", desc: "σ(T) ⊂ ℝ" },
  compact: { label: "Compact", desc: "σ(T) clusters at 0" },
  general: { label: "General", desc: "σ(T) roams ℂ" },
};

function OperatorSpectra() {
  const [opType, setOpType] = useState("selfadjoint");
  const [dim, setDim] = useState(30);
  const [seed, setSeed] = useState(0);
  const eigenvalues = useMemo(() => {
    let s = seed + dim * 137;
    const rand = () => { s = (s * 1664525 + 1013904223) & 0xffffffff; return (s >>> 0) / 0xffffffff; };
    if (opType === "selfadjoint") return Array.from({ length: dim }, () => ({ re: (rand() - 0.5) * 4, im: 0 }));
    if (opType === "compact") return Array.from({ length: dim }, (_, k) => ({ re: (rand() > 0.5 ? 1 : -1) / ((k + 1) ** 2) + (rand() - 0.5) * 0.01, im: (rand() - 0.5) * 0.01 / ((k + 1) ** 2) }));
    return Array.from({ length: dim }, () => { const r = rand() * 2, t = rand() * 2 * Math.PI; return { re: r * Math.cos(t), im: r * Math.sin(t) }; });
  }, [opType, dim, seed]);
  const xR = [-3, 3], yR = [-3, 3];
  const canvasRef = useCanvas((ctx, w, h) => {
    drawGrid(ctx, w, h, { xRange: xR, yRange: yR, step: 1 });
    const color = opType === "selfadjoint" ? C.curve1 : opType === "compact" ? C.curve3 : C.curve4;
    if (opType === "selfadjoint") { ctx.strokeStyle = color + "25"; ctx.lineWidth = 8; ctx.beginPath(); ctx.moveTo(0, h / 2); ctx.lineTo(w, h / 2); ctx.stroke(); }
    eigenvalues.forEach((ev, i) => {
      const [sx, sy] = toS(ev.re, ev.im, w, h, xR, yR);
      ctx.beginPath(); ctx.arc(sx, sy, 9, 0, Math.PI * 2); ctx.fillStyle = color + "20"; ctx.fill();
      ctx.beginPath(); ctx.arc(sx, sy, 3.5, 0, Math.PI * 2);
      ctx.globalAlpha = 0.4 + 0.6 * (1 - i / eigenvalues.length); ctx.fillStyle = color; ctx.fill(); ctx.globalAlpha = 1;
    });
    if (opType === "compact") { const [ox, oy] = toS(0, 0, w, h, xR, yR); ctx.beginPath(); ctx.arc(ox, oy, 22, 0, Math.PI * 2); ctx.strokeStyle = C.accent + "40"; ctx.lineWidth = 1; ctx.setLineDash([3, 3]); ctx.stroke(); ctx.setLineDash([]); }
    ctx.font = `11px ${MONO}`; ctx.fillStyle = C.textDim; ctx.fillText("Re(λ)", w - 44, h / 2 + 16); ctx.fillText("Im(λ)", w / 2 + 8, 14);
  }, [eigenvalues, opType]);

  return (<div>
    <p style={{ color: C.text, fontSize: 14, lineHeight: 1.6, fontFamily: FONT, marginBottom: 8 }}>
      The spectrum reveals an operator's structural secrets.
    </p>
    <MathBlock>σ(T) = {"{"} λ ∈ ℂ : (T − λI) not invertible {"}"},{"  "}T = T* ⟹ σ(T) ⊂ ℝ</MathBlock>
    <div style={{ display: "flex", gap: 8, marginBottom: 8, flexWrap: "wrap" }}>
      {Object.entries(OP_TYPES).map(([k, v]) => <Chip key={k} active={k === opType} onClick={() => setOpType(k)}>{v.label}</Chip>)}
    </div>
    <div style={{ display: "flex", gap: 12, marginBottom: 10 }}>
      <div style={{ flex: 1 }}><Slider label="Dimension" value={dim} onChange={v => setDim(Math.round(v))} min={5} max={80} step={1} format={v => v.toString()} /></div>
      <Chip active={false} onClick={() => setSeed(s => s + 1)}>regenerate</Chip>
    </div>
    <div style={{ background: C.bg, borderRadius: 8, border: `1px solid ${C.border}`, overflow: "hidden", aspectRatio: "1" }}>
      <canvas ref={canvasRef} style={{ width: "100%", height: "100%", display: "block" }} />
    </div>
  </div>);
}

// ═══════════════════════════════════════════════
//  TAB 4: BANACH CONTRACTION (animated)
// ═══════════════════════════════════════════════
const MAPS = {
  cosine: { label: "cos(x)", fn: Math.cos, range: [-0.5, 1.5] },
  sqrt: { label: "√(x+1)/2", fn: (x) => Math.sqrt(x + 1) / 2, range: [-0.2, 1.2] },
  cubic: { label: "x/3+0.4", fn: (x) => x / 3 + 0.4, range: [-0.2, 1.2] },
};

function BanachContraction() {
  const [mapKey, setMapKey] = useState("cosine");
  const [maxIter, setMaxIter] = useState(12);
  const [x0, setX0] = useState(0.0);
  const [vis, setVis] = useState(0);
  const [playing, setPlaying] = useState(false);
  const map = MAPS[mapKey];

  useEffect(() => {
    if (!playing) return;
    const id = setInterval(() => { setVis(s => { if (s >= maxIter) { setPlaying(false); return s; } return s + 1; }); }, 400);
    return () => clearInterval(id);
  }, [playing, maxIter]);

  const iterates = useMemo(() => {
    const pts = [x0]; let x = x0;
    for (let i = 0; i < maxIter; i++) { x = map.fn(x); pts.push(x); }
    return pts;
  }, [mapKey, maxIter, x0]);

  const xR = map.range, yR = map.range;
  const canvasRef = useCanvas((ctx, w, h) => {
    drawGrid(ctx, w, h, { xRange: xR, yRange: yR, step: 0.5 });
    ctx.beginPath(); ctx.strokeStyle = C.textDim; ctx.lineWidth = 1; ctx.setLineDash([4, 4]);
    const [a1, b1] = toS(xR[0], xR[0], w, h, xR, yR); const [a2, b2] = toS(xR[1], xR[1], w, h, xR, yR);
    ctx.moveTo(a1, b1); ctx.lineTo(a2, b2); ctx.stroke(); ctx.setLineDash([]);
    ctx.beginPath(); ctx.strokeStyle = C.curve1; ctx.lineWidth = 2;
    for (let i = 0; i <= 400; i++) { const x = xR[0] + ((xR[1] - xR[0]) * i) / 400; const [sx, sy] = toS(x, map.fn(x), w, h, xR, yR); i === 0 ? ctx.moveTo(sx, sy) : ctx.lineTo(sx, sy); }
    ctx.stroke();
    let cx = iterates[0];
    const stepsToShow = Math.min(vis, iterates.length - 1);
    for (let i = 0; i < stepsToShow; i++) {
      const fx = iterates[i + 1]; const isCur = i === stepsToShow - 1;
      ctx.strokeStyle = isCur ? C.accent : C.accent + "60"; ctx.lineWidth = isCur ? 2 : 1.2;
      const [vx1, vy1] = toS(cx, i === 0 ? 0 : cx, w, h, xR, yR); const [vx2, vy2] = toS(cx, fx, w, h, xR, yR);
      ctx.beginPath(); ctx.moveTo(vx1, vy1); ctx.lineTo(vx2, vy2); ctx.stroke();
      const [hx1, hy1] = toS(cx, fx, w, h, xR, yR); const [hx2, hy2] = toS(fx, fx, w, h, xR, yR);
      ctx.beginPath(); ctx.moveTo(hx1, hy1); ctx.lineTo(hx2, hy2); ctx.stroke();
      ctx.beginPath(); ctx.arc(hx2, hy2, isCur ? 4 : 2.5, 0, Math.PI * 2);
      ctx.fillStyle = isCur ? C.accent : C.accent + "70"; ctx.fill();
      cx = fx;
    }
    ctx.font = `11px ${MONO}`; ctx.fillStyle = C.textDim; ctx.fillText("y = x", 8, 16);
    ctx.fillStyle = C.curve1; ctx.fillText(`y = ${map.label}`, 8, 30);
    ctx.fillStyle = C.accent; ctx.fillText(`x* ≈ ${iterates[Math.min(stepsToShow, iterates.length - 1)].toFixed(8)}`, 8, 44);
  }, [mapKey, maxIter, x0, iterates, vis]);

  return (<div>
    <p style={{ color: C.text, fontSize: 14, lineHeight: 1.6, fontFamily: FONT, marginBottom: 8 }}>
      Watch the cobweb spiral inward. Banach guarantees existence, uniqueness, and the path to get there.
    </p>
    <MathBlock>d(Tx, Ty) ≤ <M>κ</M> · d(x, y),{"  "}<M>κ</M> &lt; 1{"  ⟹  "}∃! x* : Tx* = x*</MathBlock>
    <div style={{ display: "flex", gap: 8, marginBottom: 10, flexWrap: "wrap" }}>
      {Object.entries(MAPS).map(([k, v]) => <Chip key={k} active={k === mapKey} onClick={() => { setMapKey(k); setX0(k === "cosine" ? 0 : 0.1); setVis(0); setPlaying(false); }}>{v.label}</Chip>)}
    </div>
    <PlayControls playing={playing} onToggle={() => { if (vis >= maxIter) setVis(0); setPlaying(!playing); }} onStep={() => setVis(s => Math.min(s + 1, maxIter))} onReset={() => { setVis(0); setPlaying(false); }} label={`step ${vis}/${maxIter}`} />
    <Slider label="x₀" value={x0} onChange={setX0} min={map.range[0]} max={map.range[1]} step={0.01} />
    <Slider label="Iterations" value={maxIter} onChange={v => { setMaxIter(Math.round(v)); setVis(Math.min(vis, Math.round(v))); }} min={1} max={30} step={1} format={v => v.toString()} />
    <div style={{ background: C.bg, borderRadius: 8, border: `1px solid ${C.border}`, overflow: "hidden", aspectRatio: "1" }}>
      <canvas ref={canvasRef} style={{ width: "100%", height: "100%", display: "block" }} />
    </div>
  </div>);
}

// ═══════════════════════════════════════════════
//  TAB 5: HILBERT PROJECTION
// ═══════════════════════════════════════════════
function HilbertProjection() {
  const [nBasis, setNBasis] = useState(3);
  const [targetKey, setTargetKey] = useState("bump");
  const targets = { bump: { label: "Gaussian", fn: x => Math.exp(-8 * x * x) }, abs: { label: "|x|", fn: Math.abs }, cubic: { label: "x³−x", fn: x => x ** 3 - x }, hat: { label: "Hat", fn: x => Math.max(0, 1 - 3 * Math.abs(x)) } };
  const target = targets[targetKey];
  const M = 500;
  const xs = useMemo(() => Array.from({ length: M }, (_, i) => -1 + (2 * (i + 0.5)) / M), []);
  const basis = useMemo(() => {
    const vecs = [];
    for (let k = 0; k < 10; k++) {
      let v = xs.map(x => Math.pow(x, k));
      for (const u of vecs) { const dot = v.reduce((s, vi, i) => s + vi * u[i], 0) / M; v = v.map((vi, i) => vi - dot * u[i]); }
      const norm = Math.sqrt(v.reduce((s, vi) => s + vi * vi, 0) / M);
      if (norm > 1e-10) { v = v.map(vi => vi / norm); vecs.push(v); }
    }
    return vecs;
  }, []);

  const { projection, residual, l2Error } = useMemo(() => {
    const f = xs.map(x => target.fn(x));
    let proj = xs.map(() => 0);
    for (let k = 0; k < nBasis && k < basis.length; k++) {
      const c = f.reduce((s, fi, i) => s + fi * basis[k][i], 0) / M;
      proj = proj.map((pi, i) => pi + c * basis[k][i]);
    }
    const res = f.map((fi, i) => fi - proj[i]);
    return { projection: proj, residual: res, l2Error: Math.sqrt(res.reduce((s, ri) => s + ri * ri, 0) / M) };
  }, [nBasis, targetKey, basis]);

  const xR = [-1.2, 1.2], yR = [-1.5, 1.5];
  const canvasRef = useCanvas((ctx, w, h) => {
    const mainH = h * 0.62, rTop = h * 0.70, rH = h - rTop - 4;
    drawGrid(ctx, w, mainH, { xRange: xR, yRange: yR, step: 0.5 });
    ctx.beginPath(); ctx.strokeStyle = C.textDim; ctx.lineWidth = 1.5; ctx.setLineDash([3, 3]);
    xs.forEach((x, i) => { const [sx, sy] = toS(x, target.fn(x), w, mainH, xR, yR); i === 0 ? ctx.moveTo(sx, sy) : ctx.lineTo(sx, sy); });
    ctx.stroke(); ctx.setLineDash([]);
    ctx.shadowColor = C.curve3; ctx.shadowBlur = 6;
    ctx.beginPath(); ctx.strokeStyle = C.curve3; ctx.lineWidth = 2.5;
    xs.forEach((x, i) => { const [sx, sy] = toS(x, projection[i], w, mainH, xR, yR); i === 0 ? ctx.moveTo(sx, sy) : ctx.lineTo(sx, sy); });
    ctx.stroke(); ctx.shadowBlur = 0;
    ctx.font = `11px ${MONO}`; ctx.fillStyle = C.textDim; ctx.fillText("— f(x)", 8, 16);
    ctx.fillStyle = C.curve3; ctx.fillText(`— π(f), dim=${nBasis}`, 8, 30);
    ctx.fillStyle = C.accent; ctx.fillText(`‖f−π(f)‖₂ = ${l2Error.toFixed(5)}`, 8, 44);
    ctx.fillStyle = C.textDim; ctx.font = `11px ${MONO}`; ctx.fillText("residual", 8, rTop - 6);
    const maxR = Math.max(...residual.map(Math.abs), 0.01) * 1.3;
    ctx.save(); ctx.translate(0, rTop);
    ctx.strokeStyle = C.gridLine; ctx.lineWidth = 0.5; ctx.beginPath(); ctx.moveTo(0, rH / 2); ctx.lineTo(w, rH / 2); ctx.stroke();
    ctx.beginPath(); ctx.strokeStyle = C.curve2; ctx.lineWidth = 1.5;
    xs.forEach((x, i) => { const px = ((x + 1.2) / 2.4) * w; const py = rH / 2 - (residual[i] / maxR) * (rH / 2); i === 0 ? ctx.moveTo(px, py) : ctx.lineTo(px, py); });
    ctx.stroke(); ctx.restore();
  }, [nBasis, targetKey, projection, residual, l2Error]);

  return (<div>
    <p style={{ color: C.text, fontSize: 14, lineHeight: 1.6, fontFamily: FONT, marginBottom: 8 }}>
      Unique closest point in a closed subspace, error orthogonal. Pythagoras in infinite dimensions.
    </p>
    <MathBlock>π(f) = ∑<sub>k</sub> ⟨f, e<sub>k</sub>⟩ e<sub>k</sub>,{"  "}(f − π(f)) ⊥ V</MathBlock>
    <div style={{ display: "flex", gap: 8, marginBottom: 10, flexWrap: "wrap" }}>
      {Object.entries(targets).map(([k, v]) => <Chip key={k} active={k === targetKey} onClick={() => setTargetKey(k)}>{v.label}</Chip>)}
    </div>
    <Slider label="Basis dimension" value={nBasis} onChange={v => setNBasis(Math.round(v))} min={1} max={10} step={1} format={v => v.toString()} />
    <div style={{ background: C.bg, borderRadius: 8, border: `1px solid ${C.border}`, overflow: "hidden", height: 420 }}>
      <canvas ref={canvasRef} style={{ width: "100%", height: "100%", display: "block" }} />
    </div>
  </div>);
}

// ═══════════════════════════════════════════════
//  TAB 6: WEAK vs STRONG
// ═══════════════════════════════════════════════
const TEST_FNS = {
  step: { label: "Step", fn: x => (x >= 0 ? 1 : 0), color: C.curve3 },
  ramp: { label: "Ramp", fn: x => x / Math.PI, color: C.curve5 },
  gauss: { label: "Gaussian", fn: x => Math.exp(-2 * x * x), color: C.curve4 },
  sin3: { label: "sin(3x)", fn: x => Math.sin(3 * x), color: C.curve2 },
};

function WeakStrongConvergence() {
  const [n, setN] = useState(1);
  const [playing, setPlaying] = useState(false);
  const [testKey, setTestKey] = useState("step");
  const maxN = 40;
  const testFn = TEST_FNS[testKey];

  useEffect(() => {
    if (!playing) return;
    const id = setInterval(() => { setN(p => { if (p >= maxN) { setPlaying(false); return p; } return p + 1; }); }, 350);
    return () => clearInterval(id);
  }, [playing]);

  const { innerProducts, norms } = useMemo(() => {
    const ips = [], nms = [], M = 2000;
    for (let k = 1; k <= maxN; k++) {
      let ip = 0, nm = 0;
      for (let i = 0; i < M; i++) { const x = -Math.PI + ((2 * Math.PI) / M) * (i + 0.5); const fk = Math.sin(k * x); ip += fk * testFn.fn(x); nm += fk * fk; }
      ips.push((ip * 2 * Math.PI) / M); nms.push(Math.sqrt((nm * 2 * Math.PI) / M));
    }
    return { innerProducts: ips, norms: nms };
  }, [testKey]);

  const canvasRef = useCanvas((ctx, w, h) => {
    const wH = h * 0.38, ipTop = h * 0.43, ipH = h * 0.26, nmTop = h * 0.74, nmH = h * 0.22;
    const xR = [-Math.PI - 0.2, Math.PI + 0.2], yR = [-1.6, 1.6];
    drawGrid(ctx, w, wH, { xRange: xR, yRange: yR, step: 1 });
    ctx.beginPath(); ctx.strokeStyle = testFn.color; ctx.lineWidth = 2; ctx.setLineDash([5, 3]);
    for (let i = 0; i <= 800; i++) { const x = xR[0] + ((xR[1] - xR[0]) * i) / 800; const [sx, sy] = toS(x, testFn.fn(x), w, wH, xR, yR); i === 0 ? ctx.moveTo(sx, sy) : ctx.lineTo(sx, sy); }
    ctx.stroke(); ctx.setLineDash([]);
    const samples = Math.max(800, n * 8);
    ctx.beginPath(); ctx.strokeStyle = C.accent; ctx.lineWidth = 1.5; ctx.shadowColor = C.accent; ctx.shadowBlur = 4;
    for (let i = 0; i <= samples; i++) { const x = xR[0] + ((xR[1] - xR[0]) * i) / samples; const [sx, sy] = toS(x, Math.sin(n * x), w, wH, xR, yR); i === 0 ? ctx.moveTo(sx, sy) : ctx.lineTo(sx, sy); }
    ctx.stroke(); ctx.shadowBlur = 0;
    ctx.font = `11px ${MONO}`; ctx.fillStyle = testFn.color; ctx.fillText(`— g(x)`, 8, 14); ctx.fillStyle = C.accent; ctx.fillText(`— sin(${n}x)`, 8, 28);
    // inner products
    ctx.fillStyle = C.textDim; ctx.font = `11px ${MONO}`; ctx.fillText("⟨fₙ, g⟩ → 0", 8, ipTop - 6);
    const maxIP = Math.max(...innerProducts.map(Math.abs), 0.1) * 1.2;
    ctx.save(); ctx.translate(0, ipTop);
    ctx.strokeStyle = C.gridLine; ctx.lineWidth = 0.5; ctx.beginPath(); ctx.moveTo(0, ipH / 2); ctx.lineTo(w, ipH / 2); ctx.stroke();
    const barW = Math.max(2, (w / maxN) - 2);
    for (let k = 0; k < Math.min(n, maxN); k++) {
      const bx = ((k + 0.5) / maxN) * w - barW / 2, val = innerProducts[k];
      const bh = (Math.abs(val) / maxIP) * (ipH / 2), by = val >= 0 ? ipH / 2 - bh : ipH / 2;
      ctx.fillStyle = k === n - 1 ? C.accent : C.curve1 + "70"; ctx.fillRect(bx, by, barW, bh);
    }
    if (n >= 1) { ctx.fillStyle = C.accent; ctx.font = `11px ${MONO}`; ctx.fillText(`⟨f${n},g⟩ = ${innerProducts[n - 1].toFixed(4)}`, w - 160, 14); }
    ctx.restore();
    // norms
    ctx.fillStyle = C.textDim; ctx.font = `11px ${MONO}`; ctx.fillText("‖fₙ‖₂ = const!", 8, nmTop - 6);
    const expNorm = norms[0];
    ctx.save(); ctx.translate(0, nmTop);
    ctx.strokeStyle = C.curve2 + "40"; ctx.lineWidth = 1; ctx.setLineDash([4, 4]);
    const nlY = nmH - (expNorm / (expNorm * 1.3)) * nmH;
    ctx.beginPath(); ctx.moveTo(0, nlY); ctx.lineTo(w, nlY); ctx.stroke(); ctx.setLineDash([]);
    for (let k = 0; k < Math.min(n, maxN); k++) {
      const dx = ((k + 0.5) / maxN) * w, dy = nmH - (norms[k] / (expNorm * 1.3)) * nmH;
      ctx.beginPath(); ctx.arc(dx, dy, k === n - 1 ? 4 : 2.5, 0, Math.PI * 2);
      ctx.fillStyle = k === n - 1 ? C.accent : C.curve2 + "80"; ctx.fill();
    }
    ctx.fillStyle = C.accent; ctx.font = `11px ${MONO}`; ctx.fillText(`‖f${n}‖₂ = ${norms[n - 1].toFixed(4)}`, w - 160, 14);
    ctx.fillStyle = C.curve2 + "60"; ctx.fillText(`√π ≈ ${Math.sqrt(Math.PI).toFixed(4)}`, w - 160, 28);
    ctx.restore();
  }, [n, testKey, innerProducts, norms]);

  return (<div>
    <p style={{ color: C.text, fontSize: 14, lineHeight: 1.6, fontFamily: FONT, marginBottom: 8 }}>
      sin(<M>nx</M>) converges weakly to zero — inner products with any fixed function decay — but
      ‖sin(nx)‖ = √π always. The fan spins so fast it vanishes, though the air moves with the same energy.
    </p>
    <MathBlock>f<sub>n</sub> ⇀ 0 (weakly): ⟨f<sub>n</sub>, g⟩ → 0 ∀g,{"  "}but ‖f<sub>n</sub>‖ = √π ↛ 0</MathBlock>
    <div style={{ display: "flex", gap: 8, marginBottom: 10, flexWrap: "wrap" }}>
      <span style={{ color: C.textDim, fontSize: 12, fontFamily: MONO, alignSelf: "center" }}>g:</span>
      {Object.entries(TEST_FNS).map(([k, v]) => <Chip key={k} active={k === testKey} onClick={() => setTestKey(k)}>{v.label}</Chip>)}
    </div>
    <PlayControls playing={playing} onToggle={() => { if (n >= maxN) setN(1); setPlaying(!playing); }} onStep={() => setN(p => Math.min(p + 1, maxN))} onReset={() => { setN(1); setPlaying(false); }} label={`n = ${n}`} />
    <Slider label="n" value={n} onChange={v => setN(Math.round(v))} min={1} max={maxN} step={1} format={v => v.toString()} />
    <div style={{ background: C.bg, borderRadius: 8, border: `1px solid ${C.border}`, overflow: "hidden", height: 490 }}>
      <canvas ref={canvasRef} style={{ width: "100%", height: "100%", display: "block" }} />
    </div>
  </div>);
}

// ═══════════════════════════════════════════════
//  TAB 7: COMPACT OPERATOR GEOMETRY (new!)
// ═══════════════════════════════════════════════
const SV_PRESETS = {
  traceclass: { label: "Trace class", desc: "σₖ ~ 1/k — summable singular values", gen: (k) => 1 / (k + 1) },
  hilbertschmidt: { label: "Hilbert–Schmidt", desc: "σₖ ~ 1/√(k+1) — square-summable", gen: (k) => 1 / Math.sqrt(k + 1) },
  compact: { label: "Compact", desc: "σₖ ~ 1/k⁰·³ — slow decay, still → 0", gen: (k) => 1 / Math.pow(k + 1, 0.3) },
  finiterank: { label: "Finite rank", desc: "Only first r singular values nonzero", gen: (k) => k < 3 ? 1 / (k + 1) : 0 },
  notcompact: { label: "Bounded ≠ compact", desc: "σₖ = 0.8 — no decay, not compact!", gen: () => 0.8 },
};

function CompactOperators() {
  const [presetKey, setPresetKey] = useState("traceclass");
  const [nDims, setNDims] = useState(12);
  const [viewPair, setViewPair] = useState(0); // which pair of dimensions to view
  const [angle, setAngle] = useState(0.3); // rotation angle for SVD visualization
  const [playing, setPlaying] = useState(false);
  const [animStep, setAnimStep] = useState(0); // 0=original, 1=V*, 2=Sigma, 3=U

  const preset = SV_PRESETS[presetKey];

  useEffect(() => {
    if (!playing) return;
    const id = setInterval(() => {
      setAnimStep(s => { if (s >= 3) { setPlaying(false); return s; } return s + 1; });
    }, 900);
    return () => clearInterval(id);
  }, [playing]);

  const singularValues = useMemo(() =>
    Array.from({ length: nDims }, (_, k) => Math.max(0, preset.gen(k)))
  , [presetKey, nDims]);

  // the pair of dimensions we're projecting onto
  const d1 = viewPair * 2;
  const d2 = viewPair * 2 + 1;
  const s1 = d1 < singularValues.length ? singularValues[d1] : 0;
  const s2 = d2 < singularValues.length ? singularValues[d2] : 0;

  const maxPairs = Math.floor(nDims / 2);

  const canvasRef = useCanvas((ctx, w, h) => {
    // layout: left half = geometry, right half = singular value profile
    const geoW = w * 0.55;
    const svLeft = w * 0.60;
    const svW = w * 0.38;
    const xR = [-1.6, 1.6], yR = [-1.6, 1.6];

    // ─── geometric view ───
    ctx.save();
    ctx.beginPath(); ctx.rect(0, 0, geoW, h); ctx.clip();

    drawGrid(ctx, geoW, h, { xRange: xR, yRange: yR, step: 0.5 });

    const cosA = Math.cos(angle), sinA = Math.sin(angle);

    // draw unit circle (domain)
    ctx.beginPath(); ctx.strokeStyle = C.textDim + "40"; ctx.lineWidth = 1; ctx.setLineDash([3, 3]);
    for (let i = 0; i <= 200; i++) {
      const t = (i / 200) * 2 * Math.PI;
      const [sx, sy] = toS(Math.cos(t), Math.sin(t), geoW, h, xR, yR);
      i === 0 ? ctx.moveTo(sx, sy) : ctx.lineTo(sx, sy);
    }
    ctx.closePath(); ctx.stroke(); ctx.setLineDash([]);

    // points on unit circle
    const nPts = 48;
    for (let i = 0; i < nPts; i++) {
      const t = (i / nPts) * 2 * Math.PI;
      const px = Math.cos(t), py = Math.sin(t);

      // SVD decomposition: T = U Σ V*
      // step 0: original point (px, py)
      // step 1: after V* rotation
      // step 2: after Σ scaling
      // step 3: after U rotation
      let x = px, y = py;

      // V* = rotation by -angle
      if (animStep >= 1) {
        const rx = x * cosA + y * sinA;
        const ry = -x * sinA + y * cosA;
        x = rx; y = ry;
      }
      // Σ: scale by singular values
      if (animStep >= 2) {
        x *= s1; y *= s2;
      }
      // U = rotation by angle (for visual clarity)
      if (animStep >= 3) {
        const rx = x * cosA - y * sinA;
        const ry = x * sinA + y * cosA;
        x = rx; y = ry;
      }

      const hue = (i / nPts) * 360;
      const [sx, sy] = toS(x, y, geoW, h, xR, yR);

      // trail line from origin
      const [ox, oy] = toS(0, 0, geoW, h, xR, yR);
      ctx.beginPath(); ctx.strokeStyle = `hsla(${hue}, 70%, 60%, 0.15)`;
      ctx.lineWidth = 1; ctx.moveTo(ox, oy); ctx.lineTo(sx, sy); ctx.stroke();

      // point
      ctx.beginPath(); ctx.arc(sx, sy, 3.5, 0, Math.PI * 2);
      ctx.fillStyle = `hsla(${hue}, 70%, 60%, 0.85)`; ctx.fill();
    }

    // draw the image ellipse outline (full transform)
    ctx.beginPath();
    ctx.strokeStyle = C.accent; ctx.lineWidth = 2;
    ctx.shadowColor = C.accent; ctx.shadowBlur = 6;
    for (let i = 0; i <= 200; i++) {
      const t = (i / 200) * 2 * Math.PI;
      let x = Math.cos(t), y = Math.sin(t);
      // full SVD
      let rx = x * cosA + y * sinA, ry = -x * sinA + y * cosA;
      rx *= s1; ry *= s2;
      const fx = rx * cosA - ry * sinA, fy = rx * sinA + ry * cosA;
      const [sx, sy] = toS(fx, fy, geoW, h, xR, yR);
      i === 0 ? ctx.moveTo(sx, sy) : ctx.lineTo(sx, sy);
    }
    ctx.closePath(); ctx.stroke(); ctx.shadowBlur = 0;

    // stage label
    const stages = ["unit ball  B", "after V*  (rotate)", "after Σ  (scale)", "after UΣV* = T  (full)"];
    ctx.fillStyle = C.accent; ctx.font = `12px ${MONO}`;
    ctx.fillText(stages[animStep], 8, h - 12);

    ctx.fillStyle = C.textDim; ctx.font = `11px ${MONO}`;
    ctx.fillText(`dims ${d1 + 1}–${d2 + 1}`, 8, 16);
    ctx.fillText(`σ${d1 + 1}=${s1.toFixed(3)}, σ${d2 + 1}=${s2.toFixed(3)}`, 8, 30);

    ctx.restore();

    // ─── singular value profile ───
    ctx.save(); ctx.translate(svLeft, 0);

    ctx.fillStyle = C.textDim; ctx.font = `12px ${MONO}`;
    ctx.fillText("Singular values σₖ", 0, 20);

    const maxSV = Math.max(...singularValues, 0.01);
    const barH = (h - 50) / nDims;
    const barMaxW = svW - 20;

    for (let k = 0; k < nDims; k++) {
      const by = 32 + k * barH;
      const bw = (singularValues[k] / maxSV) * barMaxW;

      // highlight viewed pair
      const isViewed = k === d1 || k === d2;
      ctx.fillStyle = isViewed ? C.accent + "30" : "transparent";
      ctx.fillRect(-4, by, svW, barH - 1);

      // bar
      ctx.fillStyle = singularValues[k] === 0 ? C.textDim + "20" :
        isViewed ? C.accent : C.curve1 + "80";
      ctx.fillRect(0, by + 2, Math.max(1, bw), barH - 4);

      // label
      ctx.fillStyle = isViewed ? C.accent : C.textDim;
      ctx.font = `${Math.min(11, barH - 2)}px ${MONO}`;
      ctx.fillText(`σ${k + 1}`, bw + 4, by + barH - 4);
    }

    // decay info
    const traceNorm = singularValues.reduce((s, v) => s + v, 0);
    const hsNorm = Math.sqrt(singularValues.reduce((s, v) => s + v * v, 0));
    const opNorm = singularValues[0];

    ctx.fillStyle = C.textDim; ctx.font = `10px ${MONO}`;
    const infoY = h - 36;
    ctx.fillText(`‖T‖ = ${opNorm.toFixed(3)}`, 0, infoY);
    ctx.fillText(`‖T‖₂ = ${hsNorm.toFixed(3)}`, 0, infoY + 13);
    ctx.fillText(`‖T‖₁ = ${traceNorm.toFixed(3)}`, 0, infoY + 26);

    ctx.restore();
  }, [presetKey, nDims, viewPair, angle, animStep, singularValues, s1, s2]);

  return (<div>
    <p style={{ color: C.text, fontSize: 14, lineHeight: 1.6, fontFamily: FONT, marginBottom: 8 }}>
      A compact operator maps the unit ball to a set with compact closure — in infinite dimensions, a genuinely
      restrictive condition. The SVD decomposes it: rotate, scale each axis by a singular value, rotate again.
      Compactness means the singular values decay to zero: the image ellipsoid gets thinner and thinner in
      successive dimensions. Navigate dimension-pairs to see the squishing accumulate.
    </p>
    <MathBlock>
      T = UΣV*,{"  "}σ₁ ≥ σ₂ ≥ ⋯ ≥ 0<br />
      T compact ⟺ σₖ → 0,{"  "}
      T trace-class ⟺ ∑σₖ &lt; ∞,{"  "}
      T Hilbert–Schmidt ⟺ ∑σₖ² &lt; ∞
    </MathBlock>
    <div style={{ display: "flex", gap: 8, marginBottom: 10, flexWrap: "wrap" }}>
      {Object.entries(SV_PRESETS).map(([k, v]) =>
        <Chip key={k} active={k === presetKey} onClick={() => { setPresetKey(k); setAnimStep(0); setPlaying(false); }}>{v.label}</Chip>
      )}
    </div>
    <p style={{ color: C.textDim, fontSize: 12, fontFamily: MONO, marginBottom: 10 }}>{preset.desc}</p>

    <PlayControls playing={playing}
      onToggle={() => { if (animStep >= 3) setAnimStep(0); setPlaying(!playing); }}
      onStep={() => setAnimStep(s => Math.min(s + 1, 3))}
      onReset={() => { setAnimStep(0); setPlaying(false); }}
      label={["B (unit ball)", "V* (first rotation)", "Σ (scaling)", "UΣV* (complete)"][animStep]} />

    <div style={{ display: "flex", gap: 12 }}>
      <div style={{ flex: 1 }}><Slider label="Dimensions" value={nDims} onChange={v => { setNDims(Math.round(v)); setViewPair(Math.min(viewPair, Math.floor(Math.round(v) / 2) - 1)); }} min={4} max={24} step={2} format={v => v.toString()} /></div>
      <div style={{ flex: 1 }}><Slider label="View dimension pair" value={viewPair} onChange={v => setViewPair(Math.round(v))} min={0} max={Math.max(0, maxPairs - 1)} step={1} format={v => `${v * 2 + 1}–${v * 2 + 2}`} /></div>
    </div>
    <Slider label="Rotation angle θ" value={angle} onChange={setAngle} min={0} max={Math.PI} step={0.01} format={v => (v * 180 / Math.PI).toFixed(0) + "°"} />

    <div style={{ background: C.bg, borderRadius: 8, border: `1px solid ${C.border}`, overflow: "hidden", aspectRatio: "1.5/1", minHeight: 340 }}>
      <canvas ref={canvasRef} style={{ width: "100%", height: "100%", display: "block" }} />
    </div>
  </div>);
}

// ═══════════════════════════════════════════════
//  MAIN
// ═══════════════════════════════════════════════
export default function FunctionalAnalysisExplorer() {
  const [activeTab, setActiveTab] = useState("lp");
  const content = {
    lp: <LpGeometry />, fourier: <FourierConvergence />, spectra: <OperatorSpectra />,
    banach: <BanachContraction />, projection: <HilbertProjection />,
    weakstrong: <WeakStrongConvergence />, compact: <CompactOperators />,
  };

  return (
    <div style={{ minHeight: "100vh", background: C.bg, color: C.text, fontFamily: FONT, padding: "24px 16px" }}>
      <link href="https://fonts.googleapis.com/css2?family=EB+Garamond:ital,wght@0,400;0,500;0,600;1,400&family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet" />
      <div style={{ maxWidth: 680, margin: "0 auto" }}>
        <h1 style={{ fontSize: 28, fontWeight: 400, letterSpacing: "-0.02em", color: C.highlight, marginBottom: 4 }}>
          Functional Analysis Explorer
        </h1>
        <p style={{ color: C.textDim, fontSize: 13, marginBottom: 20, fontFamily: MONO }}>
          geometry in infinite dimensions — made visible, temporal, and tactile
        </p>
        <div style={{ display: "flex", gap: 0, marginBottom: 20, borderBottom: `1px solid ${C.border}`, overflowX: "auto" }}>
          {TABS.map(tab => (
            <button key={tab.id} onClick={() => setActiveTab(tab.id)} style={{
              padding: "9px 10px", border: "none",
              borderBottom: `2px solid ${activeTab === tab.id ? C.accent : "transparent"}`,
              background: "transparent", color: activeTab === tab.id ? C.accent : C.textDim,
              cursor: "pointer", fontSize: 12, fontFamily: MONO, whiteSpace: "nowrap",
              transition: "color 0.2s, border-color 0.2s",
            }}>{tab.label}</button>
          ))}
        </div>
        <div style={{ background: C.panel, borderRadius: 12, border: `1px solid ${C.border}`, padding: 18 }}>
          {content[activeTab]}
        </div>
        <p style={{ color: C.textDim, fontSize: 11, marginTop: 14, textAlign: "center", fontFamily: MONO }}>
          ▶ play to animate · drag sliders to explore · navigate dimensions to see infinite-dimensional structure
        </p>
      </div>
    </div>
  );
}
