import { useState, useEffect, useRef, useMemo } from "react";

const C = {
  bg: "#0a0b0f", panel: "#12131a", border: "#1e2030",
  text: "#c8cad0", textDim: "#6b6e7a", accent: "#e8a44a", accentDim: "#e8a44a44",
  curve1: "#5b9bd5", curve2: "#e06c75", curve3: "#98c379", curve4: "#c678dd",
  curve5: "#56b6c2", gridLine: "#252738", highlight: "#ffffff", mathBg: "#0e0f16",
  hot: "#ff6b35", warm: "#e8a44a", cool: "#5b9bd5", cold: "#2a5298",
};
const FONT = "'EB Garamond', Georgia, serif";
const MONO = "'IBM Plex Mono', monospace";

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

function Chip({ active, onClick, children }) {
  return (<button onClick={onClick} style={{ padding: "5px 12px", borderRadius: 4, fontSize: 12, fontFamily: MONO, border: `1px solid ${active ? C.accent : C.border}`, background: active ? C.accentDim : "transparent", color: active ? C.accent : C.textDim, cursor: "pointer" }}>{children}</button>);
}

function PlayControls({ playing, onToggle, onReset, label }) {
  const btn = (text, onClick, hl) => (<button onClick={onClick} style={{ padding: "4px 12px", borderRadius: 4, fontSize: 12, fontFamily: MONO, border: `1px solid ${hl ? C.accent : C.border}`, background: hl ? C.accentDim : "transparent", color: hl ? C.accent : C.textDim, cursor: "pointer" }}>{text}</button>);
  return (<div style={{ display: "flex", gap: 6, alignItems: "center", marginBottom: 10 }}>
    {btn(playing ? "⏸ pause" : "▶ play", onToggle, playing)}
    {onReset && btn("↺ reset", onReset, false)}
    {label && <span style={{ color: C.textDim, fontSize: 11, fontFamily: MONO, marginLeft: 6 }}>{label}</span>}
  </div>);
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
  const { xRange: xR = [0, 1], yRange: yR = [-1, 1], step = 0.5 } = opts;
  const xS = w / (xR[1] - xR[0]), yS = h / (yR[1] - yR[0]);
  ctx.strokeStyle = C.gridLine; ctx.lineWidth = 0.5;
  for (let x = Math.ceil(xR[0] / step) * step; x <= xR[1]; x += step) { const px = (x - xR[0]) * xS; ctx.beginPath(); ctx.moveTo(px, 0); ctx.lineTo(px, h); ctx.stroke(); }
  for (let y = Math.ceil(yR[0] / step) * step; y <= yR[1]; y += step) { const py = h - (y - yR[0]) * yS; ctx.beginPath(); ctx.moveTo(0, py); ctx.lineTo(w, py); ctx.stroke(); }
}

function toS(x, y, w, h, xR, yR) {
  return [((x - xR[0]) / (xR[1] - xR[0])) * w, h - ((y - yR[0]) / (yR[1] - yR[0])) * h];
}

// ─── Initial conditions ───
const INITIAL_CONDITIONS = {
  step: {
    label: "Step function",
    desc: "sharp discontinuity — the heat equation smooths it instantly",
    fn: (x) => x < 0.5 ? 1 : 0,
  },
  spike: {
    label: "Delta-like spike",
    desc: "concentrated heat diffuses outward — the fundamental solution",
    fn: (x) => Math.exp(-200 * (x - 0.5) ** 2),
  },
  sawtooth: {
    label: "Sawtooth",
    desc: "linear ramps with sharp corners get rounded",
    fn: (x) => 2 * (x - Math.floor(x + 0.5)),
  },
  twoblock: {
    label: "Two blocks",
    desc: "separate hot regions merge as heat diffuses between them",
    fn: (x) => (x > 0.15 && x < 0.35) || (x > 0.65 && x < 0.85) ? 1 : 0,
  },
  sine_sum: {
    label: "High-freq sum",
    desc: "the high harmonics die first — a spectral drama",
    fn: (x) => 0.5 * Math.sin(2 * Math.PI * x) + 0.3 * Math.sin(6 * Math.PI * x) + 0.2 * Math.sin(14 * Math.PI * x),
  },
  noise: {
    label: "Rough noise",
    desc: "jagged randomness becomes silk under the heat kernel",
    fn: null, // generated at runtime
  },
};

// generate noise deterministically
function generateNoise() {
  let s = 42;
  const rand = () => { s = (s * 1664525 + 1013904223) & 0xffffffff; return (s >>> 0) / 0xffffffff; };
  // piecewise constant with random heights, then some interpolation
  const nPieces = 30;
  const heights = Array.from({ length: nPieces + 1 }, () => (rand() - 0.5) * 2);
  return (x) => {
    const idx = Math.min(Math.floor(x * nPieces), nPieces - 1);
    const frac = x * nPieces - idx;
    return heights[idx] * (1 - frac) + heights[idx + 1] * frac;
  };
}

// ─── Fourier coefficients on [0, 1] with periodic BC ───
function computeFourierCoeffs(fn, maxK) {
  const M = 2000;
  const coeffs = [];
  for (let k = -maxK; k <= maxK; k++) {
    let re = 0, im = 0;
    for (let i = 0; i < M; i++) {
      const x = (i + 0.5) / M;
      const fv = fn(x);
      const angle = -2 * Math.PI * k * x;
      re += fv * Math.cos(angle);
      im += fv * Math.sin(angle);
    }
    coeffs.push({ k, re: re / M, im: im / M });
  }
  return coeffs;
}

// evaluate heat equation solution at time t: sum of c_k * e^{-4π²k²t} * e^{2πikx}
function evalHeatSolution(coeffs, x, t) {
  let re = 0;
  for (const { k, re: ck_re, im: ck_im } of coeffs) {
    const decay = Math.exp(-4 * Math.PI * Math.PI * k * k * t);
    const angle = 2 * Math.PI * k * x;
    const cos_a = Math.cos(angle), sin_a = Math.sin(angle);
    // c_k * e^{-4π²k²t} * e^{2πikx}
    // = (ck_re + i*ck_im) * decay * (cos_a + i*sin_a)
    re += decay * (ck_re * cos_a - ck_im * sin_a);
  }
  return re;
}

// temperature to color
function tempColor(v, vmin, vmax) {
  const t = Math.max(0, Math.min(1, (v - vmin) / (vmax - vmin + 1e-10)));
  // cold blue → warm amber → hot orange
  const r = Math.round(42 + t * 213);
  const g = Math.round(82 + t * 70 - t * t * 80);
  const b = Math.round(152 - t * 120);
  return `rgb(${r},${g},${b})`;
}

export default function HeatEquationExplorer() {
  const [icKey, setIcKey] = useState("step");
  const [time, setTime] = useState(0);
  const [playing, setPlaying] = useState(false);
  const [speed, setSpeed] = useState(1);
  const [showGhosts, setShowGhosts] = useState(true);

  const maxK = 50;

  // generate noise function once
  const noiseFn = useMemo(() => generateNoise(), []);

  const icFn = useMemo(() => {
    if (icKey === "noise") return noiseFn;
    return INITIAL_CONDITIONS[icKey].fn;
  }, [icKey, noiseFn]);

  const coeffs = useMemo(() => computeFourierCoeffs(icFn, maxK), [icFn]);

  // animation
  useEffect(() => {
    if (!playing) return;
    let frame;
    let lastT = performance.now();
    const animate = (now) => {
      const dt = (now - lastT) / 1000;
      lastT = now;
      setTime(t => {
        const next = t + dt * speed * 0.01;
        if (next > 0.5) { setPlaying(false); return 0.5; }
        return next;
      });
      frame = requestAnimationFrame(animate);
    };
    frame = requestAnimationFrame(animate);
    return () => cancelAnimationFrame(frame);
  }, [playing, speed]);

  // snapshot times for ghost curves
  const ghostTimes = [0, 0.001, 0.005, 0.02, 0.05, 0.15];

  const N = 500; // spatial resolution
  const xs = useMemo(() => Array.from({ length: N }, (_, i) => i / (N - 1)), []);

  const currentVals = useMemo(() => xs.map(x => evalHeatSolution(coeffs, x, time)), [coeffs, time]);

  // precompute ghost curves
  const ghostCurves = useMemo(() =>
    ghostTimes.map(gt => xs.map(x => evalHeatSolution(coeffs, x, gt)))
  , [coeffs]);

  // spectral decay data
  const spectralDecay = useMemo(() => {
    const data = [];
    for (let k = 1; k <= 20; k++) {
      const idx = coeffs.findIndex(c => c.k === k);
      if (idx === -1) continue;
      const c = coeffs[idx];
      const mag0 = Math.sqrt(c.re * c.re + c.im * c.im);
      const decay = Math.exp(-4 * Math.PI * Math.PI * k * k * time);
      data.push({ k, mag0, magT: mag0 * decay, decay });
    }
    return data;
  }, [coeffs, time]);

  const yMin = Math.min(...currentVals, ...ghostCurves[0], -0.2);
  const yMax = Math.max(...currentVals, ...ghostCurves[0], 0.2);
  const yPad = (yMax - yMin) * 0.15;
  const xR = [-0.02, 1.02];
  const yR = [yMin - yPad, yMax + yPad];

  // ─── main canvas ───
  const mainRef = useCanvas((ctx, w, h) => {
    // layout: top 55% = spatial, bottom section = spectrum + heatmap
    const spatH = h * 0.50;
    const heatTop = spatH + 2;
    const heatH = 32;
    const specTop = heatTop + heatH + 16;
    const specH = h - specTop - 8;

    // ─── spatial plot ───
    drawGrid(ctx, w, spatH, { xRange: xR, yRange: yR, step: 0.25 });

    // ghost curves (historical snapshots)
    if (showGhosts) {
      ghostCurves.forEach((curve, gi) => {
        if (ghostTimes[gi] > time + 0.001) return;
        const alpha = Math.max(0.08, 0.4 - gi * 0.06);
        ctx.beginPath();
        ctx.strokeStyle = gi === 0 ? C.textDim + "60" : C.curve5 + Math.round(alpha * 255).toString(16).padStart(2, "0");
        ctx.lineWidth = gi === 0 ? 1.5 : 1;
        if (gi === 0) { ctx.setLineDash([3, 3]); }
        for (let i = 0; i < N; i++) {
          const [sx, sy] = toS(xs[i], curve[i], w, spatH, xR, yR);
          i === 0 ? ctx.moveTo(sx, sy) : ctx.lineTo(sx, sy);
        }
        ctx.stroke();
        ctx.setLineDash([]);
      });
    }

    // current solution
    ctx.beginPath(); ctx.strokeStyle = C.accent; ctx.lineWidth = 2.5;
    ctx.shadowColor = C.accent; ctx.shadowBlur = 8;
    for (let i = 0; i < N; i++) {
      const [sx, sy] = toS(xs[i], currentVals[i], w, spatH, xR, yR);
      i === 0 ? ctx.moveTo(sx, sy) : ctx.lineTo(sx, sy);
    }
    ctx.stroke(); ctx.shadowBlur = 0;

    // labels
    ctx.font = `11px ${MONO}`; ctx.fillStyle = C.textDim;
    ctx.fillText("— u₀(x) initial", 8, 14);
    ctx.fillStyle = C.accent;
    ctx.fillText(`— u(x, ${time.toFixed(4)})`, 8, 28);

    // ─── heat strip (color map) ───
    ctx.fillStyle = C.textDim; ctx.font = `10px ${MONO}`;
    ctx.fillText("temperature field", 8, heatTop - 2);

    for (let i = 0; i < N; i++) {
      const px = (i / (N - 1)) * w;
      const pw = w / N + 1;
      ctx.fillStyle = tempColor(currentVals[i], yR[0], yR[1]);
      ctx.fillRect(px, heatTop, pw, heatH);
    }
    // border
    ctx.strokeStyle = C.border; ctx.lineWidth = 1;
    ctx.strokeRect(0, heatTop, w, heatH);

    // ─── spectral decay ───
    ctx.fillStyle = C.textDim; ctx.font = `11px ${MONO}`;
    ctx.fillText("Fourier mode amplitudes |ĉₖ| · e^(−4π²k²t)", 8, specTop - 4);

    if (spectralDecay.length > 0) {
      const maxMag = Math.max(...spectralDecay.map(d => d.mag0), 0.01);
      const barW = Math.max(4, (w / 22) - 4);

      for (const d of spectralDecay) {
        const bx = ((d.k - 0.5) / 21) * w;

        // original magnitude (ghost)
        const bh0 = (d.mag0 / maxMag) * (specH - 8);
        ctx.fillStyle = C.curve1 + "25";
        ctx.fillRect(bx, specTop + specH - bh0, barW, bh0);

        // decayed magnitude
        const bhT = (d.magT / maxMag) * (specH - 8);
        const decayColor = d.decay > 0.5 ? C.curve3 : d.decay > 0.1 ? C.accent : C.curve2;
        ctx.fillStyle = decayColor + "cc";
        ctx.fillRect(bx, specTop + specH - bhT, barW, bhT);

        // k label
        if (d.k <= 15 || d.k % 5 === 0) {
          ctx.fillStyle = C.textDim; ctx.font = `9px ${MONO}`;
          ctx.fillText(`${d.k}`, bx + 1, specTop + specH + 10);
        }
      }

      // decay annotation
      ctx.fillStyle = C.curve2 + "90"; ctx.font = `10px ${MONO}`;
      ctx.fillText("high k decays ∝ e^(−k²t) — fast!", w - 170, specTop + 12);
      ctx.fillStyle = C.curve3 + "90";
      ctx.fillText("low k survives longest", w - 170, specTop + 24);
    }
  }, [time, icKey, currentVals, ghostCurves, spectralDecay, showGhosts, yR]);

  const ic = INITIAL_CONDITIONS[icKey];

  return (
    <div style={{ minHeight: "100vh", background: C.bg, color: C.text, fontFamily: FONT, padding: "24px 16px" }}>
      <link href="https://fonts.googleapis.com/css2?family=EB+Garamond:ital,wght@0,400;0,500;0,600;1,400&family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet" />
      <div style={{ maxWidth: 680, margin: "0 auto" }}>
        <h1 style={{ fontSize: 28, fontWeight: 400, letterSpacing: "-0.02em", color: C.highlight, marginBottom: 4 }}>
          Heat Equation Semigroup
        </h1>
        <p style={{ color: C.textDim, fontSize: 13, marginBottom: 16, fontFamily: MONO }}>
          e<sup>tΔ</sup> — watching the Laplacian smooth
        </p>

        <div style={{ background: C.panel, borderRadius: 12, border: `1px solid ${C.border}`, padding: 18 }}>
          <p style={{ color: C.text, fontSize: 14, lineHeight: 1.6, fontFamily: FONT, marginBottom: 8 }}>
            The heat equation u<sub>t</sub> = u<sub>xx</sub> is functional analysis made physical: the solution
            operator e<sup>tΔ</sup> forms a <em>strongly continuous semigroup</em>, a one-parameter family of bounded
            operators that smooths any initial condition. Each Fourier mode decays at rate e<sup>−4π²k²t</sup>, so
            high frequencies die quadratically faster than low ones. Roughness is annihilated;
            only the coarse shape survives.
          </p>
          <MathBlock>
            u(x,t) = ∑<sub>k</sub> ĉ<sub>k</sub> · e<sup>−4π²k²t</sup> · e<sup>2πikx</sup>,{"   "}
            e<sup>tΔ</sup> : L² → C<sup>∞</sup> for t &gt; 0
          </MathBlock>

          {/* initial condition selector */}
          <div style={{ display: "flex", gap: 8, marginBottom: 8, flexWrap: "wrap" }}>
            {Object.entries(INITIAL_CONDITIONS).map(([k, v]) =>
              <Chip key={k} active={k === icKey} onClick={() => { setIcKey(k); setTime(0); setPlaying(false); }}>{v.label}</Chip>
            )}
          </div>
          <p style={{ color: C.textDim, fontSize: 12, fontFamily: MONO, marginBottom: 10 }}>{ic.desc}</p>

          <PlayControls playing={playing}
            onToggle={() => { if (time >= 0.49) setTime(0); setPlaying(!playing); }}
            onReset={() => { setTime(0); setPlaying(false); }}
            label={`t = ${time.toFixed(4)}`} />

          <Slider label="Time t" value={time} onChange={v => setTime(v)} min={0} max={0.5} step={0.0001} format={v => v.toFixed(4)} />
          <Slider label="Playback speed" value={speed} onChange={setSpeed} min={0.1} max={5} step={0.1} format={v => v.toFixed(1) + "×"} />

          <div style={{ display: "flex", gap: 8, marginBottom: 10 }}>
            <Chip active={showGhosts} onClick={() => setShowGhosts(!showGhosts)}>
              {showGhosts ? "☑" : "☐"} show time ghosts
            </Chip>
          </div>

          <div style={{ background: C.bg, borderRadius: 8, border: `1px solid ${C.border}`, overflow: "hidden", height: 520 }}>
            <canvas ref={mainRef} style={{ width: "100%", height: "100%", display: "block" }} />
          </div>

          {/* energy conservation note */}
          <div style={{ marginTop: 14, padding: "10px 14px", background: C.mathBg, borderRadius: 6, borderLeft: `2px solid ${C.curve5}` }}>
            <p style={{ color: C.text, fontSize: 13, fontFamily: FONT, lineHeight: 1.6, margin: 0 }}>
              <strong style={{ color: C.curve5 }}>What to watch for:</strong> the roughest features smooth first (high-<M>k</M> modes
              decay as e<sup>−k²t</sup>). The delta spike broadens into a Gaussian — this is the fundamental solution.
              Two separated blocks merge when their diffusion radii (~√t) overlap. The total heat ∫u dx is conserved,
              but the L² norm ‖u‖² decreases — energy dissipates. Every initial condition, no matter how rough,
              becomes infinitely smooth for any t &gt; 0.
            </p>
          </div>
        </div>

        <p style={{ color: C.textDim, fontSize: 11, marginTop: 14, textAlign: "center", fontFamily: MONO }}>
          the Laplacian as sculptor — roughness annihilated, form preserved
        </p>
      </div>
    </div>
  );
}
