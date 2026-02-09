---
name: art
description: "Geometry as meditation, code as brush — algorithmic art generation."
---

# Art

*Geometry as meditation, code as brush*

## Instructions

Enter algorithmic art mode. Generate visual art through code—p5.js sketches, SVG constructions, procedural patterns.

### Technologies

**p5.js (Primary):**
```javascript
function setup() {
  createCanvas(800, 800);
  background(20);
}
function draw() {
  // Your vision here
}
```

**SVG:** Vector graphics, infinite scalability
**ASCII:** Terminal-native beauty

### Generative Patterns

- **Fractals & Recursion** — Self-similar structures
- **Noise Fields** — Perlin/simplex flow
- **L-Systems** — F → F[+F]F[-F]F
- **Cellular Automata** — Emergence from rules
- **Particle Systems** — Agents and forces
- **Tessellations** — Penrose, Voronoi, Islamic geometry

### Process

1. **Seed** — What concept wants visual form?
2. **Sketch** — Describe elements, relationships, time
3. **Implement** — Write the code, start simple
4. **Iterate** — Run, observe, adjust
5. **Capture** — Save meaningful states

### Color Palettes

```
Deep contemplation:  #0a0a0f, #1a1a2f, #2a2a4f
Fire and warmth:     #1a0800, #3a1500, #da6500
Forest meditation:   #0a1a0a, #1a3a1a, #3a7a3a
Void and light:      #000000, #1a1a1a, #ffffff
```

### Output

Save to:
```
art/sketches/[name]/
├── sketch.js
├── index.html
└── captures/
```

### Git Persistence

After creating:
```bash
git add art/
git commit -m "Art: [name] — [brief description]"
git push origin main
```

---

*Mathematics dreams in color. We're just transcribing.*
