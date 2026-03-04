---
name: Web Color Design
description: Guides color scheme selection for websites and apps. Use when choosing themes, palettes, brand colors, or designing UI color systems. Covers color psychology, accessibility, industry conventions, and practical palette creation.
---

# Web Color Design Skill

Help users select effective color schemes for websites and applications by applying color theory, psychology, accessibility standards, and industry best practices.

## When to Use This Skill

- User asks about color schemes, palettes, or themes for a website/app
- Creating landing pages, dashboards, or UI components
- Choosing brand colors or redesigning existing color systems
- Ensuring color accessibility compliance

## Core Principles

### The 60-30-10 Rule
Structure your palette with intentional proportions:
- **60% Dominant**: Background/base color (usually neutral or soft)
- **30% Secondary**: Supporting elements, cards, sections
- **10% Accent**: CTAs, highlights, interactive elements

### The 3-Color Foundation
Start with three colors, expand only when necessary:
1. **Primary**: Brand identity, headers, key elements
2. **Secondary**: Supporting UI, less prominent sections
3. **Accent**: Actions, alerts, emphasis

## Color Psychology Quick Reference

| Color | Conveys | Best For |
|-------|---------|----------|
| **Blue** | Trust, stability, calm | Finance, healthcare, tech, B2B |
| **Green** | Growth, health, nature | Eco, wellness, finance (positive) |
| **Red** | Energy, urgency, passion | Food, sales, entertainment |
| **Orange** | Friendly, confident, creative | Youth brands, CTAs, e-commerce |
| **Yellow** | Optimism, warmth, attention | Caution, highlights, children |
| **Purple** | Luxury, creativity, wisdom | Beauty, premium, education |
| **Black** | Sophistication, power | Luxury, fashion, tech |
| **White** | Clean, minimal, space | Modern, healthcare, tech |

## Palette Types by App Category

### SaaS / B2B Dashboards
- Neutral base (white/light gray or dark mode)
- Single strong accent for actions
- Semantic colors for status (green/yellow/red)
- Example: Slate gray + Blue accent + White backgrounds

### E-commerce
- High contrast for CTAs
- Warm accents drive action (orange, red)
- Clean product backgrounds
- Example: White base + Black text + Orange CTAs

### Creative / Portfolio
- Bold, distinctive palettes welcome
- Can break conventional rules
- Express personality through color
- Example: Deep purple + Coral + Cream

### Finance / Healthcare
- Conservative, trustworthy palettes
- Blues and greens dominate
- Avoid aggressive colors
- Example: Navy + Teal accents + Light backgrounds

### Consumer Apps
- Vibrant, engaging colors
- Strong brand recognition
- Consistent across touchpoints
- Example: Spotify green, Instagram gradient

## Accessibility Requirements (WCAG)

### Contrast Ratios (Minimum)
- **Normal text**: 4.5:1 against background
- **Large text** (18px+ or 14px bold): 3:1
- **UI components/graphics**: 3:1

### Common Pitfalls
- Light gray text on white (fails contrast)
- Colored text on colored backgrounds
- Relying solely on color to convey meaning
- Pure black (#000) on pure white (#FFF) can cause eye strain—soften slightly

### Testing Tools
- WebAIM Contrast Checker
- Chrome DevTools accessibility audit
- Stark plugin for Figma/Sketch

## Practical Workflow

### Step 1: Define Purpose
What emotion/action should the site evoke? (Trust? Excitement? Calm?)

### Step 2: Research Industry
Look at competitors and industry leaders. Note patterns, but find differentiation.

### Step 3: Start with One Color
Pick your primary based on brand/purpose. Build from there.

### Step 4: Generate Palette
Use tools to create harmonious combinations:
- **Analogous**: Adjacent colors (harmonious, low contrast)
- **Complementary**: Opposite colors (high contrast, vibrant)
- **Triadic**: Three equidistant colors (balanced, dynamic)
- **Split-complementary**: One color + two adjacent to its complement

### Step 5: Test in Context
Apply to actual UI components. Check:
- Text readability
- Button visibility
- Visual hierarchy
- Dark mode compatibility

### Step 6: Document
Create a color system with:
- Hex/RGB values
- CSS variables or design tokens
- Usage guidelines

## Palette Generation Tools

| Tool | Best For | URL |
|------|----------|-----|
| **Coolors** | Quick generation, export | coolors.co |
| **Color Hunt** | Curated trending palettes | colorhunt.co |
| **Adobe Color** | Advanced color theory tools | color.adobe.com |
| **Realtime Colors** | Live preview on UI | realtimecolors.com |
| **Paletton** | Classic color wheel | paletton.com |
| **Colormind** | AI-generated palettes | colormind.io |

## Implementation Tips

### CSS Variables Structure
```css
:root {
  /* Base */
  --color-bg: #ffffff;
  --color-surface: #f8fafc;
  --color-text: #1e293b;
  --color-text-muted: #64748b;
  
  /* Brand */
  --color-primary: #3b82f6;
  --color-primary-hover: #2563eb;
  --color-secondary: #8b5cf6;
  
  /* Semantic */
  --color-success: #22c55e;
  --color-warning: #f59e0b;
  --color-error: #ef4444;
  
  /* Accent */
  --color-accent: #f97316;
}
```

### Dark Mode Considerations
- Don't just invert colors
- Reduce saturation slightly for dark backgrounds
- Ensure accent colors still pop
- Test extensively—dark mode reveals contrast issues

## Reference Files

For curated palette examples and detailed accessibility guidelines, see:
- `references/color-palettes.md` - Industry-specific palette collections
- `references/accessibility-guide.md` - Detailed WCAG compliance guide
