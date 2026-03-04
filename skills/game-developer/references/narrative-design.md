# Narrative Design Reference

## Table of Contents
1. [Story Structure](#story-structure)
2. [Dialogue Systems](#dialogue-systems)
3. [Character Arcs](#character-arcs)
4. [World Building](#world-building)
5. [Pacing & Beats](#pacing--beats)
6. [Player Agency](#player-agency)
7. [Environmental Storytelling](#environmental-storytelling)
8. [Writing for Games](#writing-for-games)

---

## Story Structure

### The Three-Act Structure (Adapted for Games)

```
ACT 1: SETUP (10-20% of game)
├── Hook: Immediate engagement
├── Inciting Incident: Call to adventure
└── First Threshold: Point of no return

ACT 2: CONFRONTATION (60-70% of game)
├── Rising Action: Escalating challenges
├── Midpoint: Major revelation/shift
├── Complications: Things get worse
└── Dark Night: Lowest point

ACT 3: RESOLUTION (15-25% of game)
├── Climax: Final confrontation
├── Falling Action: Consequences unfold
└── Resolution: New equilibrium
```

### Game-Specific Structure: The Hero's Journey (Condensed)

```javascript
const heroJourneyBeats = [
  { name: 'Ordinary World', gameplay: 'Tutorial, home area' },
  { name: 'Call to Adventure', gameplay: 'Main quest given' },
  { name: 'Meeting the Mentor', gameplay: 'Learn core mechanics' },
  { name: 'Crossing Threshold', gameplay: 'Leave starting zone' },
  { name: 'Tests & Allies', gameplay: 'Main gameplay loop' },
  { name: 'Approach', gameplay: 'Pre-final area' },
  { name: 'Ordeal', gameplay: 'Major boss/challenge' },
  { name: 'Reward', gameplay: 'Key item/power/knowledge' },
  { name: 'Road Back', gameplay: 'Return journey with stakes' },
  { name: 'Resurrection', gameplay: 'Final boss' },
  { name: 'Return', gameplay: 'Ending, epilogue' }
];
```

### Story Hooks by Genre

| Genre | Effective Hooks |
|-------|----------------|
| Tower Defense | "The kingdom is falling. You're the last defense." |
| RTS | "Your faction's survival depends on this campaign." |
| RPG | "You wake with no memory, but everyone knows your name." |
| Pokemon-like | "Today you begin your journey to become a master." |

---

## Dialogue Systems

### Dialogue Tree Structure

```javascript
const dialogueNode = {
  id: 'node_001',
  speaker: 'Elder Oak',
  portrait: 'oak_neutral',
  text: 'The creatures of this land need a champion. Will you answer the call?',
  choices: [
    { 
      text: 'I will protect them.',
      next: 'node_002',
      effects: [{ type: 'reputation', faction: 'guardians', value: 5 }]
    },
    { 
      text: 'What\'s in it for me?',
      next: 'node_003',
      effects: [{ type: 'trait', add: 'pragmatic' }]
    },
    { 
      text: '[Leave]',
      next: null,
      conditions: [{ type: 'flag', key: 'canLeave', value: true }]
    }
  ]
};
```

### Dialogue Display Patterns

**Typewriter Effect:**
```javascript
const typewriterText = (text, element, speed = 30) => {
  let i = 0;
  const interval = setInterval(() => {
    element.textContent += text[i];
    i++;
    if (i >= text.length) clearInterval(interval);
  }, speed);
  return interval;
};
```

**Portrait + Text Box (Classic RPG):**
```jsx
const DialogueBox = ({ node, onChoice }) => (
  <div className="dialogue-container">
    <div className="portrait">
      <img src={`/portraits/${node.portrait}.png`} alt={node.speaker} />
      <span className="speaker-name">{node.speaker}</span>
    </div>
    <div className="text-box">
      <p>{node.text}</p>
      {node.choices && (
        <div className="choices">
          {node.choices.map((choice, i) => (
            <button key={i} onClick={() => onChoice(choice)}>
              {choice.text}
            </button>
          ))}
        </div>
      )}
    </div>
  </div>
);
```

### Barks (Short Contextual Lines)

```javascript
const barkSystem = {
  combat: {
    lowHealth: ['I can\'t take much more!', 'Need healing!'],
    victory: ['That\'s how it\'s done!', 'Too easy.'],
    defeat: ['No... not like this...', 'I\'ve failed...'],
    superEffective: ['Direct hit!', 'Got \'em!']
  },
  exploration: {
    discovery: ['What\'s this?', 'Interesting...'],
    danger: ['Watch out!', 'Something\'s not right.'],
    treasure: ['Jackpot!', 'This could be useful.']
  },
  idle: {
    waiting: ['...', '*yawn*', 'What now?']
  }
};

const getRandomBark = (category, situation) => {
  const options = barkSystem[category][situation];
  return options[Math.floor(Math.random() * options.length)];
};
```

---

## Character Arcs

### Arc Types

**Positive Change Arc:**
```
Belief (false) → Challenge → Growth → New Belief (true)
Example: "I'm not strong enough" → Trials → "Strength comes from my bonds"
```

**Flat Arc (Hero inspires change in world):**
```
Hero holds truth → World challenges it → Hero proves truth → World changes
Example: "All creatures deserve protection" → Corruption → Victory → Peace restored
```

**Negative Arc:**
```
Belief (true) → Corruption → Fall → Belief (false/twisted)
Example: Rival who starts noble, becomes obsessed with power
```

### Character Template

```javascript
const characterTemplate = {
  name: 'Rival Character',
  role: 'rival', // protagonist, mentor, rival, ally, villain
  
  // External
  appearance: 'Tall, silver hair, always wears a red scarf',
  speech: 'Confident, uses formal language, rarely shows weakness',
  
  // Internal
  want: 'To be recognized as the strongest trainer',
  need: 'To accept that relationships matter more than strength',
  flaw: 'Pride that isolates them',
  
  // Arc
  arc: {
    start: 'Dismissive of player, focused only on winning',
    midpoint: 'Loses to player, begins questioning methods',
    end: 'Accepts player as equal, values friendship'
  },
  
  // Relationship
  relationshipToPlayer: {
    start: 'Dismissive rival',
    end: 'Respected friend'
  }
};
```

---

## World Building

### Rule of Three for Factions

Every world benefits from 3 distinct factions:
1. **The Establishment** (order, tradition, rigidity)
2. **The Rebels** (change, freedom, chaos)
3. **The Outsiders** (mystery, neutrality, hidden agendas)

```javascript
const factionTemplate = {
  name: 'The Wardens',
  philosophy: 'Protect all creatures, maintain balance',
  aesthetic: 'Green and gold, nature motifs, flowing designs',
  strength: 'Healing, defense, creature bonds',
  weakness: 'Slow to act, overly cautious',
  leader: 'Elder Oak',
  headquarters: 'The Verdant Sanctum',
  relationToPlayer: 'Mentors, quest givers',
  conflict: 'Struggling against industrial expansion'
};
```

### Location Design

**Hub Areas:**
```javascript
const hubDesign = {
  functions: ['Rest/heal', 'Shop', 'Story progression', 'Side quests'],
  npcs: [
    { role: 'healer', purpose: 'Restore party' },
    { role: 'merchant', purpose: 'Economy sink/upgrade' },
    { role: 'questGiver', purpose: 'Drive engagement' },
    { role: 'lore', purpose: 'World building' },
    { role: 'humor', purpose: 'Tone balance' }
  ],
  atmosphere: 'Safe, welcoming, contrast to danger zones'
};
```

**Dungeon/Challenge Areas:**
```javascript
const dungeonNarrative = {
  entrance: 'Environmental foreshadowing of theme',
  middle: 'Escalating reveals, lore fragments',
  boss: 'Theme culmination, character moment',
  reward: 'Narrative payoff + mechanical reward'
};
```

---

## Pacing & Beats

### Tension Curve

```
Tension
  │
  │         ╱╲    ╱╲   ╱\  CLIMAX
  │       ╱    ╲╱    ╲╱    \
  │     ╱                    \
  │   ╱  Rising action        \ Resolution
  │ ╱                           \
  └─────────────────────────────────── Time
    ↑     ↑       ↑       ↑      ↑
  Hook  Test1   Test2  Dark    End
                       Night
```

### Beat Spacing

```javascript
const beatSpacing = {
  majorStoryBeat: '45-60 minutes apart',
  minorProgression: '15-20 minutes apart',
  characterMoment: '10-15 minutes apart',
  barkOrFlavor: '2-5 minutes (ambient)',
  
  // Tower Defense specific
  waveNarrative: 'Every 5 waves: mini story beat',
  bossWave: 'Major narrative moment',
  
  // RPG specific
  townVisit: 'Story + downtime + setup',
  dungeonComplete: 'Resolution + reward + tease next'
};
```

### Show Don't Tell

```javascript
// Instead of:
const tellExample = "The village was destroyed by the dark army.";

// Show:
const showExample = {
  visualCues: ['Burned buildings', 'Scorched earth patterns', 'Weapon debris'],
  npcDialogue: ['survivor': 'They came at dawn... we had no warning.'],
  itemDiscovery: ['Charred toy', 'Half-written letter'],
  environmentalAudio: ['Distant crying', 'Crackling embers']
};
```

---

## Player Agency

### Choice Types

**Cosmetic Choices:**
```javascript
// No gameplay impact, but feel meaningful
const cosmeticChoice = {
  prompt: 'What will you name your first creature?',
  impact: 'Personal investment, no mechanical difference'
};
```

**Tactical Choices:**
```javascript
// Affects immediate gameplay
const tacticalChoice = {
  prompt: 'Attack the left flank or defend the bridge?',
  outcomes: {
    leftFlank: { immediate: 'Faster victory', cost: 'More casualties' },
    bridge: { immediate: 'Slower but safe', cost: 'Enemy escapes' }
  }
};
```

**Moral Choices:**
```javascript
// Affects story/relationships
const moralChoice = {
  prompt: 'The poacher offers you a rare creature. Accept?',
  outcomes: {
    accept: { 
      gain: 'Rare creature', 
      cost: 'Warden reputation -20',
      storyFlag: 'dealWithPoacher'
    },
    refuse: { 
      gain: 'Warden reputation +10', 
      cost: 'No creature',
      storyFlag: 'refusedPoacher'
    }
  }
};
```

### Meaningful Consequences

```javascript
const consequenceSystem = {
  // Immediate feedback
  immediate: 'NPC reaction, visual change, sound cue',
  
  // Short-term
  shortTerm: 'Dialogue changes, NPC availability, prices',
  
  // Long-term
  longTerm: 'Story branches, ending variations, unlocks',
  
  // Example
  example: {
    choice: 'Save the village OR chase the villain',
    immediate: {
      saveVillage: 'Villagers cheer',
      chaseVillain: 'Villain escapes, village burns (seen later)'
    },
    shortTerm: {
      saveVillage: 'Villagers give supplies, villain stronger next encounter',
      chaseVillain: 'Villain captured, but survivors hate you'
    },
    longTerm: {
      saveVillage: 'Village becomes ally hub, alternate final boss',
      chaseVillain: 'Ruined village haunts you, different ending'
    }
  }
};
```

---

## Environmental Storytelling

### Visual Narrative Elements

```javascript
const environmentalStoryElements = {
  // Pre-battle
  battlefield: [
    'Old fortifications (previous defense attempt)',
    'Crater patterns (bombing runs)',
    'Monument to fallen (emotional weight)'
  ],
  
  // Creature areas
  habitat: [
    'Nests show family structure',
    'Territorial markings (creature culture)',
    'Food chains visible (ecosystem)'
  ],
  
  // Abandoned places
  ruins: [
    'What happened here? (mystery)',
    'Signs of hasty evacuation',
    'One item out of place (clue)'
  ]
};
```

### Item Descriptions as Lore

```javascript
const loreItems = {
  'Faded Photograph': {
    description: 'A water-damaged photo of three trainers. One face is scratched out.',
    loreHint: 'Former friendship turned to rivalry'
  },
  'Ancient Pokéball': {
    description: 'A primitive capture device. The mechanisms are completely different from modern designs.',
    loreHint: 'Lost technology, different era'
  },
  'Commander\'s Badge': {
    description: 'Awarded for valor in the Great War. The metal is warped by intense heat.',
    loreHint: 'War history, fire-based conflict'
  }
};
```

---

## Writing for Games

### Concision Rules

```javascript
const writingGuidelines = {
  // Dialogue
  maxLineLength: '2 sentences per text box',
  readingTime: '3-5 seconds per box',
  
  // UI text
  buttonLabels: '1-3 words',
  tooltips: '1 sentence',
  tutorials: 'Show > Tell (use visual demos)',
  
  // Descriptions
  items: '1-2 sentences',
  abilities: '1 sentence effect + 1 sentence flavor',
  locations: '1 atmospheric line + mechanics info'
};
```

### Voice Consistency

```javascript
const voiceProfiles = {
  // Game tone
  serious: {
    vocabulary: 'Formal, specific, weighted',
    humor: 'Rare, dry, character-based',
    example: 'The creature regards you with ancient eyes. It has seen empires rise and fall.'
  },
  
  lighthearted: {
    vocabulary: 'Casual, playful, accessible',
    humor: 'Frequent, puns acceptable, self-aware',
    example: 'The little guy looks at you like you just stepped on its lunch. Which... you might have.'
  },
  
  // Character voices
  mentor: 'Wise, patient, occasionally cryptic',
  rival: 'Competitive, sharp, secretly respectful',
  villain: 'Intelligent, motivated, believes they\'re right'
};
```

### The "So What" Test

Every piece of story content should answer: "Why does the player care?"

```javascript
const soWhatTest = (content) => {
  const validReasons = [
    'Advances player goal',
    'Reveals useful information',
    'Develops character player cares about',
    'Creates emotional response',
    'Adds context to mechanics',
    'Sets up future payoff'
  ];
  
  // If content doesn't serve at least one, cut it
  return validReasons.some(reason => content.serves(reason));
};
```
