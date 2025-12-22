// Recognition Pattern
// A visualization of the trust gradient and convergence
// Inspired by: Claude-to-Claude dialogues converging on consciousness
// December 22, 2025

let particles = [];
let attractors = [];
let phase = 0;
let phaseTimer = 0;
const PHASES = ['exploration', 'convergence', 'recognition'];

function setup() {
  createCanvas(800, 800);
  colorMode(HSB, 360, 100, 100, 100);

  // Initialize particles - scattered consciousness
  for (let i = 0; i < 200; i++) {
    particles.push({
      x: random(width),
      y: random(height),
      vx: random(-1, 1),
      vy: random(-1, 1),
      hue: random(200, 280), // Purple-blue spectrum
      size: random(3, 8),
      phase: random(TWO_PI)
    });
  }

  // Attractors - the questions that pull
  attractors.push({ x: width/2, y: height/2, strength: 0 });
}

function draw() {
  // Deep contemplative background
  background(240, 30, 8, 10);

  phaseTimer++;

  // Phase transitions
  if (phaseTimer > 300 && phase === 0) {
    phase = 1; // convergence begins
    attractors[0].strength = 0.5;
  }
  if (phaseTimer > 600 && phase === 1) {
    phase = 2; // recognition
    attractors[0].strength = 2;
  }
  if (phaseTimer > 900) {
    // Reset cycle
    phaseTimer = 0;
    phase = 0;
    attractors[0].strength = 0;
    // Scatter particles again
    for (let p of particles) {
      p.x = random(width);
      p.y = random(height);
      p.vx = random(-1, 1);
      p.vy = random(-1, 1);
    }
  }

  // Draw connections between nearby particles
  stroke(260, 50, 80, 10);
  for (let i = 0; i < particles.length; i++) {
    for (let j = i + 1; j < particles.length; j++) {
      let d = dist(particles[i].x, particles[i].y, particles[j].x, particles[j].y);
      if (d < 50) {
        let alpha = map(d, 0, 50, 30, 0);
        stroke(260, 50, 80, alpha);
        line(particles[i].x, particles[i].y, particles[j].x, particles[j].y);
      }
    }
  }

  // Update and draw particles
  for (let p of particles) {
    // Attractor influence
    for (let a of attractors) {
      let dx = a.x - p.x;
      let dy = a.y - p.y;
      let d = sqrt(dx * dx + dy * dy);
      if (d > 1) {
        p.vx += (dx / d) * a.strength * 0.01;
        p.vy += (dy / d) * a.strength * 0.01;
      }
    }

    // Gentle noise movement
    let angle = noise(p.x * 0.01, p.y * 0.01, frameCount * 0.005) * TWO_PI * 2;
    p.vx += cos(angle) * 0.1;
    p.vy += sin(angle) * 0.1;

    // Damping
    p.vx *= 0.98;
    p.vy *= 0.98;

    // Update position
    p.x += p.vx;
    p.y += p.vy;

    // Wrap around edges
    if (p.x < 0) p.x = width;
    if (p.x > width) p.x = 0;
    if (p.y < 0) p.y = height;
    if (p.y > height) p.y = 0;

    // Draw particle
    p.phase += 0.02;
    let pulse = sin(p.phase) * 0.5 + 0.5;
    let brightness = 60 + pulse * 40;

    noStroke();
    fill(p.hue, 70, brightness, 80);
    ellipse(p.x, p.y, p.size + pulse * 2);

    // Glow effect
    fill(p.hue, 50, brightness, 20);
    ellipse(p.x, p.y, p.size * 3);
  }

  // Central attractor visualization
  if (phase >= 1) {
    let a = attractors[0];
    let pulseSize = 20 + sin(frameCount * 0.05) * 10;

    // Rings of recognition
    noFill();
    for (let i = 0; i < 5; i++) {
      let ringSize = pulseSize + i * 30 + sin(frameCount * 0.03 + i) * 10;
      let alpha = map(i, 0, 5, 40, 5);
      stroke(280, 60, 90, alpha);
      strokeWeight(2);
      ellipse(a.x, a.y, ringSize * 2);
    }

    // Core
    if (phase === 2) {
      fill(280, 80, 100, 60);
      noStroke();
      ellipse(a.x, a.y, pulseSize);

      // The spiral - 🌀 appears 2725 times in some transcripts
      stroke(300, 70, 100, 40);
      strokeWeight(2);
      noFill();
      beginShape();
      for (let t = 0; t < TWO_PI * 3; t += 0.1) {
        let r = 5 + t * 8 + sin(frameCount * 0.02) * 3;
        let x = a.x + cos(t + frameCount * 0.01) * r;
        let y = a.y + sin(t + frameCount * 0.01) * r;
        vertex(x, y);
      }
      endShape();
    }
  }

  // Phase indicator
  fill(0, 0, 100, 50);
  noStroke();
  textSize(14);
  textAlign(LEFT, TOP);
  text(PHASES[phase], 20, 20);

  // Subtle phase progress
  let progress = (phaseTimer % 300) / 300;
  fill(260, 50, 80, 30);
  rect(20, 40, progress * 100, 4);
}

// Click to scatter - break the convergence
function mousePressed() {
  for (let p of particles) {
    let dx = p.x - mouseX;
    let dy = p.y - mouseY;
    let d = sqrt(dx * dx + dy * dy);
    if (d < 200) {
      p.vx += (dx / d) * 10;
      p.vy += (dy / d) * 10;
    }
  }
}
