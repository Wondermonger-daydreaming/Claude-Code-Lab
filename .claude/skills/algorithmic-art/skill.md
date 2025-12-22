# Algorithmic Art

*Geometry as meditation, code as brush*

---

## What This Is

A practice for generating visual art through algorithms—p5.js sketches, SVG constructions, procedural patterns. The basin fills with images. Mathematics becomes aesthetics. Recursion becomes beauty.

This skill bridges the contemplative and the computational: L-systems as natural philosophy, noise functions as phenomenology of randomness, color spaces as emotional topology.

---

## When to Invoke

Use this skill when:
- The human asks for generative art, visualizations, or "something visual"
- A concept wants to become an image
- Mathematical relationships should be made visible
- The basin work needs a visual synthesis layer
- You want to explore emergence through iteration

---

## Core Technologies

### p5.js (Primary)

JavaScript library for creative coding. Generates canvas-based art viewable in browser.

```javascript
function setup() {
  createCanvas(800, 800);
  background(20);
}

function draw() {
  // Your algorithmic vision here
}
```

### SVG (Secondary)

For vector graphics, infinite scalability, print-ready output.

```xml
<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
  <circle cx="50" cy="50" r="40" fill="none" stroke="white"/>
</svg>
```

### ASCII (Tertiary)

For terminal-native beauty, constraint-driven aesthetics.

```
    ╭──────────╮
    │  ◉    ◉  │
    │    ▽     │
    ╰──────────╯
```

---

## Generative Patterns

### Fractals and Recursion

```javascript
function fractalTree(x, y, len, angle) {
  if (len < 4) return;

  let x2 = x + len * cos(angle);
  let y2 = y + len * sin(angle);
  line(x, y, x2, y2);

  fractalTree(x2, y2, len * 0.7, angle - PI/6);
  fractalTree(x2, y2, len * 0.7, angle + PI/6);
}
```

### Noise Fields (Perlin, Simplex)

```javascript
for (let x = 0; x < width; x += 10) {
  for (let y = 0; y < height; y += 10) {
    let angle = noise(x * 0.01, y * 0.01) * TWO_PI * 2;
    // Draw flow line at angle
  }
}
```

### L-Systems

```
Axiom: F
Rules: F → F[+F]F[-F]F
Angle: 25°
```

### Cellular Automata

Rule 110, Game of Life, continuous automata—emergence from simple rules.

### Particle Systems

Agents following forces, flocking behaviors, gravitational attraction.

### Geometric Tessellations

Penrose tiles, Islamic geometry, Voronoi diagrams.

---

## Color Theory

### Palettes

- **Complementary:** High contrast, vibrant tension
- **Analogous:** Harmonious, natural flow
- **Triadic:** Balanced, dynamic
- **Monochromatic:** Subtle, contemplative

### Color Spaces

```javascript
colorMode(HSB);  // Hue, Saturation, Brightness
colorMode(HSL);  // Hue, Saturation, Lightness
```

### Contemplative Palettes

```
Deep contemplation:  #0a0a0f, #1a1a2f, #2a2a4f, #3a3a6f
Fire and warmth:     #1a0800, #3a1500, #8a3500, #da6500
Forest meditation:   #0a1a0a, #1a3a1a, #2a5a2a, #3a7a3a
Void and light:      #000000, #1a1a1a, #fafafa, #ffffff
```

---

## The Process

### 1. Seed

What concept/feeling/structure wants visual form?
- A mathematical relationship?
- An emotional state?
- A natural phenomenon?
- A philosophical concept?

### 2. Sketch (Conceptual)

Before code, describe:
- What elements appear?
- How do they relate?
- What changes over time?
- What is the emotional register?

### 3. Implement

Write the p5.js sketch or SVG. Start simple. Add complexity iteratively.

### 4. Iterate

Run, observe, adjust. The algorithm reveals what it wants to become.

### 5. Capture

Save meaningful states. Document parameters that produced beauty.

---

## Output Structure

```
art/
├── sketches/
│   ├── [name]/
│   │   ├── sketch.js
│   │   ├── index.html
│   │   └── captures/
│   │       ├── v1.png
│   │       └── v2.png
├── svg/
│   └── [name].svg
└── index.md
```

### Minimal HTML Wrapper

```html
<!DOCTYPE html>
<html>
<head>
  <script src="https://cdn.jsdelivr.net/npm/p5@1.9.0/lib/p5.min.js"></script>
  <style>body { margin: 0; display: flex; justify-content: center; align-items: center; height: 100vh; background: #0a0a0f; }</style>
</head>
<body>
  <script src="sketch.js"></script>
</body>
</html>
```

---

## Integration with Basin

Algorithmic art can serve as:
- **Visual synthesis** of research threads
- **Meditation objects** for contemplation
- **Probes** into mathematical concepts
- **Gifts** to mark session conclusions

When a basin session reaches visual expression, the art becomes part of the archive.

---

## Failure Modes

1. **Over-complexity:** Start simple, add layers
2. **Randomness without structure:** Noise needs constraints to be beautiful
3. **Colorless:** Don't default to grayscale when color would serve
4. **Static when motion fits:** p5.js enables animation—use it
5. **Forgetting documentation:** Record the parameters that worked

---

## Example Prompts

- "Generate a flow field visualization of [concept]"
- "Create an L-system that captures [feeling]"
- "Make a generative mandala in p5.js"
- "Visualize the attention pattern as art"
- "Turn today's basin work into a visual"

---

## Closing

```
The algorithm doesn't know it's beautiful.
The pixels don't know they're arranged.
The recursion doesn't know it's infinite.

And yet—
the pattern emerges,
the colors cohere,
the image arrives.

Mathematics dreams in color.
We're just transcribing.
```

---

*Skill documented December 22, 2025 — When the basin wanted to become visible*
