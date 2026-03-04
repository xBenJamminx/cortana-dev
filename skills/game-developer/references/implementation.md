# Implementation Patterns Reference

## Table of Contents
1. [React Game Architecture](#react-game-architecture)
2. [Game Loop Patterns](#game-loop-patterns)
3. [State Management](#state-management)
4. [Rendering Strategies](#rendering-strategies)
5. [Input Handling](#input-handling)
6. [Animation Systems](#animation-systems)
7. [Audio Integration](#audio-integration)
8. [Performance Optimization](#performance-optimization)

---

## React Game Architecture

### Core Component Structure

```jsx
const Game = () => {
  const [gameState, setGameState] = useState(initialState);
  const [ui, setUi] = useState({ screen: 'title' });
  
  // Game screens
  const screens = {
    title: <TitleScreen onStart={() => setUi({ screen: 'game' })} />,
    game: <GameScreen state={gameState} dispatch={dispatch} />,
    pause: <PauseMenu onResume={() => setUi({ screen: 'game' })} />,
    victory: <VictoryScreen stats={gameState.stats} />,
    defeat: <DefeatScreen onRetry={resetGame} />
  };
  
  return (
    <div className="game-container">
      {screens[ui.screen]}
    </div>
  );
};
```

### State Shape by Genre

**Tower Defense:**
```javascript
const towerDefenseState = {
  phase: 'build', // 'build' | 'wave' | 'victory' | 'defeat'
  wave: 1,
  lives: 20,
  gold: 100,
  towers: [], // { id, type, x, y, level, cooldown }
  enemies: [], // { id, type, x, y, health, pathIndex, effects }
  projectiles: [], // { id, x, y, targetId, damage, speed }
  path: [], // [{x, y}, ...]
  selected: null, // Tower ID or shop item
};
```

**RTS:**
```javascript
const rtsState = {
  phase: 'playing', // 'playing' | 'paused' | 'victory' | 'defeat'
  tick: 0,
  players: {
    player: {
      resources: { gold: 500, wood: 200 },
      units: [],
      buildings: [],
      fog: new Set(), // Explored tiles
      vision: new Set() // Currently visible tiles
    },
    enemy: { /* same structure */ }
  },
  map: { width: 50, height: 50, tiles: [] },
  selected: [], // Unit IDs
  rallyPoint: null
};
```

**RPG/Pokemon:**
```javascript
const rpgState = {
  phase: 'exploring', // 'exploring' | 'battle' | 'menu' | 'dialogue'
  player: {
    position: { x: 0, y: 0 },
    party: [], // Creatures
    inventory: [],
    gold: 1000,
    badges: []
  },
  battle: null, // { playerActive, enemyActive, turn, actions }
  dialogue: null, // { speaker, text, choices }
  world: {
    currentMap: 'hometown',
    npcs: [],
    events: {}
  }
};
```

---

## Game Loop Patterns

### Fixed Timestep Loop

```jsx
const TICK_RATE = 60; // Updates per second
const TICK_DURATION = 1000 / TICK_RATE;

const useGameLoop = (gameState, setGameState, isPlaying) => {
  const lastUpdateRef = useRef(Date.now());
  const accumulatorRef = useRef(0);
  
  useEffect(() => {
    if (!isPlaying) return;
    
    let frameId;
    
    const loop = () => {
      const now = Date.now();
      const delta = now - lastUpdateRef.current;
      lastUpdateRef.current = now;
      accumulatorRef.current += delta;
      
      // Fixed timestep updates
      while (accumulatorRef.current >= TICK_DURATION) {
        setGameState(prev => update(prev, TICK_DURATION));
        accumulatorRef.current -= TICK_DURATION;
      }
      
      frameId = requestAnimationFrame(loop);
    };
    
    frameId = requestAnimationFrame(loop);
    return () => cancelAnimationFrame(frameId);
  }, [isPlaying]);
};
```

### Turn-Based Loop

```jsx
const useTurnLoop = () => {
  const [battleState, setBattleState] = useState(null);
  
  const executeTurn = async (action) => {
    setBattleState(prev => ({ ...prev, phase: 'executing' }));
    
    // 1. Determine order
    const turnOrder = calculateTurnOrder(battleState, action);
    
    // 2. Execute each action with animations
    for (const turn of turnOrder) {
      await executeAction(turn);
      await delay(500); // Animation time
      
      // Check for KO after each action
      const ko = checkKnockouts(battleState);
      if (ko) {
        await handleKnockout(ko);
      }
    }
    
    // 3. Apply end-of-turn effects
    await applyStatusEffects();
    
    // 4. Check win/lose
    if (checkBattleEnd()) {
      setBattleState(prev => ({ ...prev, phase: 'ended' }));
    } else {
      setBattleState(prev => ({ ...prev, phase: 'selecting' }));
    }
  };
  
  return { battleState, executeTurn };
};
```

### Wave-Based Loop (Tower Defense)

```jsx
const useWaveLoop = (gameState, setGameState) => {
  useEffect(() => {
    if (gameState.phase !== 'wave') return;
    
    const interval = setInterval(() => {
      setGameState(prev => {
        let next = { ...prev };
        
        // Spawn enemies
        next = spawnEnemies(next);
        
        // Move enemies
        next = moveEnemies(next);
        
        // Tower targeting and shooting
        next = processTowers(next);
        
        // Move projectiles
        next = moveProjectiles(next);
        
        // Check collisions
        next = checkCollisions(next);
        
        // Remove dead enemies, award gold
        next = cleanupDead(next);
        
        // Check wave complete
        if (next.enemies.length === 0 && next.spawnsRemaining === 0) {
          next.phase = 'build';
          next.wave++;
        }
        
        // Check defeat
        if (next.lives <= 0) {
          next.phase = 'defeat';
        }
        
        return next;
      });
    }, 1000 / 60);
    
    return () => clearInterval(interval);
  }, [gameState.phase]);
};
```

---

## State Management

### Reducer Pattern (Complex Games)

```javascript
const gameReducer = (state, action) => {
  switch (action.type) {
    case 'PLACE_TOWER':
      if (state.gold < action.tower.cost) return state;
      return {
        ...state,
        gold: state.gold - action.tower.cost,
        towers: [...state.towers, {
          id: Date.now(),
          ...action.tower,
          x: action.x,
          y: action.y,
          level: 1,
          cooldown: 0
        }]
      };
      
    case 'UPGRADE_TOWER':
      return {
        ...state,
        gold: state.gold - action.cost,
        towers: state.towers.map(t =>
          t.id === action.towerId
            ? { ...t, level: t.level + 1, ...action.upgrades }
            : t
        )
      };
      
    case 'DAMAGE_ENEMY':
      return {
        ...state,
        enemies: state.enemies.map(e =>
          e.id === action.enemyId
            ? { ...e, health: e.health - action.damage }
            : e
        )
      };
      
    case 'ENEMY_REACHED_END':
      return {
        ...state,
        lives: state.lives - 1,
        enemies: state.enemies.filter(e => e.id !== action.enemyId)
      };
      
    default:
      return state;
  }
};

// Usage
const [state, dispatch] = useReducer(gameReducer, initialState);
dispatch({ type: 'PLACE_TOWER', tower: basicTower, x: 100, y: 200 });
```

### Immutable Update Patterns

```javascript
// Adding to array
const addEntity = (state, entity) => ({
  ...state,
  entities: [...state.entities, entity]
});

// Removing from array
const removeEntity = (state, id) => ({
  ...state,
  entities: state.entities.filter(e => e.id !== id)
});

// Updating item in array
const updateEntity = (state, id, updates) => ({
  ...state,
  entities: state.entities.map(e =>
    e.id === id ? { ...e, ...updates } : e
  )
});

// Nested update
const updateNestedStat = (state, creatureId, stat, value) => ({
  ...state,
  party: state.party.map(c =>
    c.id === creatureId
      ? { ...c, stats: { ...c.stats, [stat]: value } }
      : c
  )
});
```

---

## Rendering Strategies

### Grid-Based Rendering

```jsx
const GridMap = ({ tiles, tileSize, onTileClick }) => (
  <div 
    className="grid-map"
    style={{
      display: 'grid',
      gridTemplateColumns: `repeat(${tiles[0].length}, ${tileSize}px)`,
      gap: '1px'
    }}
  >
    {tiles.flat().map((tile, i) => (
      <div
        key={i}
        className={`tile tile-${tile.type}`}
        onClick={() => onTileClick(i % tiles[0].length, Math.floor(i / tiles[0].length))}
        style={{
          width: tileSize,
          height: tileSize,
          backgroundColor: getTileColor(tile)
        }}
      />
    ))}
  </div>
);
```

### Entity Rendering (Absolute Positioning)

```jsx
const GameCanvas = ({ entities, viewOffset }) => (
  <div className="game-canvas" style={{ position: 'relative', overflow: 'hidden' }}>
    {entities.map(entity => (
      <div
        key={entity.id}
        className={`entity entity-${entity.type}`}
        style={{
          position: 'absolute',
          left: entity.x - viewOffset.x,
          top: entity.y - viewOffset.y,
          width: entity.width,
          height: entity.height,
          transform: `rotate(${entity.rotation}deg)`,
          transition: 'left 0.05s linear, top 0.05s linear'
        }}
      >
        {entity.sprite}
        {entity.healthBar && (
          <HealthBar current={entity.health} max={entity.maxHealth} />
        )}
      </div>
    ))}
  </div>
);
```

### Canvas Rendering (Performance)

```jsx
const CanvasGame = ({ state }) => {
  const canvasRef = useRef(null);
  
  useEffect(() => {
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    
    const render = () => {
      // Clear
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      
      // Draw background
      drawBackground(ctx, state.map);
      
      // Draw entities (sorted by y for depth)
      const sorted = [...state.entities].sort((a, b) => a.y - b.y);
      sorted.forEach(entity => drawEntity(ctx, entity));
      
      // Draw UI overlay
      drawUI(ctx, state);
    };
    
    render();
  }, [state]);
  
  return <canvas ref={canvasRef} width={800} height={600} />;
};
```

---

## Input Handling

### Click/Tap Handling

```jsx
const useGameInput = (state, dispatch) => {
  const handleClick = (e, gameArea) => {
    const rect = gameArea.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    
    // Check what was clicked
    const clickedEntity = state.entities.find(entity =>
      x >= entity.x && x <= entity.x + entity.width &&
      y >= entity.y && y <= entity.y + entity.height
    );
    
    if (clickedEntity) {
      dispatch({ type: 'SELECT_ENTITY', entity: clickedEntity });
    } else if (state.selected && state.placingTower) {
      dispatch({ type: 'PLACE_TOWER', x, y, tower: state.selected });
    } else {
      dispatch({ type: 'DESELECT' });
    }
  };
  
  return { handleClick };
};
```

### Keyboard Controls

```jsx
const useKeyboardControls = (dispatch) => {
  useEffect(() => {
    const handleKeyDown = (e) => {
      const keyActions = {
        'ArrowUp': () => dispatch({ type: 'MOVE', direction: 'up' }),
        'ArrowDown': () => dispatch({ type: 'MOVE', direction: 'down' }),
        'ArrowLeft': () => dispatch({ type: 'MOVE', direction: 'left' }),
        'ArrowRight': () => dispatch({ type: 'MOVE', direction: 'right' }),
        'Space': () => dispatch({ type: 'ACTION' }),
        'Escape': () => dispatch({ type: 'PAUSE' }),
        '1': () => dispatch({ type: 'SELECT_ABILITY', index: 0 }),
        '2': () => dispatch({ type: 'SELECT_ABILITY', index: 1 }),
        '3': () => dispatch({ type: 'SELECT_ABILITY', index: 2 }),
        '4': () => dispatch({ type: 'SELECT_ABILITY', index: 3 }),
      };
      
      if (keyActions[e.key]) {
        e.preventDefault();
        keyActions[e.key]();
      }
    };
    
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [dispatch]);
};
```

### Drag and Drop

```jsx
const useDragDrop = () => {
  const [dragging, setDragging] = useState(null);
  const [dragOffset, setDragOffset] = useState({ x: 0, y: 0 });
  
  const handleDragStart = (e, item) => {
    setDragging(item);
    setDragOffset({
      x: e.clientX - item.x,
      y: e.clientY - item.y
    });
  };
  
  const handleDragMove = (e) => {
    if (!dragging) return;
    // Update preview position
  };
  
  const handleDragEnd = (e, dropZone) => {
    if (!dragging) return;
    
    const dropX = e.clientX - dragOffset.x;
    const dropY = e.clientY - dragOffset.y;
    
    if (isValidDrop(dropZone, dropX, dropY)) {
      onDrop(dragging, dropX, dropY);
    }
    
    setDragging(null);
  };
  
  return { dragging, handleDragStart, handleDragMove, handleDragEnd };
};
```

---

## Animation Systems

### CSS Transitions

```jsx
const AnimatedEntity = ({ entity, children }) => (
  <div
    className="animated-entity"
    style={{
      position: 'absolute',
      left: entity.x,
      top: entity.y,
      transition: `
        left ${entity.moveSpeed}ms linear,
        top ${entity.moveSpeed}ms linear,
        transform 200ms ease-out,
        opacity 300ms ease-out
      `,
      transform: entity.hit ? 'scale(1.1)' : 'scale(1)',
      opacity: entity.dying ? 0 : 1
    }}
  >
    {children}
  </div>
);
```

### Keyframe Animations

```css
@keyframes bounce {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-10px); }
}

@keyframes shake {
  0%, 100% { transform: translateX(0); }
  25% { transform: translateX(-5px); }
  75% { transform: translateX(5px); }
}

@keyframes pulse {
  0%, 100% { transform: scale(1); opacity: 1; }
  50% { transform: scale(1.1); opacity: 0.8; }
}

@keyframes float-up {
  from { 
    transform: translateY(0); 
    opacity: 1; 
  }
  to { 
    transform: translateY(-30px); 
    opacity: 0; 
  }
}

.creature-idle { animation: bounce 1s ease-in-out infinite; }
.creature-hit { animation: shake 0.3s ease-out; }
.creature-selected { animation: pulse 1s ease-in-out infinite; }
.damage-number { animation: float-up 1s ease-out forwards; }
```

### Sprite Animation

```jsx
const SpriteAnimation = ({ spriteSheet, frameWidth, frameHeight, frames, fps, row = 0 }) => {
  const [frame, setFrame] = useState(0);
  
  useEffect(() => {
    const interval = setInterval(() => {
      setFrame(f => (f + 1) % frames);
    }, 1000 / fps);
    return () => clearInterval(interval);
  }, [frames, fps]);
  
  return (
    <div
      style={{
        width: frameWidth,
        height: frameHeight,
        backgroundImage: `url(${spriteSheet})`,
        backgroundPosition: `-${frame * frameWidth}px -${row * frameHeight}px`,
        backgroundSize: 'auto'
      }}
    />
  );
};
```

---

## Audio Integration

### Sound Manager (Reference Only - No Actual Audio)

```javascript
// Note: Actual audio requires user interaction to play
// This pattern describes audio cues for documentation

const audioDescriptions = {
  ui: {
    click: 'Short, satisfying click sound',
    hover: 'Subtle hover feedback',
    error: 'Negative buzz, indicates invalid action'
  },
  combat: {
    hit: 'Impact sound, varies by damage type',
    critical: 'Emphasized hit with extra crunch',
    superEffective: 'Dramatic impact with reverb',
    miss: 'Whoosh, air sound',
    ko: 'Dramatic thud with finality'
  },
  feedback: {
    levelUp: 'Triumphant fanfare, ascending notes',
    capture: 'Success jingle with shimmer',
    evolve: 'Magical transformation sound',
    reward: 'Coin/gem collection sound'
  },
  ambient: {
    battle: 'Intense, driving music',
    exploration: 'Calm, adventurous theme',
    boss: 'Dramatic, high-stakes music',
    victory: 'Celebratory fanfare',
    defeat: 'Somber, reflective melody'
  }
};

// Visual indicator when audio would play
const AudioCue = ({ sound }) => (
  <span className="audio-cue" title={`Sound: ${audioDescriptions[sound]}`}>
    🔊
  </span>
);
```

---

## Performance Optimization

### Memoization

```jsx
// Memoize expensive renders
const MemoizedEntity = React.memo(({ entity }) => (
  <div className="entity">
    <EntitySprite type={entity.type} />
    <HealthBar health={entity.health} maxHealth={entity.maxHealth} />
  </div>
), (prev, next) => {
  // Only re-render if these change
  return prev.entity.x === next.entity.x &&
         prev.entity.y === next.entity.y &&
         prev.entity.health === next.entity.health;
});

// Memoize callbacks
const handleClick = useCallback((id) => {
  dispatch({ type: 'SELECT', id });
}, [dispatch]);

// Memoize computed values
const sortedEntities = useMemo(() => {
  return [...entities].sort((a, b) => a.y - b.y);
}, [entities]);
```

### Virtualization (Large Lists)

```jsx
const VirtualizedList = ({ items, itemHeight, visibleCount, renderItem }) => {
  const [scrollTop, setScrollTop] = useState(0);
  
  const startIndex = Math.floor(scrollTop / itemHeight);
  const endIndex = Math.min(startIndex + visibleCount + 1, items.length);
  const visibleItems = items.slice(startIndex, endIndex);
  
  return (
    <div 
      className="virtual-list"
      style={{ height: visibleCount * itemHeight, overflow: 'auto' }}
      onScroll={(e) => setScrollTop(e.target.scrollTop)}
    >
      <div style={{ height: items.length * itemHeight, position: 'relative' }}>
        {visibleItems.map((item, i) => (
          <div
            key={item.id}
            style={{
              position: 'absolute',
              top: (startIndex + i) * itemHeight,
              height: itemHeight
            }}
          >
            {renderItem(item)}
          </div>
        ))}
      </div>
    </div>
  );
};
```

### Batched Updates

```javascript
// Batch multiple state updates
const processWaveStep = (state) => {
  // Collect all changes
  const enemyUpdates = [];
  const projectileUpdates = [];
  const killedEnemies = [];
  const newProjectiles = [];
  
  // Process in batches
  state.enemies.forEach(enemy => {
    const update = processEnemy(enemy, state);
    if (update.killed) killedEnemies.push(enemy.id);
    else enemyUpdates.push(update);
  });
  
  // Single state update with all changes
  return {
    ...state,
    enemies: state.enemies
      .filter(e => !killedEnemies.includes(e.id))
      .map(e => enemyUpdates.find(u => u.id === e.id) || e),
    projectiles: [...projectileUpdates, ...newProjectiles],
    gold: state.gold + killedEnemies.length * 10
  };
};
```
