# RPG & Creature Collection Mechanics Reference

## Table of Contents
1. [Turn-Based Combat](#turn-based-combat)
2. [Creature/Character Stats](#creature-stats)
3. [Type Systems](#type-systems)
4. [Abilities & Moves](#abilities--moves)
5. [Progression & Leveling](#progression--leveling)
6. [Capture/Recruitment](#capture-mechanics)
7. [Evolution & Growth](#evolution--growth)
8. [Party Management](#party-management)
9. [AI Battle Logic](#ai-battle-logic)

---

## Turn-Based Combat

### Battle Flow

```
┌─────────────────────────────────────────────────────┐
│ BATTLE START                                        │
│      ↓                                              │
│ Determine turn order (Speed stat)                   │
│      ↓                                              │
│ ┌──────────────────────────────────────┐            │
│ │ TURN LOOP                            │            │
│ │   1. Active creature selects action  │            │
│ │   2. Execute action                  │            │
│ │   3. Apply effects/damage            │            │
│ │   4. Check for KO                    │            │
│ │   5. Next creature's turn            │            │
│ │   [Loop until one side defeated]     │            │
│ └──────────────────────────────────────┘            │
│      ↓                                              │
│ BATTLE END → XP/Rewards                             │
└─────────────────────────────────────────────────────┘
```

### Turn Order System

```javascript
// Speed-based with priority moves
const calculateTurnOrder = (creatures, selectedActions) => {
  return creatures
    .map(c => ({
      creature: c,
      action: selectedActions[c.id],
      priority: selectedActions[c.id]?.priority || 0,
      speed: c.stats.speed * (c.statusEffects.paralysis ? 0.5 : 1)
    }))
    .sort((a, b) => {
      // Higher priority always goes first
      if (a.priority !== b.priority) return b.priority - a.priority;
      // Same priority: higher speed wins
      if (a.speed !== b.speed) return b.speed - a.speed;
      // Tie: random
      return Math.random() - 0.5;
    });
};
```

### Action Types

```javascript
const actionTypes = {
  attack: { // Use a move/ability
    execute: (user, target, move) => {
      const damage = calculateDamage(user, target, move);
      applyDamage(target, damage);
      applyEffects(target, move.effects);
    }
  },
  item: { // Use consumable
    priority: 6, // Items usually go first
    execute: (user, item) => {
      applyItem(user, item);
      removeFromInventory(item);
    }
  },
  switch: { // Swap active creature
    priority: 6,
    execute: (team, newActiveIndex) => {
      team.active = newActiveIndex;
    }
  },
  flee: { // Attempt to escape
    execute: (playerSpeed, enemySpeed) => {
      const escapeChance = (playerSpeed / enemySpeed) * 0.5 + 0.3;
      return Math.random() < escapeChance;
    }
  }
};
```

---

## Creature Stats

### Core Stats (Pokemon-style)

```javascript
const createCreature = (species, level = 5) => {
  const baseStats = species.baseStats;
  const ivs = generateIVs(); // 0-31 per stat
  const evs = { hp: 0, atk: 0, def: 0, spAtk: 0, spDef: 0, speed: 0 };
  
  return {
    id: generateId(),
    species: species.name,
    nickname: null,
    level,
    currentHp: calculateStat('hp', baseStats.hp, ivs.hp, evs.hp, level),
    stats: {
      hp: calculateStat('hp', baseStats.hp, ivs.hp, evs.hp, level),
      attack: calculateStat('atk', baseStats.atk, ivs.atk, evs.atk, level),
      defense: calculateStat('def', baseStats.def, ivs.def, evs.def, level),
      spAttack: calculateStat('spAtk', baseStats.spAtk, ivs.spAtk, evs.spAtk, level),
      spDefense: calculateStat('spDef', baseStats.spDef, ivs.spDef, evs.spDef, level),
      speed: calculateStat('speed', baseStats.speed, ivs.speed, evs.speed, level)
    },
    types: species.types,
    moves: [], // Max 4
    ability: species.abilities[Math.floor(Math.random() * species.abilities.length)],
    nature: getRandomNature(),
    ivs,
    evs,
    xp: 0,
    xpToNext: calculateXpToLevel(level + 1),
    statusEffect: null,
    statModifiers: { atk: 0, def: 0, spAtk: 0, spDef: 0, speed: 0, accuracy: 0, evasion: 0 }
  };
};
```

### Stat Calculation Formula

```javascript
// Pokemon-style stat formula
const calculateStat = (statName, base, iv, ev, level) => {
  if (statName === 'hp') {
    return Math.floor(((2 * base + iv + Math.floor(ev / 4)) * level) / 100) + level + 10;
  }
  return Math.floor((((2 * base + iv + Math.floor(ev / 4)) * level) / 100) + 5);
};

// Simpler formula for lighter games
const calculateStatSimple = (base, level) => {
  return Math.floor(base * (1 + (level - 1) * 0.1));
};
```

### Natures (Optional stat modifiers)

```javascript
const natures = {
  adamant: { increase: 'attack', decrease: 'spAttack' },
  jolly: { increase: 'speed', decrease: 'spAttack' },
  modest: { increase: 'spAttack', decrease: 'attack' },
  timid: { increase: 'speed', decrease: 'attack' },
  bold: { increase: 'defense', decrease: 'attack' },
  // ... 25 total (including 5 neutral)
};

const applyNature = (stats, nature) => {
  if (nature.increase) stats[nature.increase] *= 1.1;
  if (nature.decrease) stats[nature.decrease] *= 0.9;
  return stats;
};
```

---

## Type Systems

### Type Chart (Simplified 9-type system)

```javascript
const typeChart = {
  //          NOR  FIR  WAT  GRS  ELE  ICE  FGT  PSY  DRK
  normal:   [ 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0 ],
  fire:     [ 1.0, 0.5, 0.5, 2.0, 1.0, 2.0, 1.0, 1.0, 1.0 ],
  water:    [ 1.0, 2.0, 0.5, 0.5, 1.0, 1.0, 1.0, 1.0, 1.0 ],
  grass:    [ 1.0, 0.5, 2.0, 0.5, 1.0, 1.0, 1.0, 1.0, 1.0 ],
  electric: [ 1.0, 1.0, 2.0, 0.5, 0.5, 1.0, 1.0, 1.0, 1.0 ],
  ice:      [ 1.0, 0.5, 0.5, 2.0, 1.0, 0.5, 1.0, 1.0, 1.0 ],
  fighting: [ 2.0, 1.0, 1.0, 1.0, 1.0, 2.0, 1.0, 0.5, 2.0 ],
  psychic:  [ 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 2.0, 0.5, 0.0 ],
  dark:     [ 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.5, 2.0, 0.5 ]
};

const getTypeEffectiveness = (moveType, defenderTypes) => {
  let multiplier = 1.0;
  defenderTypes.forEach(defType => {
    const typeIndex = Object.keys(typeChart).indexOf(defType);
    multiplier *= typeChart[moveType][typeIndex];
  });
  return multiplier;
};
```

### Effectiveness Messaging

```javascript
const effectivenessMessage = (multiplier) => {
  if (multiplier === 0) return "It had no effect...";
  if (multiplier < 1) return "It's not very effective...";
  if (multiplier > 1) return "It's super effective!";
  return null; // Normal effectiveness, no message
};
```

---

## Abilities & Moves

### Move Structure

```javascript
const createMove = (data) => ({
  name: data.name,
  type: data.type,
  category: data.category, // 'physical' | 'special' | 'status'
  power: data.power || 0,
  accuracy: data.accuracy || 100,
  pp: data.pp || 10,
  maxPp: data.pp || 10,
  priority: data.priority || 0,
  effects: data.effects || [],
  description: data.description
});

// Example moves
const moves = {
  tackle: createMove({
    name: 'Tackle',
    type: 'normal',
    category: 'physical',
    power: 40,
    accuracy: 100,
    pp: 35,
    description: 'A basic physical attack.'
  }),
  
  flamethrower: createMove({
    name: 'Flamethrower',
    type: 'fire',
    category: 'special',
    power: 90,
    accuracy: 100,
    pp: 15,
    effects: [{ type: 'burn', chance: 10 }],
    description: 'A powerful fire attack that may burn.'
  }),
  
  swordsDance: createMove({
    name: 'Swords Dance',
    type: 'normal',
    category: 'status',
    pp: 20,
    effects: [{ type: 'statBoost', stat: 'attack', stages: 2, target: 'self' }],
    description: 'Sharply raises Attack.'
  }),
  
  quickAttack: createMove({
    name: 'Quick Attack',
    type: 'normal',
    category: 'physical',
    power: 40,
    accuracy: 100,
    pp: 30,
    priority: 1, // Goes first
    description: 'A fast attack that always strikes first.'
  })
};
```

### Damage Formula

```javascript
const calculateDamage = (attacker, defender, move) => {
  if (move.category === 'status') return 0;
  
  // Determine which stats to use
  const attackStat = move.category === 'physical' 
    ? attacker.stats.attack 
    : attacker.stats.spAttack;
  const defenseStat = move.category === 'physical' 
    ? defender.stats.defense 
    : defender.stats.spDefense;
  
  // Base damage formula
  let damage = Math.floor(
    ((2 * attacker.level / 5 + 2) * move.power * (attackStat / defenseStat)) / 50 + 2
  );
  
  // STAB (Same Type Attack Bonus)
  if (attacker.types.includes(move.type)) {
    damage = Math.floor(damage * 1.5);
  }
  
  // Type effectiveness
  const effectiveness = getTypeEffectiveness(move.type, defender.types);
  damage = Math.floor(damage * effectiveness);
  
  // Critical hit (6.25% chance, 1.5x damage)
  const criticalHit = Math.random() < 0.0625;
  if (criticalHit) {
    damage = Math.floor(damage * 1.5);
  }
  
  // Random variance (85-100%)
  damage = Math.floor(damage * (0.85 + Math.random() * 0.15));
  
  return {
    damage: Math.max(1, damage),
    effectiveness,
    critical: criticalHit
  };
};
```

### Status Effects

```javascript
const statusEffects = {
  burn: {
    damagePerTurn: (creature) => Math.floor(creature.stats.hp / 16),
    statModifier: { attack: 0.5 },
    duration: Infinity, // Until healed
    message: 'is hurt by its burn!'
  },
  poison: {
    damagePerTurn: (creature) => Math.floor(creature.stats.hp / 8),
    duration: Infinity,
    message: 'is hurt by poison!'
  },
  paralysis: {
    statModifier: { speed: 0.5 },
    skipTurnChance: 0.25,
    duration: Infinity,
    message: 'is paralyzed! It can\'t move!'
  },
  sleep: {
    skipTurn: true,
    duration: [1, 3], // Random 1-3 turns
    message: 'is fast asleep.'
  },
  freeze: {
    skipTurn: true,
    thawChance: 0.2, // 20% to thaw each turn
    duration: Infinity,
    message: 'is frozen solid!'
  },
  confusion: {
    selfDamageChance: 0.33,
    duration: [1, 4],
    message: 'hurt itself in its confusion!'
  }
};
```

---

## Progression & Leveling

### XP Curve

```javascript
// Medium-fast growth curve (Pokemon-style)
const calculateXpToLevel = (level) => {
  return Math.floor(Math.pow(level, 3)); // level^3
};

// XP from battle
const calculateXpGain = (defeatedCreature, isWild, participantCount) => {
  const baseXp = defeatedCreature.species.baseXpYield;
  const levelFactor = defeatedCreature.level;
  const wildBonus = isWild ? 1 : 1.5; // Trainer battles give more
  return Math.floor((baseXp * levelFactor * wildBonus) / (7 * participantCount));
};
```

### Level Up

```javascript
const checkLevelUp = (creature) => {
  while (creature.xp >= creature.xpToNext) {
    creature.xp -= creature.xpToNext;
    creature.level++;
    creature.xpToNext = calculateXpToLevel(creature.level + 1);
    
    // Recalculate stats
    recalculateStats(creature);
    
    // Check for new moves
    const newMove = creature.species.learnset[creature.level];
    if (newMove) {
      return { leveledUp: true, newMove };
    }
  }
  return { leveledUp: false };
};
```

---

## Capture Mechanics

### Capture Formula

```javascript
const calculateCaptureRate = (creature, ball) => {
  const maxHp = creature.stats.hp;
  const currentHp = creature.currentHp;
  const catchRate = creature.species.catchRate; // 0-255
  const ballBonus = ball.catchRateModifier; // 1x for normal, 2x for great, etc.
  
  // Status bonuses
  let statusBonus = 1;
  if (['sleep', 'freeze'].includes(creature.statusEffect)) statusBonus = 2.5;
  if (['paralysis', 'burn', 'poison'].includes(creature.statusEffect)) statusBonus = 1.5;
  
  // Modified catch rate
  const modifiedRate = 
    ((3 * maxHp - 2 * currentHp) * catchRate * ballBonus * statusBonus) / (3 * maxHp);
  
  // Shake probability
  const shakeProbability = Math.min(255, Math.floor(modifiedRate)) / 255;
  
  return shakeProbability;
};

const attemptCapture = (creature, ball) => {
  const catchRate = calculateCaptureRate(creature, ball);
  const shakes = [0, 1, 2, 3].map(() => Math.random() < catchRate);
  
  const successfulShakes = shakes.filter(s => s).length;
  
  return {
    caught: successfulShakes === 4,
    shakes: successfulShakes,
    animation: successfulShakes // For visual feedback
  };
};
```

### Ball Types

```javascript
const ballTypes = {
  pokeball: { catchRateModifier: 1, cost: 200 },
  greatball: { catchRateModifier: 1.5, cost: 600 },
  ultraball: { catchRateModifier: 2, cost: 1200 },
  masterball: { catchRateModifier: 255, cost: Infinity } // Always catches
};
```

---

## Evolution & Growth

### Evolution Triggers

```javascript
const evolutionTriggers = {
  level: (creature, targetLevel) => creature.level >= targetLevel,
  item: (creature, item) => item === creature.species.evolutionItem,
  trade: (creature) => creature.tradedFlag === true,
  happiness: (creature) => creature.happiness >= 220,
  timeOfDay: (creature, time) => time === creature.species.evolutionTime,
  location: (creature, location) => location === creature.species.evolutionLocation,
  move: (creature, moveType) => creature.moves.some(m => m.type === moveType)
};

const checkEvolution = (creature, context) => {
  const evolution = creature.species.evolutions?.find(evo => {
    return evolutionTriggers[evo.trigger.type](creature, evo.trigger.value, context);
  });
  return evolution?.targetSpecies || null;
};
```

### Evolution Animation State

```javascript
const evolutionAnimation = {
  phases: [
    { name: 'glow', duration: 2000 },
    { name: 'transform', duration: 3000 },
    { name: 'reveal', duration: 1500 }
  ],
  cancelWindow: 5000 // Player can cancel during first 5 seconds
};
```

---

## Party Management

### Party Structure

```javascript
const createParty = () => ({
  creatures: [], // Max 6 active
  storage: [],   // PC boxes
  maxActive: 6,
  activeIndex: 0
});

const partyOperations = {
  addToParty: (party, creature) => {
    if (party.creatures.length < party.maxActive) {
      party.creatures.push(creature);
      return { success: true, location: 'party' };
    }
    party.storage.push(creature);
    return { success: true, location: 'storage' };
  },
  
  swap: (party, index1, index2) => {
    [party.creatures[index1], party.creatures[index2]] = 
    [party.creatures[index2], party.creatures[index1]];
  },
  
  getFirstHealthy: (party) => {
    return party.creatures.find(c => c.currentHp > 0);
  },
  
  isWiped: (party) => {
    return party.creatures.every(c => c.currentHp <= 0);
  }
};
```

---

## AI Battle Logic

### Move Selection

```javascript
const selectAIMove = (aiCreature, playerCreature, difficulty = 'medium') => {
  const availableMoves = aiCreature.moves.filter(m => m.pp > 0);
  
  if (difficulty === 'easy') {
    // Random move
    return availableMoves[Math.floor(Math.random() * availableMoves.length)];
  }
  
  if (difficulty === 'medium') {
    // Prefer super effective moves
    const scored = availableMoves.map(move => ({
      move,
      score: scoreMoveEffectiveness(move, playerCreature)
    }));
    scored.sort((a, b) => b.score - a.score);
    
    // 70% chance to pick best move, 30% random
    return Math.random() < 0.7 ? scored[0].move : 
      availableMoves[Math.floor(Math.random() * availableMoves.length)];
  }
  
  if (difficulty === 'hard') {
    // Full damage calculation, considers status, setup moves
    return calculateOptimalMove(aiCreature, playerCreature, availableMoves);
  }
};

const scoreMoveEffectiveness = (move, target) => {
  if (move.category === 'status') return 50; // Moderate priority
  const effectiveness = getTypeEffectiveness(move.type, target.types);
  return move.power * effectiveness;
};
```

### Switch Logic

```javascript
const shouldAISwitch = (activeCreature, playerCreature, party, difficulty) => {
  if (difficulty === 'easy') return false; // Never switches
  
  // Check if current matchup is bad
  const currentMatchup = evaluateMatchup(activeCreature, playerCreature);
  
  if (currentMatchup < 0.5) {
    // Look for better option
    const betterOption = party.creatures.find(c => 
      c.currentHp > 0 && 
      c !== activeCreature &&
      evaluateMatchup(c, playerCreature) > currentMatchup
    );
    
    if (betterOption && Math.random() < (difficulty === 'hard' ? 0.8 : 0.4)) {
      return betterOption;
    }
  }
  
  return null;
};

const evaluateMatchup = (attacker, defender) => {
  // Score based on type advantage and stats
  let score = 0.5; // Neutral
  
  // Type advantage
  const bestMove = attacker.moves.reduce((best, move) => {
    const eff = getTypeEffectiveness(move.type, defender.types);
    return eff > best ? eff : best;
  }, 1);
  
  score += (bestMove - 1) * 0.25;
  
  // Speed advantage
  if (attacker.stats.speed > defender.stats.speed) score += 0.1;
  
  return Math.min(1, Math.max(0, score));
};
```
