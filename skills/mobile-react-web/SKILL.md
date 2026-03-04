---
name: mobile-react-web
description: Optimize React/Next.js web apps for mobile browsers (iOS Safari, Android Chrome). Use when working on responsive web apps, PWAs, or mobile web experiences. Covers technical implementation (viewport sizing, touch interactions, scrolling physics, keyboard handling, browser quirks) and design considerations (typography, spacing, color contrast, component sizing, layout adaptation, responsive patterns). For React Native/Expo apps, use the mobile-react-native-expo skill instead.
---

# Mobile React Web Optimization

Make web apps feel indistinguishable from native iOS/Android apps.

## Core Philosophy

Web apps on mobile browsers should feel indistinguishable from native apps. This requires handling both technical and design considerations:

**Technical Implementation:**
1. **Viewport** - Content fits the actual visible area, accounting for mobile browser chrome
2. **Touch** - Interactions respond to fingers, not mouse pointers
3. **Motion** - Scrolling and animations match platform physics

**Design & UX:**
4. **Readability** - Text is effortlessly readable at arm's length, even in bright light
5. **Spacing** - Touch targets and visual rhythm feel spacious, not cramped
6. **Adaptation** - Desktop patterns transform appropriately for mobile context

## Workflow

### 1. Technical Audit Mode
When reviewing existing code for technical issues, run through `references/checklist.md` systematically. Fix issues in priority order.

### 2. Design Audit Mode
When reviewing visual design, UX patterns, or overall mobile feel, run through `references/design-checklist.md`. Check typography, spacing, color contrast, component sizing, and layout adaptation.

### 3. Build Mode
When building new features, apply patterns from `references/patterns.md` proactively and design principles from `references/design-checklist.md`. Don't wait for mobile bugs.

### 4. Debug Mode
When fixing specific mobile issues, check `references/platform-quirks.md` for iOS/Android-specific technical causes, and cross-reference with design considerations.

## Quick Reference

### Design Essentials

**Typography:**
- Body text: **16-18px minimum** (never below 16px)
- Line height: **1.5-1.6** (more than desktop)
- Headings: Clear hierarchy (H1: 28-32px, H2: 24-28px, H3: 20-24px)
- System fonts: `-apple-system, system-ui` for native feel

**Touch-Friendly Spacing:**
- Touch targets: **44x44px minimum**
- Between targets: **8px minimum**
- Around content: **16-24px padding**
- Section separation: **24-32px vertical rhythm**

**Color & Contrast:**
- Text contrast: **4.5:1 minimum**, 7:1 preferred
- Test in bright outdoor light (mobile context)
- Interactive elements need color + another indicator (icon, underline)

**Component Sizing:**
- Buttons: **48-56px height** (comfortable thumb tap)
- Form inputs: **48-56px height**
- Cards: **16-20px padding** (more than desktop)

**Responsive Breakpoints:**
- Mobile: 0-640px (single column)
- Tablet: 641-1024px (optional 2-column)
- Desktop: 1025px+ (full multi-column)
- Design for **375px width** first (iPhone SE base)

### Viewport Essentials

```css
/* Always use dynamic viewport units */
height: 100dvh;  /* NOT 100vh - accounts for mobile browser chrome */
min-height: 100dvh;
min-height: -webkit-fill-available; /* iOS fallback */

/* Prevent input zoom on iOS (16px minimum) */
input, select, textarea {
  font-size: 16px;
}

/* Respect safe areas (notch, home indicator) */
padding: env(safe-area-inset-top) env(safe-area-inset-right) 
         env(safe-area-inset-bottom) env(safe-area-inset-left);
```

### Touch Essentials

```css
/* Minimum touch target: 44x44px */
.interactive {
  min-height: 44px;
  min-width: 44px;
}

/* Remove tap delay */
touch-action: manipulation;

/* Disable text selection on interactive elements */
-webkit-user-select: none;
user-select: none;

/* Remove iOS tap highlight */
-webkit-tap-highlight-color: transparent;
```

### Scroll Essentials

```css
/* Native momentum scrolling */
.scroll-container {
  overflow-y: auto;
  -webkit-overflow-scrolling: touch;
  overscroll-behavior: contain; /* Prevent scroll chaining */
}

/* Hide scrollbars on mobile (still scrollable) */
.scroll-container::-webkit-scrollbar {
  display: none;
}
```

### Keyboard Essentials

```tsx
// Track actual visible viewport (accounts for keyboard)
const [viewportHeight, setViewportHeight] = useState('100dvh');

useEffect(() => {
  const viewport = window.visualViewport;
  if (!viewport) return;
  
  const onResize = () => {
    setViewportHeight(`${viewport.height}px`);
  };
  
  viewport.addEventListener('resize', onResize);
  return () => viewport.removeEventListener('resize', onResize);
}, []);
```

## Common Patterns to Avoid

### Technical Patterns

| Desktop Pattern | Mobile Problem | Solution |
|-----------------|----------------|----------|
| `height: 100vh` | Overlaps mobile browser UI | Use `100dvh` |
| Hover states for info | No hover on touch | Use tap or long-press |
| Small click targets | Impossible to tap accurately | Minimum 44x44px |
| Fixed position modals | Keyboard pushes them offscreen | Use `visualViewport` |
| Horizontal scroll tables | Hidden content, no indication | Stack or card layout |
| CSS `:hover` effects | Sticky on mobile after tap | Use `@media (hover: hover)` |
| `position: fixed` footer | Jumps when keyboard opens | Use `position: sticky` or viewport API |

### Design Patterns

| Desktop Pattern | Mobile Problem | Solution |
|-----------------|----------------|----------|
| Small body text (14px) | Hard to read at arm's length | Use 16-18px minimum |
| Tight spacing (8-12px) | Feels cramped, hard to tap | Use 16-24px padding, 24-32px sections |
| Low-contrast grays | Invisible in bright sunlight | High contrast (4.5:1 min), test outdoors |
| Multi-column layouts | Hard to scan vertically | Single column, stack vertically |
| Sidebar navigation | Takes up precious space | Bottom tabs or hamburger drawer |
| Small buttons (32px) | Miss-taps, frustration | 48-56px height minimum |
| Hover tooltips | No way to access info | Show inline or use tap-to-reveal |
| Dense tables | Information overload | Card layout, show key info only |

## File References

**Technical Implementation:**
- **`references/checklist.md`** - Full technical audit checklist (viewport, touch, keyboard, scrolling)
- **`references/patterns.md`** - Copy-paste React/Next.js code patterns for each fix
- **`references/platform-quirks.md`** - iOS Safari vs Android Chrome specific technical issues

**Design & UX:**
- **`references/design-checklist.md`** - Comprehensive design audit (typography, spacing, color, component sizing, layout adaptation, responsive patterns)
