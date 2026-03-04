---
name: cs-generative-art
description: Generative and algorithmic art toolkit using p5.js. This skill should be used when creating procedural artwork, visualizations with seeded randomness, flow fields, particle systems, or interactive canvas experiences. Produces self-contained HTML files with parameter controls for exploring variations.
---

# Generative Art with p5.js

Create algorithmic artwork with seeded randomness and interactive parameter exploration.

## Core Principles

1. **Seeded randomness** - Same seed produces identical output
2. **Parameter-driven** - Tune behavior through adjustable values
3. **Self-contained** - Single HTML file with everything embedded

## Basic Structure

```html
<!DOCTYPE html>
<html>
<head>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/p5.js/1.9.0/p5.min.js"></script>
  <style>
    body { margin: 0; display: flex; justify-content: center; align-items: center; min-height: 100vh; background: #1a1a1a; }
    #controls { position: fixed; top: 20px; left: 20px; background: rgba(255,255,255,0.9); padding: 20px; border-radius: 8px; }
  </style>
</head>
<body>
  <div id="controls">
    <label>Seed: <input type="number" id="seed" value="12345" onchange="regenerate()"></label><br>
    <button onclick="randomSeed()">Random</button>
    <button onclick="saveCanvas('artwork', 'png')">Save</button>
  </div>
  <script>
    let params = {
      seed: 12345,
      // Add parameters here
    };

    function setup() {
      createCanvas(800, 800);
      regenerate();
    }

    function regenerate() {
      params.seed = parseInt(document.getElementById('seed').value);
      randomSeed(params.seed);
      noiseSeed(params.seed);
      redraw();
    }

    function randomSeed() {
      document.getElementById('seed').value = floor(random(99999));
      regenerate();
    }

    function draw() {
      background(20);
      // Your generative algorithm here
      noLoop();
    }
  </script>
</body>
</html>
```

## Algorithmic Patterns

### Flow Fields

```javascript
let params = {
  seed: 12345,
  particles: 1000,
  noiseScale: 0.005,
  speed: 2
};

let particles = [];

function setup() {
  createCanvas(800, 800);
  regenerate();
}

function regenerate() {
  randomSeed(params.seed);
  noiseSeed(params.seed);
  particles = [];
  for (let i = 0; i < params.particles; i++) {
    particles.push({
      x: random(width),
      y: random(height),
      px: 0,
      py: 0
    });
  }
  background(20);
}

function draw() {
  for (let p of particles) {
    p.px = p.x;
    p.py = p.y;

    let angle = noise(p.x * params.noiseScale, p.y * params.noiseScale) * TWO_PI * 2;
    p.x += cos(angle) * params.speed;
    p.y += sin(angle) * params.speed;

    // Wrap around
    if (p.x < 0) p.x = width;
    if (p.x > width) p.x = 0;
    if (p.y < 0) p.y = height;
    if (p.y > height) p.y = 0;

    stroke(255, 10);
    line(p.px, p.py, p.x, p.y);
  }
}
```

### Circle Packing

```javascript
let params = {
  seed: 12345,
  maxCircles: 500,
  minRadius: 5,
  maxRadius: 50
};

let circles = [];

function setup() {
  createCanvas(800, 800);
  noLoop();
}

function draw() {
  randomSeed(params.seed);
  background(240);
  circles = [];

  let attempts = 0;
  while (circles.length < params.maxCircles && attempts < 10000) {
    let c = {
      x: random(width),
      y: random(height),
      r: random(params.minRadius, params.maxRadius)
    };

    let valid = true;
    for (let other of circles) {
      let d = dist(c.x, c.y, other.x, other.y);
      if (d < c.r + other.r + 2) {
        valid = false;
        break;
      }
    }

    if (valid) {
      circles.push(c);
      fill(random(255), random(255), random(255), 150);
      noStroke();
      ellipse(c.x, c.y, c.r * 2);
    }
    attempts++;
  }
}
```

### Recursive Subdivision

```javascript
let params = {
  seed: 42,
  depth: 5,
  splitChance: 0.8
};

function setup() {
  createCanvas(800, 800);
  noLoop();
}

function draw() {
  randomSeed(params.seed);
  background(250);
  stroke(30);
  strokeWeight(1);
  noFill();

  subdivide(50, 50, width - 100, height - 100, 0);
}

function subdivide(x, y, w, h, depth) {
  if (depth >= params.depth || random() > params.splitChance) {
    rect(x, y, w, h);
    return;
  }

  if (random() > 0.5) {
    // Horizontal split
    let split = random(0.3, 0.7) * h;
    subdivide(x, y, w, split, depth + 1);
    subdivide(x, y + split, w, h - split, depth + 1);
  } else {
    // Vertical split
    let split = random(0.3, 0.7) * w;
    subdivide(x, y, split, h, depth + 1);
    subdivide(x + split, y, w - split, h, depth + 1);
  }
}
```

## Color Techniques

### Palette from seed

```javascript
function generatePalette(seed, count) {
  randomSeed(seed);
  let palette = [];
  let hue = random(360);

  for (let i = 0; i < count; i++) {
    palette.push(color(
      (hue + i * (360 / count)) % 360,
      random(60, 90),
      random(70, 95)
    ));
  }
  return palette;
}

// Usage
colorMode(HSB, 360, 100, 100);
let colors = generatePalette(params.seed, 5);
```

### Gradient mapping

```javascript
function valueToColor(value, palette) {
  // value: 0-1, palette: array of colors
  let idx = value * (palette.length - 1);
  let low = floor(idx);
  let high = ceil(idx);
  let t = idx - low;
  return lerpColor(palette[low], palette[min(high, palette.length - 1)], t);
}
```

## Animation Loop

```javascript
let params = {
  seed: 12345,
  speed: 0.01
};

let t = 0;

function draw() {
  background(20);

  // Use time-based noise for animation
  for (let x = 0; x < width; x += 20) {
    for (let y = 0; y < height; y += 20) {
      let n = noise(x * 0.01, y * 0.01, t);
      fill(n * 255);
      rect(x, y, 18, 18);
    }
  }

  t += params.speed;
}
```

## Interactive Controls Template

```html
<div id="controls">
  <h3>Parameters</h3>

  <label>Seed:
    <input type="number" id="seed" value="12345">
  </label>
  <button onclick="randomizeSeed()">Random</button>

  <label>Particles:
    <input type="range" id="particles" min="100" max="5000" value="1000">
    <span id="particles-val">1000</span>
  </label>

  <label>Scale:
    <input type="range" id="scale" min="1" max="100" value="50" step="1">
    <span id="scale-val">0.005</span>
  </label>

  <button onclick="regenerate()">Regenerate</button>
  <button onclick="saveCanvas('art', 'png')">Save PNG</button>
</div>

<script>
  // Sync UI to params
  document.querySelectorAll('input[type="range"]').forEach(input => {
    input.addEventListener('input', function() {
      document.getElementById(this.id + '-val').textContent = this.value;
      updateParams();
    });
  });

  function updateParams() {
    params.seed = parseInt(document.getElementById('seed').value);
    params.particles = parseInt(document.getElementById('particles').value);
    params.noiseScale = parseInt(document.getElementById('scale').value) / 10000;
    regenerate();
  }
</script>
```

## Best Practices

1. **Always use seeded random** - `randomSeed(seed)` and `noiseSeed(seed)`
2. **Separate parameters** - Make tunable values explicit
3. **Include save button** - `saveCanvas()` for exporting
4. **Test multiple seeds** - Ensure variety across seeds
5. **Document the algorithm** - Brief description of approach

## Resources

- p5.js reference: https://p5js.org/reference/
- Noise functions: `noise()`, `noiseSeed()`, `noiseDetail()`
- Random functions: `random()`, `randomSeed()`, `randomGaussian()`
