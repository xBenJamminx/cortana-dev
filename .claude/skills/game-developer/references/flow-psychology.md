# Flow Psychology & Game Feel Reference

## Table of Contents
1. [Flow State Theory](#flow-state-theory)
2. [Difficulty Design](#difficulty-design)
3. [Game Feel & Juice](#game-feel--juice)
4. [Feedback Systems](#feedback-systems)
5. [Player Psychology](#player-psychology)
6. [Onboarding & Tutorials](#onboarding--tutorials)
7. [Retention Mechanics](#retention-mechanics)

---

## Flow State Theory

### The Flow Channel

```
Challenge
    │
    │     ANXIETY           ┌─────────────┐
    │     (Too hard)        │             │
    │                       │   FLOW      │
    │   ┌───────────────────│   ZONE      │
    │   │                   │             │
    │   │                   └─────────────┘
    │   │     
    │   │          BOREDOM
    │   │          (Too easy)
    │   │
    └───┴────────────────────────────────── Skill
```

**Flow occurs when:**
- Challenge ≈ Skill level
- Clear goals
- Immediate feedback
- Sense of control
- Concentration is possible
- Intrinsic motivation

### Maintaining Flow

```javascript
const flowMaintenance = {
  // Dynamic difficulty adjustment
  trackPlayerPerformance: (metrics) => {
    const { winRate, timeToComplete, retries, healthRemaining } = metrics;
    return calculateSkillLevel(metrics);
  },
  
  adjustChallenge: (currentDifficulty, playerSkill) => {
    const gap = playerSkill - currentDifficulty;
    
    if (gap > 0.3) return 'increase'; // Player crushing it
    if (gap < -0.3) return 'decrease'; // Player struggling
    return 'maintain'; // In the zone
  },
  
  // Invisible adjustments
  rubberBanding: {
    aiAccuracy: 'Reduce when player is low HP',
    spawnTiming: 'Delay when player is overwhelmed',
    critChance: 'Boost when player on losing streak'
  }
};
```

---

## Difficulty Design

### Difficulty Curves

**Linear (Boring):**
```
Difficulty
    │
    │                    ╱
    │                 ╱
    │              ╱
    │           ╱
    │        ╱
    │     ╱
    │  ╱
    └─────────────────── Progress
```

**Stepped (Satisfying):**
```
Difficulty
    │
    │                       ┌───
    │                   ┌───┘
    │               ┌───┘
    │           ┌───┘
    │       ┌───┘
    │   ┌───┘
    │───┘
    └─────────────────── Progress
       ↑       ↑       ↑
    New     New     New
    mechanic mechanic mechanic
```

**Sawtooth (Recommended):**
```
Difficulty
    │
    │                           /\
    │                     /\   /  \
    │               /\   /  \ /    
    │         /\   /  \ /     
    │   /\   /  \ /         
    │  /  \ /              
    │ /    
    └─────────────────────────── Progress
      ↑  ↑    ↑  ↑    ↑  ↑
    Rise Fall Rise Fall Rise Fall
    (challenge + breather pattern)
```

### Difficulty Settings

```javascript
const difficultyPresets = {
  easy: {
    label: 'Story Mode',
    description: 'Focus on narrative, minimal challenge',
    multipliers: {
      enemyHealth: 0.7,
      enemyDamage: 0.6,
      playerDamage: 1.3,
      resourceGain: 1.5,
      revives: 3
    }
  },
  normal: {
    label: 'Adventure',
    description: 'Balanced challenge for most players',
    multipliers: {
      enemyHealth: 1.0,
      enemyDamage: 1.0,
      playerDamage: 1.0,
      resourceGain: 1.0,
      revives: 1
    }
  },
  hard: {
    label: 'Champion',
    description: 'For experienced players seeking mastery',
    multipliers: {
      enemyHealth: 1.4,
      enemyDamage: 1.3,
      playerDamage: 0.9,
      resourceGain: 0.8,
      revives: 0
    }
  }
};
```

### Skill Floor vs. Skill Ceiling

```javascript
const skillDesign = {
  // Skill floor: minimum competence to progress
  floor: {
    lowFloor: 'Anyone can beat the game (Pokemon)',
    highFloor: 'Requires dedication to progress (Dark Souls)'
  },
  
  // Skill ceiling: maximum mastery potential
  ceiling: {
    lowCeiling: 'Limited optimization (visual novels)',
    highCeiling: 'Near-infinite mastery (fighting games, speedrunning)'
  },
  
  // Sweet spot for broad appeal
  recommended: {
    floor: 'Low - accessible to newcomers',
    ceiling: 'High - rewards mastery',
    example: 'Easy to beat, hard to master'
  }
};
```

---

## Game Feel & Juice

### The Juice Checklist

Every player action should have:
1. **Visual feedback** (animation, particles, color change)
2. **Audio feedback** (sound effect, music change)
3. **Tactile feedback** (screen shake, pause frame)
4. **Numerical feedback** (damage numbers, scores)

### Screen Shake Implementation

```javascript
const screenShake = (intensity, duration) => {
  const startTime = Date.now();
  
  const shake = () => {
    const elapsed = Date.now() - startTime;
    if (elapsed > duration) {
      document.body.style.transform = '';
      return;
    }
    
    // Decay over time
    const decay = 1 - (elapsed / duration);
    const currentIntensity = intensity * decay;
    
    const x = (Math.random() - 0.5) * currentIntensity;
    const y = (Math.random() - 0.5) * currentIntensity;
    
    document.body.style.transform = `translate(${x}px, ${y}px)`;
    requestAnimationFrame(shake);
  };
  
  shake();
};

// Usage
// Light hit: screenShake(3, 100)
// Heavy hit: screenShake(8, 200)
// Explosion: screenShake(15, 400)
```

### Hit Pause (Freeze Frames)

```javascript
const hitPause = (duration = 50) => {
  // Pause game time briefly on impact
  gameState.paused = true;
  
  setTimeout(() => {
    gameState.paused = false;
  }, duration);
};

// Apply different durations
const hitPauseDurations = {
  lightAttack: 30,
  heavyAttack: 60,
  critical: 100,
  superEffective: 80,
  knockout: 150
};
```

### Animation Easing

```javascript
const easingFunctions = {
  // Never use linear for game animations
  linear: t => t, // DON'T USE
  
  // Quick start, slow end (satisfying for arrivals)
  easeOut: t => 1 - Math.pow(1 - t, 3),
  
  // Slow start, quick end (good for anticipation)
  easeIn: t => Math.pow(t, 3),
  
  // Overshoot and settle (bouncy, playful)
  easeOutBack: t => {
    const c = 1.70158;
    return 1 + (c + 1) * Math.pow(t - 1, 3) + c * Math.pow(t - 1, 2);
  },
  
  // Bounce at end (cartoony)
  easeOutBounce: t => {
    if (t < 1 / 2.75) return 7.5625 * t * t;
    if (t < 2 / 2.75) return 7.5625 * (t -= 1.5 / 2.75) * t + 0.75;
    if (t < 2.5 / 2.75) return 7.5625 * (t -= 2.25 / 2.75) * t + 0.9375;
    return 7.5625 * (t -= 2.625 / 2.75) * t + 0.984375;
  }
};
```

### Particle Effects

```javascript
const particlePresets = {
  hit: {
    count: 8,
    spread: 360,
    speed: { min: 50, max: 150 },
    lifetime: 300,
    size: { start: 8, end: 0 },
    color: '#ffff00'
  },
  
  death: {
    count: 20,
    spread: 360,
    speed: { min: 100, max: 300 },
    lifetime: 500,
    size: { start: 12, end: 0 },
    color: '#ff4444'
  },
  
  levelUp: {
    count: 30,
    spread: 360,
    speed: { min: 50, max: 200 },
    lifetime: 1000,
    size: { start: 6, end: 10 },
    color: '#00ffff',
    gravity: -50 // Float up
  },
  
  sparkle: {
    count: 5,
    spread: 45,
    speed: { min: 20, max: 60 },
    lifetime: 400,
    size: { start: 4, end: 0 },
    color: '#ffffff'
  }
};
```

---

## Feedback Systems

### Positive Feedback Loop

```
Player succeeds → Reward/Power → Easier success → More rewards
```

**When to use:** Early game, tutorial, when player needs momentum

**Example (Tower Defense):**
```javascript
// Killing enemies gives gold → buy more towers → kill faster → more gold
const positiveLoop = {
  trigger: 'enemyKill',
  reward: { gold: enemy.value * killStreak.multiplier },
  powerup: 'More gold = more towers',
  result: 'Faster kills'
};
```

### Negative Feedback Loop

```
Player succeeds too much → Challenge increases → Success harder
Player struggles → Assistance → Success easier
```

**When to use:** To maintain balance, prevent runaway leads, keep games close

**Example (RTS AI):**
```javascript
// Rubber-banding AI
const rubberBanding = (playerScore, aiScore) => {
  const ratio = playerScore / aiScore;
  
  if (ratio > 1.5) {
    // Player dominating - boost AI
    return { aiResourceBonus: 1.2, aiDamageBonus: 1.1 };
  }
  if (ratio < 0.7) {
    // Player struggling - subtle help
    return { playerCritBonus: 1.1, enemyAccuracyPenalty: 0.9 };
  }
  return {}; // No adjustment
};
```

### Feedback Timing

```javascript
const feedbackTiming = {
  // Immediate (0-100ms)
  immediate: ['Hit spark', 'Sound effect', 'Button press response'],
  
  // Quick (100-500ms)
  quick: ['Damage numbers', 'Enemy reaction', 'UI update'],
  
  // Delayed (500ms-2s)
  delayed: ['Death animation', 'XP gain', 'Loot drop'],
  
  // Deferred (end of action/round)
  deferred: ['Wave complete summary', 'Battle results', 'Level up'],
  
  // Long-term (session/game end)
  longTerm: ['Statistics screen', 'Achievements', 'Unlocks']
};
```

---

## Player Psychology

### Motivation Types

```javascript
const motivationProfiles = {
  // Bartle's Player Types (adapted)
  achiever: {
    drives: ['Completion', 'Mastery', 'Collection'],
    features: ['Achievements', 'Leaderboards', 'Rare unlocks'],
    percentage: '40%'
  },
  
  explorer: {
    drives: ['Discovery', 'Secrets', 'Lore'],
    features: ['Hidden areas', 'Easter eggs', 'World building'],
    percentage: '30%'
  },
  
  socializer: {
    drives: ['Cooperation', 'Competition', 'Community'],
    features: ['Multiplayer', 'Sharing', 'Chat'],
    percentage: '20%'
  },
  
  competitor: {
    drives: ['Dominance', 'Ranking', 'Skill expression'],
    features: ['PvP', 'Rankings', 'Challenges'],
    percentage: '10%'
  }
};
```

### Loss Aversion

Players feel losses ~2x more than equivalent gains.

```javascript
const lossAversionDesign = {
  // Frame rewards as avoiding loss
  framing: {
    bad: 'Gain 10% bonus damage',
    good: 'Don\'t miss out on 10% bonus damage!'
  },
  
  // Protect player investment
  protection: {
    autosave: 'Frequent saves prevent loss of progress',
    partialReward: 'Even failed attempts give something',
    insuranceMechanic: 'Spent currency gives backup rewards'
  },
  
  // Make losses feel fair
  fairness: {
    telegraphedAttacks: 'Player could have avoided',
    resourceWarnings: 'Low health/ammo alerts',
    undoOptions: 'Confirm destructive actions'
  }
};
```

### Variable Reward Schedules

```javascript
const rewardSchedules = {
  // Fixed ratio (every X actions)
  fixed: {
    pattern: 'Reward every 10 enemies',
    effect: 'Predictable, methodical play',
    engagement: 'Medium'
  },
  
  // Variable ratio (average X, but random)
  variable: {
    pattern: 'Reward averages every 10, but could be 2 or 20',
    effect: 'Highly engaging, "one more try"',
    engagement: 'Very High',
    example: 'Rare creature encounters, critical hits, loot drops'
  },
  
  // Fixed interval (every X seconds)
  fixedInterval: {
    pattern: 'Reward available every 60 seconds',
    effect: 'Scheduled engagement',
    engagement: 'Low-Medium',
    example: 'Daily login rewards'
  }
};
```

---

## Onboarding & Tutorials

### Tutorial Principles

1. **Teach by doing, not reading**
2. **Introduce one concept at a time**
3. **Let players fail safely**
4. **Repeat with variation**

### Progressive Disclosure

```javascript
const tutorialStages = {
  stage1_movement: {
    teaches: 'Basic movement',
    environment: 'Safe, no enemies',
    goal: 'Reach point B',
    unlockNext: 'Complete movement'
  },
  
  stage2_interaction: {
    teaches: 'Interact with objects',
    environment: 'Simple puzzle',
    goal: 'Open the door',
    unlockNext: 'Open door'
  },
  
  stage3_combat: {
    teaches: 'Basic attack',
    environment: 'One weak enemy',
    goal: 'Defeat enemy',
    unlockNext: 'Win fight',
    safetyNet: 'Enemy can\'t kill player'
  },
  
  stage4_advanced: {
    teaches: 'Special abilities',
    environment: 'Enemy requires ability',
    goal: 'Use ability to win',
    unlockNext: 'Use special move'
  }
};
```

### Contextual Tips

```javascript
const contextualTips = {
  triggers: {
    lowHealth: {
      condition: 'health < 20%',
      message: 'Press [H] to use a healing item!',
      showOnce: true
    },
    
    firstBoss: {
      condition: 'boss.type === "first" && boss.health === boss.maxHealth',
      message: 'Bosses have patterns. Watch for the wind-up!',
      showOnce: true
    },
    
    idleTooLong: {
      condition: 'idleTime > 30000',
      message: 'Need help? Check the menu for hints.',
      showOnce: false
    },
    
    repeatedDeath: {
      condition: 'deathCount >= 3 && sameLocation',
      message: 'Having trouble? Try a different strategy.',
      showOnce: false,
      offerHelp: true
    }
  }
};
```

---

## Retention Mechanics

### Session Hooks

```javascript
const sessionHooks = {
  // Start of session
  welcomeBack: {
    showProgress: 'You\'ve collected 47/100 creatures!',
    tease: 'New area unlocked: The Frozen Peaks',
    incentive: 'Daily bonus: 500 gold'
  },
  
  // End of session
  saveAndQuit: {
    summarize: 'Great session! You gained 3 levels.',
    tease: 'Almost at the next boss...',
    remind: 'Don\'t forget: Tournament starts tomorrow!'
  },
  
  // Interrupt prevention
  midSession: {
    unsavedWarning: 'You have unsaved progress!',
    streakWarning: 'Quitting will break your win streak.',
    suggestion: 'Reach the next checkpoint?'
  }
};
```

### Progression Visibility

```javascript
const progressIndicators = {
  // Always visible
  persistent: {
    level: 'Current level / XP to next',
    currency: 'Gold count',
    collection: '47/100 creatures discovered'
  },
  
  // Milestone celebrations
  milestones: {
    percentage: [25, 50, 75, 100],
    message: 'Halfway there! 50% complete!',
    reward: 'Bonus unlock at each milestone'
  },
  
  // Near-miss motivation
  almostThere: {
    condition: 'progress > 90%',
    message: 'So close! Just 3 more to go!',
    effect: 'Increased motivation to complete'
  }
};
```

### The Zeigarnik Effect

People remember incomplete tasks better than completed ones.

```javascript
const incompletionHooks = {
  // Leave things visibly unfinished
  mapFog: 'Unexplored areas visible but inaccessible',
  lockedContent: 'Show silhouettes of locked creatures',
  questLog: 'Active quests always visible',
  
  // Partial progress
  partialRewards: 'Collect 3/5 gems for chest',
  nearMiss: 'Just missed catching that rare one!',
  
  // Cliffhangers
  storyTease: 'End sessions mid-story beat',
  mechanicTease: 'Preview next unlock'
};
```
