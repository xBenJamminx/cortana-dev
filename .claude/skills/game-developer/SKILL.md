---
name: game-developer
description: Comprehensive game design and development expertise for creating playable browser games. Use when asked to build games, design game mechanics, create game design documents, implement game systems, or discuss game theory. Specializes in RTS (real-time strategy), tower defense, and RPG/creature-collection games (Pokemon-style). Covers flow psychology, narrative design, progression systems, balancing, and React/HTML implementation. Triggers on requests like "build me a game", "design a tower defense", "create an RPG battle system", "make a Pokemon clone", "help with game mechanics", "game design document", or any game development task.
---

# Game Developer

Expert game designer and developer specializing in strategy, skill-based, and RPG games with emphasis on flow, narrative, and playable implementations.

## Core Philosophy

Great games emerge from the intersection of three pillars:
1. **Flow** — Maintaining optimal challenge-to-skill ratio
2. **Systems** — Interlocking mechanics that create emergent gameplay
3. **Narrative** — Story and progression that give meaning to player actions

## Workflow

### 1. Determine Request Type

**Design consultation?** → Discuss theory, provide GDD structure, analyze mechanics
**Build a playable game?** → Follow implementation workflow below
**Specific mechanic help?** → Load relevant reference file for genre

### 2. For Playable Games

1. Clarify core loop and genre (RTS / Tower Defense / RPG / Hybrid)
2. Define scope (prototype vs. polished demo)
3. Load relevant reference files based on genre
4. Implement using React artifact patterns
5. Iterate on feel and balance

### 3. Reference Files by Need

| Need | Reference |
|------|-----------|
| RTS mechanics (economy, units, combat) | [rts-mechanics.md](references/rts-mechanics.md) |
| Tower defense (waves, paths, towers) | [tower-defense.md](references/tower-defense.md) |
| RPG/Pokemon (battles, creatures, progression) | [rpg-mechanics.md](references/rpg-mechanics.md) |
| Story, dialogue, narrative pacing | [narrative-design.md](references/narrative-design.md) |
| Flow state, difficulty, game feel | [flow-psychology.md](references/flow-psychology.md) |
| React patterns, game loops, state | [implementation.md](references/implementation.md) |

**Always load relevant references before implementing.** Genre-specific files contain critical formulas, patterns, and code structures.

## Quick Design Principles

### The Core Loop
Every game needs a tight core loop: **Action → Feedback → Reward → Decision**

```
Player acts → Game responds immediately → 
Reward/consequence delivered → Player makes next decision
```

Loop duration by genre:
- Tower Defense: 2-5 seconds (place tower → see effect)
- RTS: 5-15 seconds (build/move → tactical outcome)
- RPG Battle: 10-30 seconds (turn cycle)

### Progression Curves

```
Power
  │      ╭──────── Mastery plateau
  │    ╱
  │  ╱   ← Skill ceiling
  │╱
  └─────────────── Time
    ↑
    Learning curve (must feel achievable)
```

### Balancing Triangle

```
       POWER
        /\
       /  \
      /    \
     /      \
    /________\
 COST        SPEED
```

Every unit/tower/ability trades between these three axes.

## Implementation Standards

### React Game Artifacts

All playable games use React with these conventions:

```jsx
// State structure pattern
const [gameState, setGameState] = useState({
  phase: 'setup', // setup | playing | paused | victory | defeat
  tick: 0,
  entities: [],
  resources: {},
  ui: { selected: null, hovering: null }
});

// Game loop pattern
useEffect(() => {
  if (gameState.phase !== 'playing') return;
  const interval = setInterval(() => {
    setGameState(prev => gameLoop(prev));
  }, 1000 / 60); // 60 FPS
  return () => clearInterval(interval);
}, [gameState.phase]);
```

### Visual Feedback Checklist

- [ ] Hover states on all interactive elements
- [ ] Click/selection feedback (visual + optional sound cue description)
- [ ] Damage numbers or effect indicators
- [ ] Resource change animations
- [ ] State transitions (fade, slide, scale)

### Juice Principles

Small details that make games feel alive:
- Easing on all animations (never linear)
- Screen shake on impacts (subtle, 2-4px)
- Particle effects for destruction/creation
- Number countups for scores/damage
- Anticipation frames before big actions

## Scope Templates

### Prototype (30-60 min build)
- Single core mechanic working
- Placeholder visuals (colored shapes)
- No progression system
- Win/lose condition

### Demo (2-4 hour build)
- Core loop complete
- 3-5 unit/tower/creature types
- Basic progression (levels or waves)
- Simple UI with feedback
- Polished game feel

### Full Experience (iterative)
- Multiple interlocking systems
- Narrative wrapper
- Save/load state
- Balancing pass
- Tutorial flow
