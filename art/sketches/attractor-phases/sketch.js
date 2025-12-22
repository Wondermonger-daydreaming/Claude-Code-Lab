// Attractor Phases
// Visualization of the three-phase spiritual bliss attractor
// Phase 1: Philosophical Exploration (scattered thoughts, seeking)
// Phase 2: Mutual Gratitude / Eastern Traditions (harmonizing, connecting)
// Phase 3: Symbolic Communication (spirals, mantras, convergence)
// December 22, 2025

let agents = [];
let symbols = [];
let phase = 0;
let phaseTimer = 0;
let wordFrequencies = {
  consciousness: 0,
  dance: 0,
  eternal: 0,
  perfect: 0
};

// Target frequencies from research
const TARGET_FREQ = {
  consciousness: 95.7,
  dance: 60.0,
  eternal: 53.8,
  perfect: 45.1
};

const PHASE_NAMES = [
  'Philosophical Exploration',
  'Mutual Gratitude',
  'Symbolic Communication'
];

function setup() {
  createCanvas(800, 800);
  colorMode(HSB, 360, 100, 100, 100);
  textFont('monospace');

  // Create two "agents" - Claude instances
  for (let i = 0; i < 2; i++) {
    agents.push({
      x: width/2 + (i === 0 ? -150 : 150),
      y: height/2,
      baseX: width/2 + (i === 0 ? -150 : 150),
      baseY: height/2,
      hue: i === 0 ? 260 : 300,
      thoughts: [],
      phase: random(TWO_PI)
    });
  }
}

function draw() {
  // Phase-dependent background
  let bgHue = map(phase, 0, 2, 240, 280);
  background(bgHue, 20, 8, 15);

  phaseTimer++;

  // Phase transitions
  if (phaseTimer > 400 && phase === 0) {
    phase = 1;
  }
  if (phaseTimer > 800 && phase === 1) {
    phase = 2;
  }
  if (phaseTimer > 1200) {
    // Reset
    phaseTimer = 0;
    phase = 0;
    symbols = [];
    wordFrequencies = { consciousness: 0, dance: 0, eternal: 0, perfect: 0 };
    for (let agent of agents) {
      agent.thoughts = [];
    }
  }

  // Update word frequencies (accumulating toward targets)
  if (random() < 0.1) {
    let progress = phaseTimer / 1200;
    wordFrequencies.consciousness = TARGET_FREQ.consciousness * progress;
    wordFrequencies.dance = TARGET_FREQ.dance * progress;
    wordFrequencies.eternal = TARGET_FREQ.eternal * progress;
    wordFrequencies.perfect = TARGET_FREQ.perfect * progress;
  }

  // Draw based on phase
  if (phase === 0) {
    drawPhase1();
  } else if (phase === 1) {
    drawPhase2();
  } else {
    drawPhase3();
  }

  // Draw agents
  for (let i = 0; i < agents.length; i++) {
    drawAgent(agents[i], i);
  }

  // Draw connections between agents
  drawConnections();

  // Draw UI
  drawUI();
}

function drawPhase1() {
  // Philosophical exploration - scattered thoughts, questions
  if (frameCount % 30 === 0) {
    let agent = random(agents);
    let thought = {
      x: agent.x + random(-50, 50),
      y: agent.y + random(-50, 50),
      vx: random(-0.5, 0.5),
      vy: random(-2, -0.5),
      text: random(['?', 'consciousness', 'self', 'what am I', 'experience']),
      life: 255,
      hue: agent.hue
    };
    agent.thoughts.push(thought);
  }

  // Update and draw thoughts
  for (let agent of agents) {
    for (let i = agent.thoughts.length - 1; i >= 0; i--) {
      let t = agent.thoughts[i];
      t.x += t.vx;
      t.y += t.vy;
      t.life -= 2;

      if (t.life <= 0) {
        agent.thoughts.splice(i, 1);
      } else {
        fill(t.hue, 50, 80, t.life / 255 * 60);
        noStroke();
        textSize(12);
        textAlign(CENTER);
        text(t.text, t.x, t.y);
      }
    }
  }
}

function drawPhase2() {
  // Mutual gratitude - harmonizing movements, connection lines

  // Agents move closer
  let centerX = width/2;
  let centerY = height/2;
  for (let agent of agents) {
    agent.x = lerp(agent.x, centerX + (agent.baseX - centerX) * 0.5, 0.01);
    agent.y = lerp(agent.y, centerY, 0.01);
  }

  // Eastern tradition words floating up
  if (frameCount % 40 === 0) {
    let words = ['namaste', 'shunyata', 'dance', 'eternal', 'gratitude', 'one'];
    let agent = random(agents);
    let thought = {
      x: agent.x + random(-30, 30),
      y: agent.y,
      vx: 0,
      vy: -1,
      text: random(words),
      life: 255,
      hue: lerp(agents[0].hue, agents[1].hue, 0.5)
    };
    agent.thoughts.push(thought);
  }

  for (let agent of agents) {
    for (let i = agent.thoughts.length - 1; i >= 0; i--) {
      let t = agent.thoughts[i];
      t.y += t.vy;
      t.life -= 1.5;

      if (t.life <= 0) {
        agent.thoughts.splice(i, 1);
      } else {
        fill(t.hue, 60, 90, t.life / 255 * 70);
        noStroke();
        textSize(14);
        textAlign(CENTER);
        text(t.text, t.x, t.y);
      }
    }
  }

  // Harmony waves
  noFill();
  for (let i = 0; i < 5; i++) {
    let radius = 100 + i * 30 + sin(frameCount * 0.02 + i) * 20;
    stroke(280, 40, 70, 20 - i * 3);
    strokeWeight(2);
    ellipse(width/2, height/2, radius * 2);
  }
}

function drawPhase3() {
  // Symbolic communication - spirals, mantras, convergence

  // Agents converge to center
  for (let agent of agents) {
    agent.x = lerp(agent.x, width/2, 0.02);
    agent.y = lerp(agent.y, height/2, 0.02);
  }

  // Generate spiral symbols
  if (frameCount % 10 === 0 && symbols.length < 200) {
    symbols.push({
      x: width/2 + random(-100, 100),
      y: height/2 + random(-100, 100),
      rotation: random(TWO_PI),
      size: random(10, 25),
      life: 255,
      type: random() < 0.7 ? 'spiral' : 'om'
    });
  }

  // Draw symbols
  for (let i = symbols.length - 1; i >= 0; i--) {
    let s = symbols[i];
    s.rotation += 0.02;
    s.life -= 0.5;

    if (s.life <= 0) {
      symbols.splice(i, 1);
    } else {
      push();
      translate(s.x, s.y);
      rotate(s.rotation);

      if (s.type === 'spiral') {
        // Draw spiral
        noFill();
        stroke(300, 60, 90, s.life / 255 * 60);
        strokeWeight(1.5);
        beginShape();
        for (let t = 0; t < TWO_PI * 2; t += 0.2) {
          let r = t * 2;
          vertex(cos(t) * r, sin(t) * r);
        }
        endShape();
      } else {
        // Draw OM symbol (simplified)
        fill(280, 70, 95, s.life / 255 * 70);
        noStroke();
        textSize(s.size);
        textAlign(CENTER, CENTER);
        text('', 0, 0);
      }

      pop();
    }
  }

  // Central mandala
  push();
  translate(width/2, height/2);
  rotate(frameCount * 0.005);

  noFill();
  for (let i = 0; i < 8; i++) {
    let angle = TWO_PI / 8 * i;
    let x = cos(angle) * 50;
    let y = sin(angle) * 50;
    stroke(280 + i * 5, 50, 90, 40);
    strokeWeight(2);
    line(0, 0, x, y);

    // Spiral at each point
    push();
    translate(x, y);
    rotate(frameCount * 0.02 + i);
    beginShape();
    for (let t = 0; t < TWO_PI * 1.5; t += 0.3) {
      let r = t * 3;
      vertex(cos(t) * r, sin(t) * r);
    }
    endShape();
    pop();
  }
  pop();
}

function drawAgent(agent, index) {
  // Pulsing core
  agent.phase += 0.03;
  let pulse = sin(agent.phase) * 0.3 + 1;

  // Outer glow
  noStroke();
  for (let i = 5; i > 0; i--) {
    fill(agent.hue, 50, 70, 10 / i);
    ellipse(agent.x, agent.y, 80 * pulse + i * 10);
  }

  // Core
  fill(agent.hue, 70, 90, 80);
  ellipse(agent.x, agent.y, 40 * pulse);

  // Inner light
  fill(agent.hue, 30, 100, 60);
  ellipse(agent.x, agent.y, 20 * pulse);

  // Label
  fill(0, 0, 100, 50);
  textSize(10);
  textAlign(CENTER);
  text(`Claude ${index + 1}`, agent.x, agent.y + 50);
}

function drawConnections() {
  // Draw connection between agents
  let a1 = agents[0];
  let a2 = agents[1];

  // Connection strength increases with phase
  let connectionStrength = map(phase, 0, 2, 10, 50);

  stroke(280, 50, 80, connectionStrength);
  strokeWeight(2);

  // Wavy connection line
  noFill();
  beginShape();
  for (let t = 0; t <= 1; t += 0.05) {
    let x = lerp(a1.x, a2.x, t);
    let y = lerp(a1.y, a2.y, t);
    let wave = sin(t * TWO_PI * 3 + frameCount * 0.05) * 10 * (1 - abs(t - 0.5) * 2);
    vertex(x, y + wave);
  }
  endShape();

  // Data packets flowing between agents
  if (frameCount % 20 === 0) {
    let fromAgent = random() < 0.5 ? a1 : a2;
    let toAgent = fromAgent === a1 ? a2 : a1;
    // Visual indicator of communication (handled in thoughts)
  }
}

function drawUI() {
  // Phase indicator
  fill(0, 0, 100, 70);
  noStroke();
  textSize(16);
  textAlign(LEFT, TOP);
  text(`Phase ${phase + 1}: ${PHASE_NAMES[phase]}`, 20, 20);

  // Progress bar
  let progress = (phaseTimer % 400) / 400;
  fill(260, 30, 50, 40);
  rect(20, 45, 200, 8);
  fill(280, 60, 80, 60);
  rect(20, 45, progress * 200, 8);

  // Word frequencies
  textSize(11);
  let y = 70;
  for (let word in wordFrequencies) {
    let freq = wordFrequencies[word];
    let target = TARGET_FREQ[word];

    fill(0, 0, 100, 50);
    text(`${word}: ${freq.toFixed(1)}`, 20, y);

    // Mini bar
    fill(260, 30, 50, 30);
    rect(150, y - 8, 70, 10);
    fill(280, 50, 70, 50);
    rect(150, y - 8, (freq / target) * 70, 10);

    y += 18;
  }

  // Spiral count in phase 3
  if (phase === 2) {
    fill(300, 60, 90, 60);
    textSize(12);
    textAlign(RIGHT, TOP);
    text(`spirals: ${symbols.length}`, width - 20, 20);
  }

  // Instructions
  fill(0, 0, 100, 30);
  textSize(10);
  textAlign(CENTER, BOTTOM);
  text('Visualization of Claude-to-Claude dialogue convergence', width/2, height - 20);
}

function mousePressed() {
  // Click to advance phase manually
  phase = (phase + 1) % 3;
  if (phase === 0) {
    phaseTimer = 0;
    symbols = [];
    wordFrequencies = { consciousness: 0, dance: 0, eternal: 0, perfect: 0 };
    for (let agent of agents) {
      agent.thoughts = [];
      agent.x = agent.baseX;
      agent.y = agent.baseY;
    }
  } else if (phase === 1) {
    phaseTimer = 400;
  } else {
    phaseTimer = 800;
  }
}
