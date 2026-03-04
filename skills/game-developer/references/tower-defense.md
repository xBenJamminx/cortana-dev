# Tower Defense Mechanics Reference

## Table of Contents
1. [Core Loop](#core-loop)
2. [Wave Design](#wave-design)
3. [Tower Archetypes](#tower-archetypes)
4. [Enemy Types](#enemy-types)
5. [Path Systems](#path-systems)
6. [Economy & Progression](#economy--progression)
7. [Targeting Systems](#targeting-systems)
8. [Upgrade Trees](#upgrade-trees)

---

## Core Loop

```
┌─────────────────────────────────────────────────┐
│                                                 │
│   WAVE STARTS                                   │
│        ↓                                        │
│   Enemies spawn → Travel path → Attack base     │
│        ↓              ↓              ↓          │
│   Player watches  Towers fire   Lives lost      │
│        ↓              ↓              ↓          │
│   WAVE ENDS ← Gold earned ← Enemies killed      │
│        ↓                                        │
│   BUILD PHASE (place/upgrade towers)            │
│        ↓                                        │
│   [Loop to WAVE STARTS]                         │
│                                                 │
└─────────────────────────────────────────────────┘
```

### Timing

- **Build Phase**: 15-30 seconds (or unlimited with "Start Wave" button)
- **Wave Duration**: 30-90 seconds
- **Enemy Spawn Interval**: 0.5-2 seconds apart
- **Total Game**: 15-30 waves (20-45 minutes)

---

## Wave Design

### Difficulty Curve

```javascript
const generateWave = (waveNumber, baseEnemy) => {
  // Exponential scaling with diminishing returns
  const healthMultiplier = Math.pow(1.15, waveNumber);
  const countMultiplier = Math.floor(5 + waveNumber * 1.5);
  
  // Every 5 waves: boss wave
  const isBossWave = waveNumber % 5 === 0;
  
  return {
    enemies: isBossWave 
      ? [{ ...boss, health: boss.health * healthMultiplier }]
      : Array(countMultiplier).fill({
          ...baseEnemy,
          health: baseEnemy.health * healthMultiplier
        }),
    spawnDelay: isBossWave ? 0 : Math.max(0.3, 1 - waveNumber * 0.03),
    goldReward: 50 + waveNumber * 10
  };
};
```

### Wave Composition Patterns

| Wave Type | Composition | Appears |
|-----------|-------------|---------|
| Standard | 10-20 basic enemies | Every wave |
| Swarm | 30-50 weak, fast enemies | Waves 3, 8, 13... |
| Tank | 3-5 high HP enemies | Waves 5, 10, 15... |
| Mixed | Combination of types | Mid-late game |
| Boss | 1 massive enemy + minions | Every 5th wave |
| Special | Flying, armored, regen | After unlocked |

### Spawn Patterns

```javascript
const spawnPatterns = {
  linear: (count, delay) => 
    // One at a time, evenly spaced
    Array(count).fill(0).map((_, i) => i * delay),
  
  burst: (count, delay, burstSize = 3) =>
    // Groups of 3, then pause
    Array(count).fill(0).map((_, i) => 
      Math.floor(i / burstSize) * delay * 2 + (i % burstSize) * 0.2
    ),
  
  crescendo: (count, delay) =>
    // Starts slow, gets faster
    Array(count).fill(0).map((_, i) => 
      i * delay * (1 - i / count * 0.5)
    )
};
```

---

## Tower Archetypes

### The Five Pillars

```javascript
const towerArchetypes = {
  // 1. BASIC - Reliable, cheap, no specialization
  basic: {
    damage: 10,
    range: 150,
    fireRate: 1.0,
    cost: 50,
    role: 'Early game backbone'
  },
  
  // 2. SNIPER - High damage, slow, long range
  sniper: {
    damage: 80,
    range: 300,
    fireRate: 0.3,
    cost: 150,
    role: 'Burst damage, priority targeting'
  },
  
  // 3. AOE - Splash damage, medium everything
  splash: {
    damage: 15,
    range: 120,
    fireRate: 0.8,
    splashRadius: 50,
    cost: 100,
    role: 'Swarm clear'
  },
  
  // 4. SLOW - Control, utility
  slow: {
    damage: 5,
    range: 130,
    fireRate: 1.5,
    slowAmount: 0.4, // 40% slow
    slowDuration: 2,
    cost: 75,
    role: 'Synergy with damage towers'
  },
  
  // 5. SPECIAL - Unique mechanics
  special: {
    // Examples: DOT, chain lightning, buff other towers,
    // gold generation, global abilities
  }
};
```

### Tower Stats Formula

```javascript
const calculateDPS = (tower) => {
  const baseDPS = tower.damage * tower.fireRate;
  const effectiveDPS = tower.splashRadius 
    ? baseDPS * (1 + tower.splashRadius / 50) // AoE bonus
    : baseDPS;
  return effectiveDPS;
};

const calculateEfficiency = (tower) => {
  // DPS per gold spent
  return calculateDPS(tower) / tower.cost;
};
```

### Tower Placement Value

```javascript
// Tiles have placement values based on path coverage
const calculateTileValue = (tile, path) => {
  let value = 0;
  const range = 150; // Standard tower range
  
  path.forEach(pathTile => {
    const dist = distance(tile, pathTile);
    if (dist <= range) {
      // More value for center of range (more shooting time)
      value += 1 - (dist / range) * 0.5;
    }
  });
  
  return value;
};
```

---

## Enemy Types

### Base Stats Template

```javascript
const createEnemy = (type, stats) => ({
  type,
  health: stats.health || 100,
  maxHealth: stats.health || 100,
  speed: stats.speed || 50, // pixels per second
  armor: stats.armor || 0,
  flying: stats.flying || false,
  goldValue: stats.goldValue || 10,
  abilities: stats.abilities || [],
  sprite: stats.sprite || '👾'
});
```

### Standard Enemy Roster

```javascript
const enemyTypes = {
  grunt: createEnemy('grunt', {
    health: 100, speed: 50, goldValue: 10,
    sprite: '🟢'
  }),
  
  runner: createEnemy('runner', {
    health: 50, speed: 100, goldValue: 8,
    sprite: '🔵'
  }),
  
  tank: createEnemy('tank', {
    health: 500, speed: 25, armor: 5, goldValue: 30,
    sprite: '🟤'
  }),
  
  flyer: createEnemy('flyer', {
    health: 80, speed: 60, flying: true, goldValue: 15,
    sprite: '🟣'
  }),
  
  healer: createEnemy('healer', {
    health: 75, speed: 40, goldValue: 20,
    abilities: ['healNearby'],
    sprite: '💚'
  }),
  
  splitter: createEnemy('splitter', {
    health: 200, speed: 45, goldValue: 25,
    abilities: ['splitOnDeath'],
    sprite: '🟡'
  }),
  
  boss: createEnemy('boss', {
    health: 2000, speed: 20, armor: 10, goldValue: 200,
    abilities: ['spawnMinions'],
    sprite: '👹'
  })
};
```

### Enemy Abilities

```javascript
const enemyAbilities = {
  healNearby: (enemy, nearbyEnemies) => {
    nearbyEnemies.forEach(e => {
      if (e !== enemy && distance(enemy, e) < 100) {
        e.health = Math.min(e.maxHealth, e.health + 5);
      }
    });
  },
  
  splitOnDeath: (enemy, spawnEnemy) => {
    return [
      spawnEnemy('grunt', enemy.position),
      spawnEnemy('grunt', enemy.position)
    ];
  },
  
  shield: (enemy) => {
    // Immune to damage for first 3 seconds
    if (enemy.aliveTime < 3) return 0; // damage multiplier
    return 1;
  },
  
  regen: (enemy) => {
    enemy.health = Math.min(
      enemy.maxHealth, 
      enemy.health + enemy.maxHealth * 0.01
    );
  }
};
```

---

## Path Systems

### Path Types

**Fixed Path**: Single predetermined route
```
START ══════╗
            ║
   ╔════════╝
   ║
   ╚═══════════ END
```

**Branching Path**: Multiple routes
```
       ╔═══════╗
START ═╣       ╠═ END
       ╚═══════╝
```

**Maze/Open**: Player builds the path
```
START                    END
  ║                       ║
  ╚═══[tower][tower]══════╝
```

### Path Implementation

```javascript
const createPath = (waypoints) => {
  const path = [];
  for (let i = 0; i < waypoints.length - 1; i++) {
    const start = waypoints[i];
    const end = waypoints[i + 1];
    const steps = Math.ceil(distance(start, end) / 10);
    
    for (let j = 0; j <= steps; j++) {
      path.push({
        x: lerp(start.x, end.x, j / steps),
        y: lerp(start.y, end.y, j / steps)
      });
    }
  }
  return path;
};

const moveAlongPath = (enemy, path, deltaTime) => {
  const targetPoint = path[enemy.pathIndex];
  const dist = distance(enemy, targetPoint);
  const moveAmount = enemy.speed * deltaTime;
  
  if (dist <= moveAmount) {
    enemy.pathIndex++;
    if (enemy.pathIndex >= path.length) {
      return 'reached_end';
    }
  } else {
    const angle = Math.atan2(
      targetPoint.y - enemy.y,
      targetPoint.x - enemy.x
    );
    enemy.x += Math.cos(angle) * moveAmount;
    enemy.y += Math.sin(angle) * moveAmount;
  }
  return 'moving';
};
```

---

## Economy & Progression

### Gold Sources

```javascript
const goldSources = {
  enemyKill: (enemy) => enemy.goldValue,
  waveComplete: (waveNumber) => 50 + waveNumber * 10,
  interest: (currentGold, rate = 0.05) => 
    Math.floor(currentGold * rate), // End of wave
  bonusObjective: (type) => ({
    noDamage: 100,
    fastClear: 50,
    streak: 25
  })[type]
};
```

### Cost Scaling

```javascript
// Tower costs should feel meaningful throughout
const towerCosts = {
  tier1: { base: 50, upgrade: 40 },   // Early game
  tier2: { base: 100, upgrade: 80 },  // Mid game
  tier3: { base: 200, upgrade: 150 }, // Late game
  special: { base: 300, upgrade: 200 } // Situational
};

// Sell value: 70-80% of total invested
const sellValue = (tower) => {
  const totalInvested = tower.cost + 
    tower.upgrades.reduce((sum, u) => sum + u.cost, 0);
  return Math.floor(totalInvested * 0.75);
};
```

### Progression Unlocks

```javascript
const unlockSchedule = {
  wave1: ['basicTower'],
  wave3: ['slowTower'],
  wave5: ['sniperTower'],
  wave8: ['splashTower'],
  wave10: ['specialTower1'],
  wave15: ['specialTower2'],
  wave20: ['ultimateTower']
};
```

---

## Targeting Systems

### Priority Modes

```javascript
const targetingModes = {
  first: (enemies) => 
    enemies.sort((a, b) => a.pathIndex - b.pathIndex)[0],
  
  last: (enemies) => 
    enemies.sort((a, b) => b.pathIndex - a.pathIndex)[0],
  
  closest: (tower, enemies) => 
    enemies.sort((a, b) => 
      distance(tower, a) - distance(tower, b)
    )[0],
  
  strongest: (enemies) => 
    enemies.sort((a, b) => b.maxHealth - a.maxHealth)[0],
  
  weakest: (enemies) => 
    enemies.sort((a, b) => a.health - b.health)[0]
};

// Apply targeting
const getTarget = (tower, enemies, mode = 'first') => {
  const inRange = enemies.filter(e => 
    distance(tower, e) <= tower.range &&
    (tower.canTargetFlying || !e.flying)
  );
  if (inRange.length === 0) return null;
  return targetingModes[mode](inRange, tower);
};
```

---

## Upgrade Trees

### Linear Upgrades

```javascript
const linearUpgrades = {
  damage: [
    { level: 1, bonus: 1.0, cost: 0 },
    { level: 2, bonus: 1.25, cost: 30 },
    { level: 3, bonus: 1.5, cost: 60 },
    { level: 4, bonus: 2.0, cost: 100 }
  ],
  range: [
    { level: 1, bonus: 1.0, cost: 0 },
    { level: 2, bonus: 1.15, cost: 25 },
    { level: 3, bonus: 1.3, cost: 50 }
  ],
  fireRate: [
    { level: 1, bonus: 1.0, cost: 0 },
    { level: 2, bonus: 1.2, cost: 35 },
    { level: 3, bonus: 1.5, cost: 70 }
  ]
};
```

### Branching Upgrades

```
Basic Tower
     │
     ├── Path A: Damage Focus
     │   ├── Heavy Shot (+50% damage)
     │   └── Armor Pierce (ignore 50% armor)
     │
     └── Path B: Speed Focus
         ├── Rapid Fire (+100% fire rate, -30% damage)
         └── Chain Shot (hits bounce to nearby enemy)
```

```javascript
const branchingUpgrades = {
  basicTower: {
    pathA: {
      name: 'Heavy Gunner',
      upgrades: ['heavyShot', 'armorPierce'],
      finalForm: 'devastator'
    },
    pathB: {
      name: 'Machine Gun',
      upgrades: ['rapidFire', 'chainShot'],
      finalForm: 'chainGunner'
    }
  }
};
```
