---
name: superdesign
description: Library of 100 premium React/Tailwind UI components plus design philosophy for creating distinctive, production-grade frontend interfaces. Use when the user requests fancy animations, interactive backgrounds, landing page sections, buttons with effects, text animations, scroll effects, pricing tables, navigation components, image galleries, or any visually impressive UI elements. Also use when styling/beautifying any web UI or wanting to avoid generic AI aesthetics. Triggers include "cool button", "animated background", "landing page hero", "gooey effect", "glassmorphism", "gradient animation", "scroll animation", "text reveal", "pricing section", "make it look amazing", "more premium", or building websites/dashboards/React components.
---

# Superdesign: Components + Design Philosophy

A curated collection of 100 production-ready React components with Tailwind CSS styling, PLUS design principles for creating distinctive interfaces that avoid generic "AI slop" aesthetics.

---

## Design Philosophy: Avoiding AI Slop

Before using any component, commit to a **BOLD aesthetic direction**. Generic output happens when design decisions are deferred.

### Design Thinking Process

1. **Purpose**: What problem does this interface solve? Who uses it?
2. **Tone**: Pick a direction - brutally minimal, maximalist chaos, retro-futuristic, organic/natural, luxury/refined, playful/toy-like, editorial/magazine, brutalist/raw, art deco/geometric, soft/pastel, industrial/utilitarian
3. **Constraints**: Technical requirements (framework, performance, accessibility)
4. **Differentiation**: What makes this UNFORGETTABLE? What's the one thing someone will remember?

### Anti-AI-Slop Rules

**NEVER use these generic patterns:**
- Overused fonts: Inter, Roboto, Arial, system fonts, Space Grotesk (across multiple projects)
- Cliched colors: Purple gradients on white backgrounds
- Predictable layouts: Everything centered, uniform spacing, cookie-cutter components
- Safe choices: Default shadows, standard border-radius, boring hover states

**ALWAYS pursue:**
- **Typography**: Distinctive display fonts paired with refined body fonts. Unexpected, characterful choices.
- **Color**: Cohesive palettes with dominant colors and sharp accents. Bold > timid.
- **Motion**: High-impact moments - one well-orchestrated page load with staggered reveals beats scattered micro-interactions. Scroll-triggering and hover states that surprise.
- **Spatial Composition**: Asymmetry. Overlap. Diagonal flow. Grid-breaking elements. Generous negative space OR controlled density.
- **Atmosphere**: Gradient meshes, noise textures, geometric patterns, layered transparencies, dramatic shadows, decorative borders, grain overlays.

### Execution Principle

Match implementation complexity to aesthetic vision:
- **Maximalist designs** need elaborate code with extensive animations and effects
- **Minimalist designs** need restraint, precision, and careful attention to spacing/typography/subtle details

Elegance comes from executing the vision well, not from choosing a "safe" middle ground.

---

## Component Library

> **CORE PRINCIPLE**: Style components are complete visual languages. DO NOT interpret them loosely or add your own interpretation. MATCH THEM EXACTLY - fonts, colors, shadows, layouts, and characteristic elements. Generic output means you didn't follow the reference closely enough.

## CRITICAL: Retrieval Process

The component library file is **1.7MB** and cannot be read directly. You MUST use the extraction script to get complete component code.

### Step 1: Browse Components

Use Node.js to search the compact index (works on Windows/Mac/Linux):

```bash
# Search by keyword (case-insensitive)
node -e "
const path = require('path');
const home = process.env.HOME || process.env.USERPROFILE;
const skillDir = process.platform === 'win32'
  ? path.join(process.env.APPDATA, 'Claude/skills/superdesign')
  : path.join(home, 'Library/Application Support/Claude/skills/superdesign');
const data = require(path.join(skillDir, 'references/component-index.json'));
const results = data.filter(c => c.title.toLowerCase().includes('brutalist'));
results.forEach(c => console.log(c.id, '-', c.title, '| Tags:', c.tags.join(', ')));
"

# Filter by tag
node -e "
const path = require('path');
const home = process.env.HOME || process.env.USERPROFILE;
const skillDir = process.platform === 'win32'
  ? path.join(process.env.APPDATA, 'Claude/skills/superdesign')
  : path.join(home, 'Library/Application Support/Claude/skills/superdesign');
const data = require(path.join(skillDir, 'references/component-index.json'));
const results = data.filter(c => c.tags.includes('style'));
results.forEach(c => console.log(c.id, '-', c.title));
"

# List all available tags with counts
node -e "
const path = require('path');
const home = process.env.HOME || process.env.USERPROFILE;
const skillDir = process.platform === 'win32'
  ? path.join(process.env.APPDATA, 'Claude/skills/superdesign')
  : path.join(home, 'Library/Application Support/Claude/skills/superdesign');
const data = require(path.join(skillDir, 'references/component-index.json'));
const tags = {};
data.forEach(c => c.tags.forEach(t => tags[t] = (tags[t] || 0) + 1));
Object.entries(tags).sort((a,b) => b[1]-a[1]).forEach(([t,n]) => console.log(t + ': ' + n));
"
```

### Step 2: Extract Full Component Code

**USE THIS SCRIPT** - it's the only reliable way to get complete code:

```bash
node -e "
const fs = require('fs');
const path = require('path');
const home = process.env.HOME || process.env.USERPROFILE;
const skillDir = process.platform === 'win32'
  ? path.join(process.env.APPDATA, 'Claude/skills/superdesign')
  : path.join(home, 'Library/Application Support/Claude/skills/superdesign');
const libPath = path.join(skillDir, 'references/component-library.json');
const data = JSON.parse(fs.readFileSync(libPath, 'utf8'));
const component = data.prompts.find(c => c.id === 'COMPONENT_ID_HERE');
if (component) {
  console.log('=== COMPONENT: ' + component.title + ' ===');
  console.log('');
  console.log(component.prompt);
} else {
  console.log('Component not found');
}
"
```

Replace `COMPONENT_ID_HERE` with the actual ID from the index.

### Step 3: Verify Complete Retrieval

Before proceeding, verify you have:
- [ ] Complete `<style>` block with font imports (@import url statements)
- [ ] All CSS keyframes and animations (check for @keyframes blocks)
- [ ] Complete component function(s) (should end with proper closing braces)
- [ ] All helper components (CustomCursor, NoiseOverlay, etc. for style components)
- [ ] Export statement at the end

**RED FLAGS that indicate truncation:**
- Code ending mid-line or mid-function
- Missing closing braces `}` or parentheses `)`
- `[Omitted...]` messages in output
- Export statement missing

### Step 4: If Extraction Fails

If the Node.js script output is truncated or incomplete:

1. **Ask the user directly:**
   > "The component code is too large and got truncated. Could you please:
   > 1. Go to the preview URL: [previewUrl from index]
   > 2. Copy the full component code
   > 3. Paste it here so I can implement it accurately"

2. **Use the Style DNA approach as fallback:**
   - Even with partial code, extract what you CAN see (fonts, colors, CSS variables)
   - Fill out the Style DNA template
   - Ask the user to verify specific values you're uncertain about

3. **Never guess or interpret loosely** - if you can't see the exact code, ask for it.

---

## Component Categories & Fidelity Levels

### HIGH-FIDELITY: Style Components (tag: "style")

**These define complete visual languages. Match them EXACTLY.**

Style components include: Neo-Brutalism, Dark Avant-Garde, Cyber Serif, Organic Modern, etc.

When adapting a style component, you MUST preserve:

| Element | Why It Matters | What to Extract |
|---------|---------------|-----------------|
| **Display Font** | Defines the entire personality | Font family name, Google Fonts import URL |
| **Body Font** | Affects readability and tone | Font family, weight range |
| **Color System** | Creates visual coherence | CSS variables (--ink, --paper, --accent, etc.) |
| **Shadow Pattern** | Signature brutalist/modern look | Exact px values, no blur vs blur |
| **Border Weight** | Defines visual weight | 2px, 3px, 4px - be exact |
| **Characteristic Elements** | What makes it unique | Marquees, tilts, cursors, noise overlays |
| **Hover States** | Interaction feel | Transform + shadow changes |
| **Layout Patterns** | Structural DNA | Bento grids, asymmetric layouts |

#### Style DNA Extraction Template

Before implementing a style component, fill out this checklist:

```markdown
## Style DNA: [Component Name]

### Typography
- Display Font: ____________________
- Body Font: ____________________
- Font Import URL: ____________________

### Colors (CSS Variables)
- Primary/Ink: ____________________
- Background/Paper: ____________________
- Accent: ____________________
- Additional: ____________________

### Shadows
- Small: ____________________
- Default: ____________________
- Large: ____________________
- Blur: Yes / No

### Borders
- Default weight: ____________________
- Border color: ____________________

### Characteristic Elements
- [ ] Marquee/ticker
- [ ] Custom cursor
- [ ] Noise overlay
- [ ] Tilted elements (rotation)
- [ ] Floating decorations
- [ ] Glitch effects
- [ ] Other: ____________________

### Hover Patterns
- Buttons: ____________________
- Cards: ____________________
- Links: ____________________

### Layout Signature
- Grid pattern: ____________________
- Spacing scale: ____________________
- Border radius: ____________________
```

### MEDIUM-FIDELITY: UI Components (tags: "ui component", "button", "nav", "pricing")

Can be adapted to match existing design systems, but preserve:
- Core interaction patterns
- Animation timing and easing
- Accessibility features

### LOW-FIDELITY: Animation Components (tags: "animation", "background")

The animation itself is the product. Preserve:
- Animation logic and keyframes
- Performance optimizations
- But container/wrapper can be freely adapted

---

## Integration Workflow

### For Style Components

1. **Extract Style DNA** - Fill out the template above
2. **Set Up Foundation** - Add fonts, CSS variables, and base utilities to globals.css
3. **Build Section by Section** - Match each section's structure
4. **Verify Fidelity** - Compare your output to the preview URL
5. **Adapt Content Only** - Change text, images, links - NOT visual patterns

### For UI/Animation Components

1. **Extract Core Logic** - Identify the key interaction/animation
2. **Check Dependencies** - framer-motion, GSAP, etc.
3. **Adapt Wrapper** - Container can match your design system
4. **Preserve Animation DNA** - Keep timing, easing, and keyframes

---

## Common Mistakes to Avoid

| Mistake | Why It Happens | How to Avoid |
|---------|---------------|--------------|
| Generic output despite using reference | Interpreted concepts instead of copying patterns | Extract Style DNA first, match exactly |
| Missing display font | Font import in `<style>` block was missed | Always check for @import statements |
| Soft shadows instead of hard | Assumed "shadow" means typical box-shadow | Check exact shadow values - brutalist = no blur |
| Lost characteristic elements | Thought marquees/cursors were optional flourishes | They ARE the style - keep them |
| Wrong hover states | Used default hover patterns | Copy exact transform + shadow changes |

---

## Quick Reference: Available Tags

| Category | Tags |
|----------|------|
| **Effects** | animation (51), scroll animation (10), text animation (10), parallax (1), morph (1) |
| **UI Elements** | ui component (32), button (3), nav (6), pricing (7), image gallery (2), footer (1) |
| **Pages/Sections** | landing page (25), page (10), hero (1), testimonials (1), features (1) |
| **Visual Styles** | background (22), style (15), gradient (1), glassmorphism (1), retro (1), bento (1) |

---

## Example: Neo-Brutalism Style DNA

For reference, here's the extracted DNA from the Neo-Brutalism component:

```markdown
## Style DNA: Neo-Brutalism / Acid Brutalism

### Typography
- Display Font: Dela Gothic One
- Body Font: Space Grotesk (300-700)
- Font Import: https://fonts.googleapis.com/css2?family=Dela+Gothic+One&family=Space+Grotesk:wght@300;400;500;600;700&display=swap

### Colors (CSS Variables)
- --ink: #0A2A1F (dark green-black)
- --paper: #F8F4E8 (warm cream)
- --acid: #D2E823 (electric lime)

### Shadows
- Small: 2px 2px 0px 0px var(--ink)
- Default: 4px 4px 0px 0px var(--ink)
- Large: 8px 8px 0px 0px var(--ink)
- Blur: NO (hard edges only)

### Borders
- Default weight: 2px solid
- Border color: var(--ink)

### Characteristic Elements
- [x] Marquee/ticker (top + tilted middle)
- [x] Custom cursor (mix-blend-difference)
- [x] Noise overlay (SVG turbulence)
- [x] Tilted elements (-rotate-1, rotate-3, etc.)
- [x] Floating decorations (animate-float)
- [x] Glitch effects (on hover)
- [x] Bento grid layout

### Hover Patterns
- Buttons: translate(2-4px, 2-4px) + reduce shadow
- Cards: translate(4px, 4px) + remove shadow
- Links: color change + underline decoration

### Layout Signature
- Grid: 12-column with bento variations
- Spacing: Generous (py-24, gap-8, etc.)
- Border radius: rounded-xl to rounded-3xl
```

---

## Quick Reference: Popular Style Component IDs

For faster retrieval, here are the IDs for commonly requested style components:

| Style | ID |
|-------|-----|
| **Neo-Brutalism** | `e6417c0d-e870-4e05-9780-e1a208d8ef6f` |
| **Dark Avant-Garde** | `9adec2ac-6685-4287-8958-63ee8da0db75` |
| **Cyber Serif** | `c0a68739-bfa4-418c-9646-eab9b38d002b` |
| **Organic Modern** | `6efb1a53-3068-4bdd-a512-c6e46ffc959f` |
| **Red Noir** | `20410f94-56bd-401e-86e4-a6cb239d5e3a` |
| **Warm Industrial Gray** | `1b5a0ee2-e8d3-4293-b92a-5bccbd9e84dc` |
| **Bold Retro-Modernism** | `5227bf60-127b-4498-8f44-6bee1cd92dd2` |
| **Tech Editorial** | `43ba6221-1a31-440e-914c-ceecd126ef3d` |
| **Glassmorphism** | `0a3885c4-eb47-4a33-9d4c-abadea200e03` |
| **Architectural Blueprint** | `ad87802f-8942-4860-815b-62cedbcc197d` |

Run the search script to find IDs for other styles.

---

## Resources

### references/
- `component-library.json` - Full library (1.7MB) - use extraction script
- `component-index.json` - Compact browsing index

### Preview URLs
Each component has a `previewUrl` field - USE IT to verify your implementation matches the reference visually.

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Node.js script returns nothing | Check the component ID is correct; use quotes around UUID |
| Output appears truncated | Ask user to paste full code directly |
| Can't find component by name | Try different search terms; check available tags |
| Implemented but looks generic | You didn't match the Style DNA - review fonts, shadows, colors |
| Missing animations | Check for @keyframes in the `<style>` block and animate-* classes |
