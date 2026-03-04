# RTS Mechanics Reference

## Table of Contents
1. [Economy Systems](#economy-systems)
2. [Unit Design](#unit-design)
3. [Combat Resolution](#combat-resolution)
4. [Fog of War](#fog-of-war)
5. [Pathfinding](#pathfinding)
6. [Base Building](#base-building)
7. [AI Opponent Patterns](#ai-opponent-patterns)

---

## Economy Systems

### Resource Types

**Primary Resources** (gathered continuously):
- Minerals/Gold — Universal currency, abundant
- Gas/Wood — Secondary, gates advanced units
- Supply/Population — Soft cap on army size

**Secondary Resources** (strategic):
- Map control points
- Tech level
- Vision/information

### Gathering Formula

```javascript
const calculateIncome = (workers, sources, efficiency = 1.0) => {
  const baseRate = 5; // per worker per second
  const diminishingReturns = Math.min(workers, sources * 3);
  const saturation = workers > sources * 2 ? 0.6 : 1.0;
  return diminishingReturns * baseRate * efficiency * saturation;
};
```

### Economic Pacing

| Phase | Time | Worker Count | Income/min |
|-------|------|--------------|------------|
| Opening | 0-3 min | 6-12 | 200-400 |
| Early | 3-8 min | 12-24 | 400-800 |
| Mid | 8-15 min | 24-40 | 800-1200 |
| Late | 15+ min | 40+ | 1200+ |

---

## Unit Design

### The Unit Triangle

```
       DAMAGE
         /\
        /  \
       / ⚔️ \
      /______\
   HEALTH    SPEED
```

Every unit emphasizes 1-2 attributes:
- **Glass Cannon**: High damage, low health, medium speed
- **Tank**: High health, low damage, low speed
- **Raider**: Medium damage, low health, high speed
- **Bruiser**: Balanced all three

### Unit Roles

```javascript
const unitArchetypes = {
  worker: { gathers: true, combatValue: 0.1 },
  scout: { vision: 'high', speed: 'fast', combat: 'weak' },
  infantry: { role: 'frontline', counter: 'cavalry' },
  cavalry: { role: 'flank', counter: 'ranged' },
  ranged: { role: 'backline', counter: 'infantry' },
  siege: { role: 'structures', counter: 'cavalry' },
  spellcaster: { role: 'support', aoe: true }
};
```

### Counter System (Rock-Paper-Scissors+)

```
Infantry → Ranged → Cavalry → Infantry
              ↓
           Siege → Buildings
              ↑
         Anti-Siege
```

Bonus damage multipliers: 1.5x (soft counter) to 2.5x (hard counter)

### Unit Stats Template

```javascript
const createUnit = (name, stats) => ({
  name,
  health: stats.health || 100,
  maxHealth: stats.health || 100,
  damage: stats.damage || 10,
  attackSpeed: stats.attackSpeed || 1.0, // attacks per second
  range: stats.range || 1, // 1 = melee
  armor: stats.armor || 0,
  speed: stats.speed || 100, // pixels per second
  cost: stats.cost || { gold: 50 },
  buildTime: stats.buildTime || 15, // seconds
  supply: stats.supply || 1,
  abilities: stats.abilities || [],
  counters: stats.counters || [],
  counteredBy: stats.counteredBy || []
});
```

---

## Combat Resolution

### Damage Calculation

```javascript
const calculateDamage = (attacker, defender) => {
  let baseDamage = attacker.damage;
  
  // Armor reduction (diminishing returns)
  const armorReduction = defender.armor / (defender.armor + 100);
  baseDamage *= (1 - armorReduction);
  
  // Counter bonus
  if (attacker.counters.includes(defender.type)) {
    baseDamage *= 1.5;
  }
  
  // Random variance (±10%)
  baseDamage *= 0.9 + Math.random() * 0.2;
  
  return Math.max(1, Math.floor(baseDamage));
};
```

### Combat Priority (Target Selection)

1. Units attacking me
2. Closest enemy unit
3. Lowest health enemy
4. Highest threat enemy

```javascript
const selectTarget = (unit, enemies) => {
  // Priority 1: Retaliation
  const attacker = enemies.find(e => e.target?.id === unit.id);
  if (attacker) return attacker;
  
  // Priority 2: In range, lowest health
  const inRange = enemies
    .filter(e => distance(unit, e) <= unit.range)
    .sort((a, b) => a.health - b.health);
  if (inRange.length) return inRange[0];
  
  // Priority 3: Closest
  return enemies.sort((a, b) => 
    distance(unit, a) - distance(unit, b)
  )[0];
};
```

---

## Fog of War

### Vision Types

```javascript
const visionStates = {
  unexplored: 0,  // Black, never seen
  fogged: 1,      // Grey, seen before but not now
  visible: 2      // Clear, currently in sight
};
```

### Vision Calculation

```javascript
const updateVision = (map, units, visionRange) => {
  // Reset to fogged (preserve explored areas)
  map.forEach(tile => {
    if (tile.vision === 2) tile.vision = 1;
  });
  
  // Apply unit vision
  units.forEach(unit => {
    const tilesInRange = getTilesInRadius(unit.x, unit.y, visionRange);
    tilesInRange.forEach(tile => {
      tile.vision = 2;
    });
  });
};
```

### High Ground Advantage

Units on high ground:
- +2 vision range
- +25% attack range
- Cannot be seen from low ground unless within 2 tiles

---

## Pathfinding

### A* Implementation

```javascript
const findPath = (start, goal, grid) => {
  const openSet = [start];
  const cameFrom = new Map();
  const gScore = new Map([[start.id, 0]]);
  const fScore = new Map([[start.id, heuristic(start, goal)]]);
  
  while (openSet.length > 0) {
    const current = openSet.reduce((a, b) => 
      fScore.get(a.id) < fScore.get(b.id) ? a : b
    );
    
    if (current.id === goal.id) {
      return reconstructPath(cameFrom, current);
    }
    
    openSet.splice(openSet.indexOf(current), 1);
    
    for (const neighbor of getNeighbors(current, grid)) {
      const tentativeG = gScore.get(current.id) + 
        movementCost(current, neighbor);
      
      if (tentativeG < (gScore.get(neighbor.id) ?? Infinity)) {
        cameFrom.set(neighbor.id, current);
        gScore.set(neighbor.id, tentativeG);
        fScore.set(neighbor.id, tentativeG + heuristic(neighbor, goal));
        if (!openSet.includes(neighbor)) openSet.push(neighbor);
      }
    }
  }
  return null; // No path
};
```

### Flow Fields (for large unit groups)

Better than individual A* for 10+ units moving to same destination.

```javascript
const generateFlowField = (goal, grid) => {
  const field = new Map();
  const queue = [goal];
  field.set(goal.id, { cost: 0, direction: null });
  
  while (queue.length > 0) {
    const current = queue.shift();
    const currentCost = field.get(current.id).cost;
    
    for (const neighbor of getNeighbors(current, grid)) {
      if (!field.has(neighbor.id)) {
        const cost = currentCost + movementCost(neighbor, current);
        const direction = normalize(subtract(current, neighbor));
        field.set(neighbor.id, { cost, direction });
        queue.push(neighbor);
      }
    }
  }
  return field;
};
```

---

## Base Building

### Build Order Constraints

```javascript
const techTree = {
  barracks: { requires: ['headquarters'], unlocks: ['infantry'] },
  factory: { requires: ['barracks'], unlocks: ['vehicles'] },
  airfield: { requires: ['factory'], unlocks: ['aircraft'] },
  techLab: { requires: ['factory'], unlocks: ['upgrades'] }
};

const canBuild = (building, playerState) => {
  const requirements = techTree[building]?.requires || [];
  return requirements.every(req => 
    playerState.buildings.includes(req)
  );
};
```

### Base Layout Principles

- Production buildings near resources
- Defensive structures at choke points
- Tech buildings protected in rear
- Supply buildings spread out (anti-AoE)

---

## AI Opponent Patterns

### Difficulty Scaling

```javascript
const aiSettings = {
  easy: {
    reactionTime: 2000, // ms before responding
    microLevel: 0.3,    // % of optimal micro
    macroCycle: 30,     // seconds between build decisions
    scoutFrequency: 0.2
  },
  medium: {
    reactionTime: 500,
    microLevel: 0.6,
    macroCycle: 15,
    scoutFrequency: 0.5
  },
  hard: {
    reactionTime: 100,
    microLevel: 0.9,
    macroCycle: 5,
    scoutFrequency: 0.8
  }
};
```

### AI State Machine

```javascript
const aiStates = {
  opening: {
    focus: 'economy',
    armyRatio: 0.2,
    transitions: { 
      'workerCount >= 16': 'expand',
      'enemyScouted': 'defend'
    }
  },
  expand: {
    focus: 'expansion',
    armyRatio: 0.4,
    transitions: {
      'bases >= 2': 'midgame',
      'underAttack': 'defend'
    }
  },
  midgame: {
    focus: 'army',
    armyRatio: 0.6,
    transitions: {
      'armySupply >= 100': 'aggression',
      'losing': 'defend'
    }
  },
  aggression: {
    focus: 'attack',
    armyRatio: 0.8,
    transitions: {
      'armyDestroyed': 'rebuild',
      'enemyDestroyed': 'victory'
    }
  }
};
```

### Build Order Templates

```javascript
const standardOpening = [
  { supply: 6, action: 'worker' },
  { supply: 7, action: 'worker' },
  { supply: 8, action: 'worker' },
  { supply: 9, action: 'supplyBuilding' },
  { supply: 10, action: 'worker' },
  { supply: 11, action: 'barracks' },
  { supply: 12, action: 'worker' },
  { supply: 13, action: 'worker' },
  { supply: 14, action: 'scout' },
  { supply: 15, action: 'marine' }
];
```
