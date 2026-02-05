# Code Analysis: Functional Analysis Visualization Artifacts

Technical analysis of two standalone React components for visualizing concepts from functional analysis.

**Files analyzed:**
- `functional-analysis-v3.jsx` (779 lines)
- `heat-equation.jsx` (394 lines)

---

## 1. Architecture Overview

### Component Hierarchy

**functional-analysis-v3.jsx:**

```
FunctionalAnalysisExplorer (default export)
  |-- Tab bar (7 tabs)
  |-- Active content panel (switches on activeTab)
       |-- LpGeometry
       |-- FourierConvergence
       |-- OperatorSpectra
       |-- BanachContraction
       |-- HilbertProjection
       |-- WeakStrongConvergence
       |-- CompactOperators
```

The root component (`FunctionalAnalysisExplorer`) holds a single `activeTab` state string and renders the corresponding child component via a plain object lookup (`content[activeTab]`). Each tab component is fully self-contained: it owns its own state, computes its own derived data via `useMemo`, manages its own animations via `useEffect`/`setInterval`, and renders its own canvas through the shared `useCanvas` hook. There is no cross-tab communication or shared state beyond the design system constants.

**heat-equation.jsx:**

```
HeatEquationExplorer (default export)
  |-- Header + description
  |-- Initial condition selector (Chips)
  |-- PlayControls + Sliders
  |-- Single canvas (spatial plot + heat strip + spectral decay)
  |-- Explanatory footer
```

This is a single-view component -- no tab system. All visualization happens in one canvas, partitioned into three vertical zones: the spatial plot (top 50%), a color-mapped heat strip (narrow band), and a spectral decay bar chart (bottom).

### Shared Utilities (duplicated, not imported)

Both files independently define the same utility layer. The following components and functions appear in both files with identical or near-identical implementations:

| Utility | Type | Purpose |
|---------|------|---------|
| `C` | Object literal | Color palette |
| `FONT` | String constant | Serif font stack |
| `MONO` | String constant | Monospace font stack |
| `MathBlock` | Component | Styled block for mathematical notation |
| `M` | Component | Inline math accent styling |
| `Slider` | Component | Labeled range input with formatted value display |
| `Chip` | Component | Toggle/selection button |
| `PlayControls` | Component | Play/pause/reset transport controls |
| `useCanvas` | Hook | DPR-aware canvas setup and redraw |
| `drawGrid` | Function | Axis grid renderer |
| `toS` | Function | Mathematical-to-screen coordinate transform |

**Differences between the two copies:**

- `C` in `heat-equation.jsx` adds four extra colors: `hot`, `warm`, `cool`, `cold` (for the temperature color map).
- `PlayControls` in `heat-equation.jsx` omits the `onStep` prop -- it only has play/pause and reset, no single-step.
- `drawGrid` in `heat-equation.jsx` defaults to `xRange: [0, 1]` (spatial domain) instead of `[-2, 2]`, and omits the axes lines (no explicit origin cross drawn).
- `functional-analysis-v3.jsx` imports `useCallback` from React but never uses it.

---

## 2. Tab/Visualization Inventory

### functional-analysis-v3.jsx -- Seven Tabs

#### Tab 1: "Lp Geometry" (`LpGeometry`)

**Mathematical concept:** Unit balls in l^p spaces (finite-dimensional R^2) as p varies.

**What it shows:** The boundary of {x in R^2 : ||x||_p <= 1} for a user-selected p, with ghost outlines of the L^1 (diamond), L^2 (circle), and L^inf (square) unit balls for comparison. As p decreases below 1, the ball becomes non-convex (star-shaped); at p = 1 it is a diamond; at p = 2 a circle; as p -> infinity it approaches a square.

**State:** Single slider for p (range 0.3 to 20).

**Rendering:** Parametric curve via 600 sample points around the angle theta, computing r(theta) = (|cos(theta)|^p + |sin(theta)|^p)^{-1/p}. The active ball is drawn with a glow effect (canvas shadowBlur). A semi-transparent fill is drawn inside the active ball.

#### Tab 2: "Fourier" (`FourierConvergence`)

**Mathematical concept:** Fourier series convergence, Gibbs phenomenon, L^2 convergence vs. pointwise behavior.

**What it shows:** Partial Fourier sums S_N(x) converging to a target function (square wave, sawtooth, or triangle), with harmonics added one at a time via animation. A secondary panel below shows the L^2 error ||f - S_N||_2 as a function of N.

**State:** `nTerms` (1-50), `targetKey` (square/sawtooth/triangle), `playing` (boolean). Animation via `setInterval` at 280ms increments.

**Rendering:** Target function in dashed grey, current partial sum in accent gold with glow. The k-th harmonic being added is shown in semi-transparent purple as a "midway" curve. Below: L^2 error plotted as a line graph with a highlighted dot at the current N.

**Mathematical computation:** Fourier coefficients computed numerically via midpoint quadrature with M=1000 sample points. The `fourierCoeffs` function computes both a_k and b_k for the real Fourier representation. The L^2 error is computed as sqrt(sum(|f(x_i) - S_N(x_i)|^2) / M) using 400 sample points.

#### Tab 3: "Spectra" (`OperatorSpectra`)

**Mathematical concept:** Spectrum of bounded linear operators on Hilbert space -- self-adjoint (real spectrum), compact (spectrum clustering at 0), and general (spectrum in complex plane).

**What it shows:** Eigenvalues plotted in the complex plane (Re(lambda) vs Im(lambda)). For self-adjoint operators, all eigenvalues lie on the real axis (highlighted with a translucent band). For compact operators, eigenvalues cluster near the origin (marked with a dashed circle). General operators scatter across the complex plane.

**State:** `opType`, `dim` (5-80), `seed` for randomized regeneration.

**Rendering:** Grid in the complex plane, dots with radial glow halos, opacity fading by index. Uses a simple linear congruential generator for deterministic pseudo-random eigenvalue placement.

#### Tab 4: "Contraction" (`BanachContraction`)

**Mathematical concept:** Banach fixed-point theorem -- contraction mappings on complete metric spaces converge to a unique fixed point.

**What it shows:** The classic "cobweb diagram": the graph of the contraction mapping y = T(x), the identity line y = x, and the iteration sequence x_0, T(x_0), T(T(x_0)), ... visualized as alternating vertical and horizontal line segments spiraling toward the fixed point.

**State:** `mapKey` (cos(x), sqrt(x+1)/2, x/3+0.4), `x0` (initial point), `maxIter` (1-30), `vis` (animated step count), `playing`.

**Rendering:** Identity line dashed, mapping curve in blue, cobweb lines in accent gold with varying opacity (latest step fully opaque). Fixed point approximation displayed numerically.

#### Tab 5: "Projection" (`HilbertProjection`)

**Mathematical concept:** Orthogonal projection onto finite-dimensional subspaces of L^2, Gram-Schmidt orthonormalization, best approximation theorem.

**What it shows:** A target function f(x) and its projection pi(f) onto the first n basis vectors of the Gram-Schmidt-orthonormalized monomial basis {1, x, x^2, ...}. A residual plot below shows f(x) - pi(f)(x), which is orthogonal to the subspace.

**State:** `nBasis` (1-10), `targetKey` (Gaussian, |x|, x^3-x, hat function).

**Rendering:** Two-panel canvas: upper shows target (dashed) and projection (green, glowing), lower shows residual (red). L^2 error displayed numerically. Gram-Schmidt computation performed on 500-point discretization of [-1, 1].

#### Tab 6: "Weak vs Strong" (`WeakStrongConvergence`)

**Mathematical concept:** Weak convergence vs. strong convergence in Hilbert spaces. The sequence f_n(x) = sin(nx) converges weakly to 0 in L^2 (inner products with any fixed function tend to 0 by the Riemann-Lebesgue lemma) but ||f_n|| = sqrt(pi) does not converge to 0.

**What it shows:** Three-panel canvas. Top: the oscillating sin(nx) plotted against a user-chosen test function g. Middle: bar chart of inner products <f_n, g> approaching 0 as n grows. Bottom: dot plot of ||f_n||_2 remaining constant at sqrt(pi).

**State:** `n` (1-40), `testKey` (step, ramp, Gaussian, sin(3x)), `playing`.

**Rendering:** Inner products computed by midpoint quadrature (M=2000 on [-pi, pi]). Each bar in the inner product chart is colored, with the current n highlighted. The constant norm sqrt(pi) is shown as a dashed reference line.

#### Tab 7: "Compact Ops" (`CompactOperators`)

**Mathematical concept:** Compact operators, singular value decomposition (SVD), the relationship between singular value decay and operator class (trace-class, Hilbert-Schmidt, compact, bounded but non-compact).

**What it shows:** Two-panel layout. Left: geometric view of the unit ball being transformed through the SVD stages (V* rotation, Sigma scaling, U rotation), showing how the circle becomes an ellipse whose semi-axes are the singular values. Right: bar chart of singular values for the selected preset.

**State:** `presetKey` (trace-class, Hilbert-Schmidt, compact, finite-rank, bounded-not-compact), `nDims` (4-24), `viewPair` (which 2D projection to view), `angle` (rotation parameter), `animStep` (0-3 for SVD stages), `playing`.

**Rendering:** 48 points on the unit circle undergo staged transformation (V*, Sigma, U), color-coded by hue based on angle. The full image ellipse is drawn in accent gold. Right panel shows horizontal bars for each singular value with operator/Hilbert-Schmidt/trace norms computed at bottom.

### heat-equation.jsx -- Single View

#### Heat Equation Semigroup

**Mathematical concept:** The heat equation u_t = u_xx on [0,1] with periodic boundary conditions, solved via Fourier series. The solution operator e^{tDelta} is a strongly continuous semigroup that maps L^2 to C^infinity for t > 0.

**What it shows:** Three vertically stacked visualizations in a single canvas:

1. **Spatial plot** (top 50%): The solution u(x,t) at the current time, with optional "ghost curves" showing snapshots at earlier times (t = 0, 0.001, 0.005, 0.02, 0.05, 0.15).

2. **Heat strip** (narrow band): A 1D color-mapped representation of the temperature field, using a cold-blue to warm-amber to hot-orange colormap.

3. **Spectral decay** (bottom): Bar chart showing the amplitude of each Fourier mode k at the initial time (ghost bar) versus current time (colored bar). Color encodes decay: green for barely decayed (>50%), amber for moderate decay, red for highly decayed (<10%).

**State:** `icKey` (6 initial conditions: step, delta-like spike, sawtooth, two blocks, high-frequency sum, rough noise), `time` (0 to 0.5), `speed` (playback rate), `playing`, `showGhosts` (toggle for ghost curves).

**Animation system:** Uses `requestAnimationFrame` instead of `setInterval` -- smoother and frame-rate-independent. Time advances as `dt * speed * 0.01` per frame.

**Initial conditions:**

| Key | Function | Physical interpretation |
|-----|----------|----------------------|
| `step` | x < 0.5 ? 1 : 0 | Sharp discontinuity |
| `spike` | exp(-200(x-0.5)^2) | Approximate delta function |
| `sawtooth` | 2(x - floor(x + 0.5)) | Periodic ramp |
| `twoblock` | Two rectangular pulses | Two separated heat sources |
| `sine_sum` | Sum of 3 sinusoids | High-frequency spectral content |
| `noise` | Piecewise linear random | Rough/jagged profile |

---

## 3. Technical Implementation Details

### Canvas Rendering Approach

Both files use the same `useCanvas` custom hook pattern:

1. A `<canvas>` element is sized via CSS to fill its container.
2. On each render triggered by dependency changes, the hook reads `getBoundingClientRect()` for logical pixel dimensions.
3. The canvas backing store is scaled by `devicePixelRatio` for crisp rendering on HiDPI displays.
4. The context is scaled by DPR, then cleared, then the draw callback is invoked with the logical width and height.
5. All drawing is done in logical (CSS) pixels -- the DPR scaling is transparent to the draw functions.

Coordinate mapping is handled by the `toS(x, y, w, h, xR, yR)` function, which maps from mathematical coordinates (in ranges xR and yR) to screen pixels. The y-axis is flipped (screen y increases downward, math y increases upward).

All rendering is immediate-mode Canvas 2D -- no retained-mode graphics, no WebGL, no SVG. Each re-render wipes the canvas and redraws everything from scratch. For the static/slider-driven tabs this is efficient enough; for the animated tabs, performance depends on the number of sample points and the complexity of the computation.

### Animation System

**functional-analysis-v3.jsx** uses `setInterval` for all animations:
- Fourier: 280ms interval, incrementing nTerms by 1
- Banach: 400ms interval, incrementing vis by 1
- Weak/Strong: 350ms interval, incrementing n by 1
- Compact: 900ms interval, incrementing animStep by 1

Each interval callback uses the functional updater form of `setState` to avoid stale closures. Cleanup is handled via the `useEffect` return value.

**heat-equation.jsx** uses `requestAnimationFrame`:
- Uses `performance.now()` for frame-accurate delta-time computation
- Time advances continuously: `next = t + dt * speed * 0.01`
- Caps at t = 0.5 and auto-pauses
- Smoother animation suitable for the continuous time parameter

This is a notable design difference. The `setInterval` approach in v3 works well for discrete-step animations (add a harmonic, advance an iteration) but would produce jerky results for continuous time evolution. The `requestAnimationFrame` approach in the heat equation is the correct choice for that use case.

### State Management

Pure React local state via `useState`. No context, no reducers, no external state management. Each tab component is completely independent. Derived data is computed via `useMemo` with appropriate dependency arrays.

Heavy computations memoized with `useMemo`:
- Fourier coefficients (recomputed only when target function changes)
- Gram-Schmidt basis (computed once, no dependencies change)
- Ghost curves in heat equation (recomputed only when initial condition changes)
- Error arrays and spectral decay data

No `useCallback` is actually needed or used for any of the draw functions (they are re-created each render but passed to `useCanvas` which only cares about the dependency array, not referential identity of the function).

---

## 4. Mathematical Accuracy Assessment

### Lp Geometry -- Correct

The parametric formula for the l^p unit ball boundary is:

```
r(theta) = (|cos(theta)|^p + |sin(theta)|^p)^{-1/p}
```

This is mathematically correct. The transition to the L^infinity case at p >= 50 using `1/max(|cos|, |sin|)` is a reasonable numerical approximation (at p = 50, the two formulas differ by negligible amounts, and the sup-norm formula avoids overflow from raising numbers to the 50th power).

**Note:** For p < 1, the "norm" is actually a quasi-norm (the triangle inequality fails), and the unit "ball" is non-convex. The code handles this correctly -- the visualization shows the star-shaped sets. The slider goes down to p = 0.3, which is mathematically valid (the formula still defines a set, it just is not a norm for p < 1). The description text does not clarify this distinction.

### Fourier Series -- Correct with minor note

The Fourier coefficients are computed via numerical quadrature (midpoint rule, M = 1000 points). The formula used:

```
a_k = (2/M) * sum(f(x_i) * cos(k * x_i))  for k >= 1
a_0 = (1/M) * sum(f(x_i))
b_k = (2/M) * sum(f(x_i) * sin(k * x_i))  for k >= 1
```

This is a valid discretization of the standard real Fourier coefficient formulas:

```
a_k = (1/pi) * integral_{-pi}^{pi} f(x) cos(kx) dx
b_k = (1/pi) * integral_{-pi}^{pi} f(x) sin(kx) dx
```

The 2/M factor arises because the integral over [-pi, pi] has length 2*pi, each sample has weight 2*pi/M, and the normalization factor is 1/pi, giving 2/M total. This checks out.

**The L^2 error computation** uses `sqrt(sum(|d_i|^2) / M)` with 400 points. This approximates `sqrt((1/(2*pi)) * integral |f - S_N|^2 dx)`. The 1/(2*pi) normalization is approximated by dividing by M without the 2*pi factor, so it is an unnormalized RMS error. This is fine for showing the convergence trend but the absolute values are not the standard L^2 norm.

**Gibbs phenomenon note:** The description correctly states "Gibbs overshoots persist at ~9%." The actual Gibbs overshoot for a square wave is approximately 8.95% of the jump, which rounds to 9%. Accurate.

### Operator Spectra -- Illustrative (not computed from actual operators)

The eigenvalues are not computed from actual matrices. They are generated to illustrate the spectral properties:
- Self-adjoint: Random real values (correct -- self-adjoint operators have real spectrum)
- Compact: Values of the form 1/k^2 with small random perturbation (correct -- compact operator spectra accumulate at 0)
- General: Random points in the complex plane (correct -- no constraint on spectrum location)

This is pedagogically appropriate. Computing actual eigenvalues of interesting operators would be far more complex and the educational value is the same.

### Banach Contraction -- Correct

The three contraction maps are valid:
- `cos(x)` on approximately [-0.5, 1.5]: cos is Lipschitz with constant |sin(x)| < 1 on this domain, so it is a contraction. The fixed point is the Dottie number (approximately 0.7390851332).
- `sqrt(x+1)/2` on [0, 1]: derivative is `1/(4*sqrt(x+1))` which is at most 1/4 < 1.
- `x/3 + 0.4` on [0, 1]: derivative is 1/3 < 1, fixed point at x = 0.6.

The cobweb diagram construction is standard and correctly implemented: vertical line from (x_n, x_n) to (x_n, f(x_n)), then horizontal line from (x_n, f(x_n)) to (f(x_n), f(x_n)). **One minor note:** on the first iteration, the vertical line goes from (x_0, 0) to (x_0, f(x_0)) -- starting from the x-axis rather than the diagonal. This is the conventional cobweb start, correctly implemented via the `i === 0` check.

### Hilbert Projection -- Correct

The Gram-Schmidt process is correctly implemented: for each new basis vector x^k, subtract projections onto all previously orthonormalized vectors, then normalize. The inner products use the discrete approximation `sum(v_i * u_i) / M` as a proxy for the L^2 inner product on [-1, 1]. The normalization factor is consistent.

The projection formula `pi(f) = sum_k <f, e_k> e_k` and the claim `(f - pi(f)) perp V` are standard results of the Hilbert space projection theorem. The visualization correctly shows the residual becoming more oscillatory as the number of basis functions increases (the projection captures the low-order polynomial structure, leaving the high-frequency residual).

### Weak vs. Strong Convergence -- Correct

The claim that sin(nx) converges weakly to 0 in L^2(-pi, pi) is correct by the Riemann-Lebesgue lemma. The claim that ||sin(nx)||_2 = sqrt(pi) is correct: integral of sin^2(nx) over (-pi, pi) = pi.

The inner product computation uses M = 2000 quadrature points with weight `2*pi/M` per point. The computation:
```
ip = sum(sin(k*x_i) * g(x_i)) * (2*pi/M)
```
This correctly approximates `integral_{-pi}^{pi} sin(kx) g(x) dx`.

The norm computation: `sqrt(sum(sin^2(kx_i)) * 2*pi/M)` correctly approximates `sqrt(integral sin^2(kx) dx) = sqrt(pi)`. The displayed values converge to sqrt(pi) approx 1.7725 as expected.

### Compact Operators / SVD -- Correct

The SVD decomposition T = U * Sigma * V* is correctly animated in stages:
1. Start with the unit ball
2. Apply V* (rotation by -angle)
3. Apply Sigma (scale axes by singular values)
4. Apply U (rotation by +angle)

The singular value presets correctly illustrate the classification:
- Trace class: sigma_k ~ 1/k, sum sigma_k < infinity
- Hilbert-Schmidt: sigma_k ~ 1/sqrt(k), sum sigma_k^2 < infinity but sum sigma_k = infinity
- Compact: sigma_k ~ 1/k^0.3, sigma_k -> 0 but slowly
- Finite rank: only first 3 nonzero
- Not compact: sigma_k = 0.8 constant (bounded operator that is NOT compact)

The norm computations at the bottom (operator norm = sigma_1, Hilbert-Schmidt norm = sqrt(sum sigma_k^2), trace norm = sum sigma_k) are all correct.

### Heat Equation -- Correct

The Fourier solution of the heat equation on [0,1] with periodic boundary conditions:

```
u(x,t) = sum_k c_k * exp(-4*pi^2*k^2*t) * exp(2*pi*i*k*x)
```

is correct. The coefficients use the complex Fourier transform:

```
c_k = integral_0^1 f(x) * exp(-2*pi*i*k*x) dx
```

approximated by midpoint quadrature with M = 2000 points. The evaluation function correctly takes the real part of the complex sum (since u(x,t) is real-valued for real initial conditions, the imaginary parts cancel).

The claim that `e^{tDelta}: L^2 -> C^infinity for t > 0` is a standard theorem of PDE theory and is correctly stated.

**The decay formula** `e^{-4*pi^2*k^2*t}` is correct for the periodic heat equation on [0,1]. For the equation u_t = u_xx with Fourier basis e^{2*pi*i*k*x}, the eigenvalue of d^2/dx^2 is -(2*pi*k)^2 = -4*pi^2*k^2.

The temperature-to-color function `tempColor` maps linearly from cold (blue) to hot (orange/amber). The mapping is:
- R: 42 + 213*t (42 to 255)
- G: 82 + 70*t - 80*t^2 (82, peaks around 117 at t~0.44, then 72 at t=1)
- B: 152 - 120*t (152 to 32)

This produces a reasonable cold-blue to warm-amber palette.

---

## 5. Shared Design System

### Color Palette (the `C` object)

| Token | Hex | Role |
|-------|-----|------|
| `bg` | `#0a0b0f` | Page background, near-black |
| `panel` | `#12131a` | Card/panel background |
| `panelDeep` | `#0d0e14` | Deeper panel variant (v3 only) |
| `border` | `#1e2030` | Panel borders, dividers |
| `text` | `#c8cad0` | Primary body text, light grey |
| `textDim` | `#6b6e7a` | Secondary/label text, medium grey |
| `accent` | `#e8a44a` | Primary accent, warm amber/gold |
| `accentDim` | `#e8a44a44` | Accent at 27% opacity (button fills) |
| `curve1` | `#5b9bd5` | Blue -- primary data curve |
| `curve2` | `#e06c75` | Red/coral -- error, residual |
| `curve3` | `#98c379` | Green -- projections, verified |
| `curve4` | `#c678dd` | Purple -- harmonics, general spectra |
| `curve5` | `#56b6c2` | Cyan/teal -- test functions, annotations |
| `gridLine` | `#252738` | Grid lines, very subtle |
| `highlight` | `#ffffff` | Pure white -- titles only |
| `mathBg` | `#0e0f16` | Math block background |
| `hot` | `#ff6b35` | Hot temperature (heat-equation only) |
| `warm` | `#e8a44a` | Warm temperature (heat-equation only) |
| `cool` | `#5b9bd5` | Cool temperature (heat-equation only) |
| `cold` | `#2a5298` | Cold temperature (heat-equation only) |

The palette is a dark-mode scheme inspired by code editor themes (the curve colors closely match One Dark Pro: `#e06c75` for red, `#98c379` for green, `#c678dd` for purple, `#56b6c2` for cyan). The warm amber accent (`#e8a44a`) creates a distinctive identity that differentiates these from generic chart visualizations.

**Note:** The `hot`, `warm`, `cool`, `cold` colors defined in the heat equation's `C` object are never actually referenced by name in the code. The `tempColor` function computes its own RGB values procedurally. These constants appear to be unused vestigial definitions.

### Typography

- **FONT** (`'EB Garamond', Georgia, serif`): Used for descriptive text, math blocks, and headings. EB Garamond is a high-quality open-source Garamond revival, lending the interface an academic/textbook quality.
- **MONO** (`'IBM Plex Mono', monospace`): Used for labels, values, canvas annotations, control text, and tab labels. IBM Plex Mono is a clean, readable monospace face.

Both fonts are loaded via a `<link>` tag to Google Fonts, rendered inline inside the component's JSX. This is unconventional (typically done in HTML `<head>` or via CSS `@import`) but works in artifact sandbox environments where you have no control over the host document.

### Shared Components

**MathBlock:** A styled `<div>` for displaying mathematical formulas. Dark background (`#0e0f16`), left border accent line, italic serif text. Used for the main formula in each tab/section.

**M:** An inline `<span>` for mathematical variables within running text. Italic, accent-colored. Minimal wrapper for semantic clarity.

**Slider:** A labeled range input. Displays label (left, serif) and formatted value (right, monospace accent). Uses the browser's native `<input type="range">` with `accentColor` for the track/thumb tinting.

**PlayControls:** Transport controls for animations. Renders play/pause, optional step, optional reset buttons. The active (playing) button gets the accent background treatment. A label string shows current state (e.g., "harmonic 5/50" or "t = 0.0123").

**Chip:** A toggle/selection button, used for choosing presets (initial conditions, target functions, operator types). Active state: accent border and translucent accent background. Inactive: border color, dim text.

**useCanvas:** Custom hook that handles the canvas lifecycle:
1. Creates a ref
2. On dependency change: reads bounding rect, sets backing store size to CSS size * DPR, scales context, clears, invokes draw callback
3. Returns the ref for attachment to the `<canvas>` element

**drawGrid:** Draws a grid of vertical and horizontal lines at regular intervals, given x and y ranges. The v3 version also draws emphasized axis lines through the origin.

**toS:** Maps mathematical (x, y) to screen coordinates (px_x, px_y), with y-axis flipped.

---

## 6. Dependencies

### Required

- **React** (useState, useEffect, useRef, useMemo, useCallback) -- the sole runtime dependency.

### Not Required

- No charting library (D3, Chart.js, Recharts, etc.)
- No math library (math.js, numeric.js, etc.)
- No animation library (framer-motion, react-spring, etc.)
- No CSS framework or styled-components
- No build-time dependencies (TypeScript, SASS, etc.)

All mathematical computation is implemented from scratch in plain JavaScript. All rendering is native Canvas 2D API. All styling is inline.

### External Resources (loaded at runtime)

- Google Fonts: `EB Garamond` (400, 500, 600 weights, plus 400 italic) and `IBM Plex Mono` (400, 500 weights), loaded via `<link>` in the component JSX.

---

## 7. Deployment Notes

### Target Environment: Artifact Sandboxes

These components are designed for Claude's artifact system (or similar React sandbox environments like CodeSandbox, StackBlitz, or custom iframe-based renderers). Key indicators:

1. **Single-file components** with no imports beyond React
2. **Default export** pattern (expected by artifact renderers)
3. **Google Fonts loaded inline** rather than via document head
4. **No routing, no external state, no side effects** beyond canvas rendering
5. **Inline styles throughout** -- no CSS files needed
6. **Self-contained mathematical computation** -- no external data or API calls

### Running Standalone

To run these as standalone applications:

1. **Create React App / Vite:** Create a new project, place the JSX file as the default export of a route or the App component.

2. **Minimal HTML harness:**
   ```html
   <div id="root"></div>
   <script type="module">
     import React from 'react';
     import ReactDOM from 'react-dom/client';
     import App from './functional-analysis-v3.jsx';
     ReactDOM.createRoot(document.getElementById('root')).render(React.createElement(App));
   </script>
   ```

3. **Move font loading:** Extract the Google Fonts `<link>` tag from the component JSX into the HTML `<head>` for proper loading behavior (avoid FOUC).

4. **Combine into one app:** The shared utility layer could be extracted into a common module, and both explorers could be rendered as sibling routes or tabs in a unified application.

### Potential Issues for Standalone Deployment

- The `useCanvas` hook's dependency array is passed as a bare expression (`deps`), not spread. React's `useEffect` expects an array, which is what `deps` is, so this works. However, the ESLint `react-hooks/exhaustive-deps` rule will flag this as unverifiable because the linter cannot statically analyze the contents of a dynamically-passed array.

- The `<link>` tag rendered inside the component body will cause the browser to re-request the stylesheet on every mount. In a sandbox this is fine (cached after first load), but in a production app it would be better placed in the document head.

- Canvas rendering is triggered by React state changes via `useEffect`. There is no resize observer -- if the container size changes (e.g., window resize), the canvas will not re-render until the next state change. Adding a ResizeObserver would fix this for production use.

---

## 8. Code Quality Observations

### Strengths

**Mathematical rigor:** The formulas are correctly implemented. The code demonstrates genuine understanding of the mathematics -- not just plotting functions, but correctly computing Fourier coefficients, Gram-Schmidt orthogonalization, inner products in function spaces, and SVD decompositions.

**Visual design:** The dark palette with warm accent creates a cohesive, distinctive aesthetic. The use of glow effects (shadowBlur), ghost/reference curves (dashed lines at reduced opacity), and multi-panel layouts gives each visualization rich contextual information beyond the primary data.

**Pedagogical layering:** Each tab pairs a mathematical formula (MathBlock), a plain-English description, interactive controls, and a visualization. The animations reveal temporal structure (harmonics landing one by one, contraction iterations spiraling inward, heat diffusing over time) that static diagrams cannot convey.

**Performance-conscious memoization:** Heavy computations (Fourier coefficients, Gram-Schmidt basis, ghost curves) are memoized with correct dependency arrays. The code avoids recomputing expensive values on every frame.

**Self-contained architecture:** Zero external dependencies beyond React means these will work in any React sandbox environment without configuration. The entire mathematical and rendering stack is visible in the source.

### Observations and Minor Issues

**Code duplication:** The shared utility layer (C, FONT, MONO, MathBlock, M, Slider, Chip, PlayControls, useCanvas, drawGrid, toS) is copy-pasted between the two files. In a multi-file project, these should be extracted into a shared module. However, for standalone artifact deployment, duplication is the correct choice (each file must be self-contained).

**Unused import:** `functional-analysis-v3.jsx` imports `useCallback` from React on line 1 but never uses it.

**Unused color constants:** `heat-equation.jsx` defines `C.hot`, `C.warm`, `C.cool`, `C.cold` but the `tempColor` function computes colors procedurally without referencing them.

**Dense formatting:** Many lines are very long, with multiple statements packed onto single lines using semicolons. This is a deliberate compactness choice for artifact-sized files (keeping total line count manageable) but reduces readability for maintenance. Examples:

```js
// Line 72: Multiple drawing commands on one line
for (let x = Math.ceil(xR[0] / step) * step; x <= xR[1]; x += step) { const px = (x - xR[0]) * xS; ctx.beginPath(); ctx.moveTo(px, 0); ctx.lineTo(px, h); ctx.stroke(); }
```

**No error boundaries:** If any computation produces NaN or Infinity (e.g., at p = 0 in Lp geometry, or division by zero), the canvas rendering silently fails. The code avoids most of these cases (p minimum is 0.3, norm checks against > 1e-10), but there are no explicit guards in the rendering pipeline.

**Hardcoded layout proportions:** Canvas regions are divided by magic fractions (e.g., `h * 0.62`, `h * 0.50`, `h * 0.38`). These work well at the default canvas size but may not adapt gracefully to very different aspect ratios.

**Animation cleanup:** All animation effects properly clean up (returning cancel functions from useEffect), which prevents memory leaks and zombie intervals. This is correctly done throughout.

**Consistent API:** The Slider, Chip, and PlayControls components have clean, consistent prop interfaces. The useCanvas hook provides a good abstraction over the DPR-aware canvas setup boilerplate.

### Overall Assessment

These are well-crafted educational visualizations. The code prioritizes correctness, visual quality, and self-containment over maintainability -- which is the right trade-off for artifact-sized interactive demonstrations. The mathematical content is accurate, the visual design is cohesive, and the interactive elements meaningfully enhance understanding of the underlying concepts. The two files together cover a substantial arc of functional analysis pedagogy: from finite-dimensional geometry (Lp balls) through infinite-dimensional phenomena (Fourier convergence, weak convergence, compact operators) to PDE applications (the heat equation as semigroup).
