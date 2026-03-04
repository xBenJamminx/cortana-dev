# Mobile Design Checklist

Run through this checklist when reviewing or creating mobile designs. Use alongside the technical checklist for comprehensive mobile optimization.

## Priority 1: Readability & Accessibility

These ensure the app is usable and accessible on mobile devices.

### Typography

- [ ] Body text is **16-18px minimum** (never below 16px)
- [ ] Line height is **1.5-1.6** for body text (more than desktop's 1.4)
- [ ] Paragraph line length is **45-75 characters** (narrower than desktop)
- [ ] Font weight is **sufficient for small screens** (400+ for body, 600+ for headings)
- [ ] Headings have clear hierarchy with **enough size difference** (H1: 28-32px, H2: 24-28px, H3: 20-24px)
- [ ] Letter spacing is slightly increased for small text (<14px should have +0.01-0.02em)
- [ ] System font stack used for native feel (`-apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui`)

**Quick test:** Hold device at arm's length. Can you still read body text comfortably?

### Color & Contrast

- [ ] Text contrast ratio is **4.5:1 minimum** (WCAG AA), **7:1 preferred** (WCAG AAA)
- [ ] Colors work in **bright outdoor light** (high contrast, avoid low-contrast grays)
- [ ] Interactive elements have **color + another indicator** (icon, underline, shape)
- [ ] Color alone never conveys information (form errors, status indicators)
- [ ] Dark text on light backgrounds preferred over light text on dark (easier to read in sunlight)
- [ ] Brand colors adjusted if necessary for mobile contrast requirements

**Quick test:** View in bright sunlight or simulated daylight. Can you distinguish all elements?

### Touch-Friendly Spacing

- [ ] Touch targets are **44x44px minimum** (Apple HIG, covered in technical checklist)
- [ ] **8px minimum spacing** between adjacent interactive elements
- [ ] **16px minimum padding** around touch targets (internal space)
- [ ] **24-32px vertical rhythm** between content sections (feels spacious on small screens)
- [ ] Form fields have **12-16px padding** (comfortable for thumb typing)
- [ ] Bottom navigation/actions have **extra padding** (80-100px from bottom on iPhone X+ for home indicator)

**Visual rhythm principle:** Mobile needs MORE spacing than desktop, not less, because elements are physically closer to your eyes.

## Priority 2: Component Adaptation

These ensure desktop patterns translate well to mobile.

### Buttons & Interactive Elements

- [ ] Primary button is **prominent** (48-56px height, full-width or nearly full-width)
- [ ] Secondary buttons are **clearly different** from primary (outline, ghost, or subtle fill)
- [ ] Destructive actions require **confirmation** (easier to tap accidentally)
- [ ] Icon buttons have **text labels or clear tooltips** (icons ambiguous without mouse hover)
- [ ] Button text is **concise** ("Save" not "Save Changes", "Delete" not "Delete This Item")
- [ ] Loading states are **clear** (spinner + disabled state, not just spinner)

### Forms & Inputs

- [ ] Input fields are **tall enough** (48-56px height for comfortable tapping)
- [ ] Labels are **above inputs**, never beside (easier to scan vertically)
- [ ] Placeholder text is **light** and never replaces labels
- [ ] Validation errors appear **immediately below** the field, not at top of form
- [ ] Multi-step forms show **progress clearly** (step indicator at top)
- [ ] Auto-focus doesn't trigger on page load (iOS keyboard pops up annoyingly)
- [ ] Autocomplete attributes set correctly (`autocomplete="email"`, `tel`, etc.)

### Cards & Lists

- [ ] Cards have **adequate padding** (16-20px, more than desktop's 12-16px)
- [ ] Card tap area extends to **entire card**, not just title
- [ ] List items have **single clear action** (entire row taps, or separate action button)
- [ ] Horizontal swipe actions are **discoverable** (partial peek, tutorial, or common pattern)
- [ ] Infinite scroll has **loading indicator** and handles slow connections gracefully
- [ ] Empty states are **helpful** (illustration + actionable message, not just "No items")

### Navigation

- [ ] Primary nav is **at bottom** for thumb reach (iOS convention) or hamburger menu
- [ ] Tab bar icons have **labels** (text + icon, not icon-only)
- [ ] Active state is **clearly indicated** (color + underline/badge)
- [ ] Back button is **always accessible** (top-left, or swipe-from-edge gesture)
- [ ] Breadcrumbs replaced with **hierarchical back** navigation
- [ ] Nested navigation uses **drill-down pattern**, not dropdowns

### Modals & Overlays

- [ ] Modals are **full-screen** on mobile (not floating)
- [ ] Modal headers are **sticky** with clear close/back button
- [ ] Modal content is **scrollable** if it exceeds viewport
- [ ] Bottom sheets used for **quick actions** (preferred over full modals when appropriate)
- [ ] Confirmation dialogs are **bottom-aligned** for thumb reach
- [ ] Toasts/snackbars appear **above bottom nav/actions** (not hidden behind)

### Tables & Data

- [ ] Tables converted to **stacked card layout** (one row = one card)
- [ ] Most important data is **at top** of each card
- [ ] Data is **scannable** (bold labels, clear hierarchy)
- [ ] Horizontal scroll avoided unless **clearly indicated** (visible scrollbar, "swipe" hint)
- [ ] If horizontal scroll necessary, use **scroll snap** (`scroll-snap-type: x mandatory`)
- [ ] Long text truncates with **ellipsis** and tap-to-expand option

## Priority 3: Layout & Visual Design

These make the app feel polished and purpose-built for mobile.

### Layout Patterns

- [ ] Single-column layout preferred over multi-column
- [ ] Sidebar patterns converted to **drawer** (slide-in from left/right)
- [ ] Multi-step flows use **wizard pattern** (one step per screen)
- [ ] Dashboard cards **stack vertically** (no side-by-side)
- [ ] Content-heavy pages use **tabs** (not sidebar sections)
- [ ] Fixed headers are **compact** (minimal height, maybe hide on scroll)

### Images & Media

- [ ] Hero images are **responsive** (`max-width: 100%`, `height: auto`)
- [ ] Aspect ratios are **maintained** (no squished/stretched images)
- [ ] Large images are **lazy loaded** (below the fold)
- [ ] Image galleries use **native scroll** (not custom JS slider unless necessary)
- [ ] Thumbnails are **large enough** to identify (min 80x80px)
- [ ] Background images have **sufficient text contrast** (dark overlay, or high-contrast text)

### Responsive Breakpoints

Standard breakpoints (adjust based on content):
- [ ] **Mobile:** 0-640px (single column, full-width components)
- [ ] **Tablet:** 641-1024px (optional: 2-column layouts start here)
- [ ] **Desktop:** 1025px+ (multi-column, sidebars, more compact)

**Mobile-first approach:** Design for 375px wide (iPhone SE/8) and scale up.

Common breakpoint patterns:
- [ ] 375px: Base mobile (iPhone SE, older Android)
- [ ] 414px: Large mobile (iPhone Pro Max)
- [ ] 768px: Tablet portrait (iPad)
- [ ] 1024px: Tablet landscape / small desktop

### Visual Hierarchy

- [ ] Screen title is **prominent** (24-32px, top of screen)
- [ ] Primary action is **visually dominant** (color, size, position)
- [ ] Sections have **clear separation** (whitespace, dividers, or background colors)
- [ ] Z-index is **sensible** (modals > popovers > sticky elements > content)
- [ ] Shadows are **subtle** and used sparingly (lighter than desktop)
- [ ] Borders are **sufficient weight** (1-2px, not hairline 0.5px)

### Consistency & Branding

- [ ] **Consistent spacing system** (8px grid: 8, 16, 24, 32, 40, 48)
- [ ] **Consistent color palette** (limited to 3-5 main colors + neutrals)
- [ ] **Consistent border radius** (0, 4, 8, 12, or 16px — pick 1-2 values)
- [ ] **Platform-appropriate patterns** (iOS: bottom tabs, Android: top tabs or drawer)
- [ ] **Brand identity maintained** without compromising usability
- [ ] **Icon style consistent** (all outline, all filled, or clear usage rules)

## Platform-Specific Design Considerations

### iOS Design Patterns

- [ ] Navigation bar at top (44px height)
- [ ] Tab bar at bottom (49px height, 5 items max)
- [ ] System fonts: SF Pro Text, SF Pro Display
- [ ] Rounded corners more common (8-12px)
- [ ] Subtle shadows and depth
- [ ] Swipe-from-edge to go back
- [ ] Blue accent color for links/actions

### Android Material Design Patterns

- [ ] Top app bar (56dp height)
- [ ] Bottom app bar or navigation drawer
- [ ] Roboto font family
- [ ] Floating action button (FAB) for primary action
- [ ] More prominent shadows (elevation)
- [ ] Ripple effects on tap
- [ ] Teal/blue accent colors common

**Cross-platform approach:** Choose patterns that work on both (bottom nav + rounded corners is safe), or detect platform and adapt.

## Quick Design Review Questions

Ask yourself these when reviewing mobile designs:

1. **Readability:** Can I read this at arm's length in bright sunlight?
2. **Thumb reach:** Can I hit every interactive element with my thumb while holding phone naturally?
3. **First tap:** What do I tap first? Is it obvious?
4. **Cognitive load:** How much info can I process in one glance? (Less is more on mobile)
5. **Exit paths:** How do I go back, cancel, or dismiss? Is it always clear?
6. **Empty states:** What happens when there's no data? Is it helpful?
7. **Error states:** What happens when something fails? Is recovery clear?
8. **Loading states:** How long will I wait? Is progress indicated?

## Quick Grep Patterns for Design Issues

```bash
# Find small font sizes (readability issues)
grep -rE "font-size:\s*(1[0-5]|[0-9])px" --include="*.css" --include="*.scss" --include="*.tsx"

# Find low contrast colors (manually review)
grep -rE "color:\s*(#[0-9a-fA-F]{3,6}|rgba?)" --include="*.css" --include="*.scss"

# Find fixed-width elements (responsive issues)
grep -rE "width:\s*[0-9]+px" --include="*.css" --include="*.scss"

# Find small touch targets (covered in technical, but good to cross-check)
grep -rE "(width|height|min-width|min-height):\s*([1-3][0-9]|[0-9])px" --include="*.css"
```

## Design Tokens Starter Template

If you're creating a design system for mobile, start with these:

```css
/* Typography Scale (Mobile-First) */
--text-xs: 12px;   /* Helper text, labels */
--text-sm: 14px;   /* Secondary text */
--text-base: 16px; /* Body text (MINIMUM) */
--text-lg: 18px;   /* Emphasized body */
--text-xl: 20px;   /* Heading 3 */
--text-2xl: 24px;  /* Heading 2 */
--text-3xl: 28px;  /* Heading 1 */
--text-4xl: 32px;  /* Hero heading */

/* Spacing Scale (8px Grid) */
--space-1: 8px;
--space-2: 16px;
--space-3: 24px;
--space-4: 32px;
--space-5: 40px;
--space-6: 48px;

/* Touch Targets */
--touch-min: 44px;  /* Apple HIG minimum */
--touch-comfortable: 48px; /* Preferred */
--touch-large: 56px; /* Primary actions */

/* Border Radius */
--radius-sm: 4px;   /* Subtle */
--radius-md: 8px;   /* Standard */
--radius-lg: 12px;  /* Prominent */
--radius-full: 9999px; /* Pills */

/* Z-Index Scale */
--z-base: 0;
--z-dropdown: 1000;
--z-sticky: 1100;
--z-modal-backdrop: 1200;
--z-modal: 1300;
--z-toast: 1400;
```

## Figma/Design Tool Checklist

If working from Figma designs:

- [ ] Artboards are **375px width** (mobile-first, iPhone SE base)
- [ ] Safe areas marked for **notch and home indicator**
- [ ] Touch targets annotated with **44x44px overlays**
- [ ] Typography styles use **16px minimum** for body
- [ ] Color contrast checked with **plugin** (Stark, Contrast)
- [ ] Spacing uses **8px grid** (check with grid overlay)
- [ ] Interactive states defined: **default, hover (desktop only), active, disabled**
- [ ] Component variants for **iOS vs Android** if platform-specific

## Priority 4: Component Composition & Reusability

Building a maintainable mobile design system requires thoughtful component architecture.

### Design System Hierarchy

Use atomic design principles adapted for mobile:

**Atoms** (Primitives)
- [ ] **Typography tokens** defined (scale, weights, line heights)
- [ ] **Color palette** limited (3-5 brand colors + neutrals + semantic)
- [ ] **Spacing scale** consistent (8px grid system)
- [ ] **Border radius scale** minimal (pick 2-3 values max)
- [ ] **Shadow/elevation scale** (3-4 levels max)
- [ ] **Icon set** consistent style (all outline OR all filled)

**Molecules** (Simple Components)
- [ ] **Button component** with variants (primary, secondary, tertiary, destructive)
- [ ] **Input component** with states (default, focused, error, disabled)
- [ ] **Badge/Tag component** for status indicators
- [ ] **Avatar component** with size variants
- [ ] **Icon button** component (icon-only actions)
- [ ] **Chip/Pill** component (removable tags)

**Organisms** (Complex Components)
- [ ] **Card component** composable (header, content, footer slots)
- [ ] **List item** with flexible layouts (avatar + text, action buttons)
- [ ] **Form group** (label + input + error + helper text)
- [ ] **Navigation bar** (top or bottom, with active states)
- [ ] **Modal/Sheet** with consistent structure
- [ ] **Toast/Snackbar** for feedback

**Templates** (Page Patterns)
- [ ] **List view** template (empty state, loading, error, success)
- [ ] **Detail view** template (header, content, actions)
- [ ] **Form** template (multi-step, single-page)
- [ ] **Settings/Profile** template

### Component Variants & States

Every interactive component needs consistent states:

- [ ] **Default** - Initial appearance
- [ ] **Hover** - Desktop only (use `@media (hover: hover)`)
- [ ] **Active/Pressed** - Visual feedback during tap
- [ ] **Focused** - For keyboard navigation (accessibility)
- [ ] **Disabled** - Clear but not distracting (opacity 0.5-0.6)
- [ ] **Loading** - Spinner or skeleton, maintains size
- [ ] **Error** - Red outline/background, error icon
- [ ] **Success** - Green indicator, checkmark

**State design principles:**
- States should be **obvious at a glance** (not subtle color shifts)
- Disabled states should be **clearly inactive** (low opacity + no pointer)
- Loading states should **maintain layout** (don't cause shifts)
- Error states should **explain what's wrong** (not just turn red)

### Component Composability

Design components to work together:

- [ ] **Consistent sizing** - Components share height scale (40, 44, 48, 56px)
- [ ] **Consistent spacing** - Internal padding matches spacing scale
- [ ] **Flexible layouts** - Components adapt to container width
- [ ] **Slot-based architecture** - Components accept children (header, content, footer)
- [ ] **Prop-driven variants** - Use props, not separate components (`<Button variant="primary" size="large" />`)

**Composability patterns:**

```tsx
// Good: Composable card
<Card>
  <Card.Header>
    <Avatar src={user.avatar} />
    <Text>{user.name}</Text>
  </Card.Header>
  <Card.Content>
    <Text>{post.body}</Text>
  </Card.Content>
  <Card.Footer>
    <Button variant="secondary">Like</Button>
    <Button variant="secondary">Comment</Button>
  </Card.Footer>
</Card>

// Bad: Monolithic card with too many props
<PostCard 
  avatar={user.avatar}
  name={user.name}
  body={post.body}
  onLike={handleLike}
  onComment={handleComment}
  showLikeButton={true}
  showCommentButton={true}
/>
```

### When to Create New Components

- [ ] **Reused 3+ times** - Abstract into component
- [ ] **Complex internal logic** - Encapsulate (date picker, dropdown)
- [ ] **Consistent behavior needed** - Ensure all instances behave the same
- [ ] **Design system standard** - Make it official

**When NOT to create components:**
- Used only once (keep it inline)
- No shared behavior or styling
- Would require too many props to be useful

### Design Tokens & Theming

Design tokens enable consistent styling and theming:

```css
/* Color tokens - semantic naming */
--color-text-primary: #1a1a1a;
--color-text-secondary: #666666;
--color-text-tertiary: #999999;
--color-bg-primary: #ffffff;
--color-bg-secondary: #f5f5f5;
--color-border: #e0e0e0;

/* Semantic color tokens */
--color-success: #22c55e;
--color-error: #ef4444;
--color-warning: #f59e0b;
--color-info: #3b82f6;

/* Interactive colors */
--color-interactive: #3b82f6;
--color-interactive-hover: #2563eb;
--color-interactive-active: #1d4ed8;

/* Component-specific tokens */
--button-primary-bg: var(--color-interactive);
--button-primary-text: #ffffff;
--button-secondary-bg: transparent;
--button-secondary-border: var(--color-border);
```

**Token principles:**
- [ ] **Two-tier system** - Primitive tokens → semantic tokens
- [ ] **Semantic naming** - Purpose-based, not appearance-based (`text-primary` not `gray-900`)
- [ ] **Mobile-optimized values** - Larger touch targets, more spacing
- [ ] **Dark mode ready** - Use CSS variables, test in both modes

### Component Documentation

Every component needs:

- [ ] **Purpose** - When to use it
- [ ] **Variants** - All available options
- [ ] **States** - How it looks in each state
- [ ] **Sizing** - Available sizes
- [ ] **Accessibility** - Keyboard navigation, screen reader support
- [ ] **Mobile considerations** - Touch target size, thumb reach
- [ ] **Code example** - Copy-paste ready

**Example documentation template:**

```markdown
## Button Component

**Purpose:** Primary action triggers throughout the app.

**Variants:**
- primary: Main actions (blue background)
- secondary: Less important actions (outline)
- tertiary: Subtle actions (ghost)
- destructive: Delete/remove actions (red)

**Sizes:**
- small: 40px height (compact areas)
- medium: 48px height (default)
- large: 56px height (prominent actions)

**Mobile considerations:**
- Minimum 44px tap target (medium size default)
- Full-width on mobile screens < 640px
- Touch feedback with scale animation
```

## Priority 5: Animation & Motion Design

Motion enhances mobile UX when done right, but can hurt performance if overdone.

### Animation Duration Guidelines

Use consistent timing across your app:

| Duration | Use Case | Example |
|----------|----------|---------|
| **50-100ms** | Micro-interactions | Button press, toggle switch |
| **150-200ms** | Simple transitions | Fade in/out, color change |
| **250-350ms** | Component transitions | Modal slide up, drawer open |
| **400-500ms** | Page transitions | Route change, tab switch |
| **500ms+** | Complex animations | Multi-step flows, celebrations |

**Mobile-specific timing:**
- Mobile animations should be **slightly faster** than desktop (20-30% less duration)
- Longer animations feel sluggish on mobile
- Exception: Loading states can be longer to indicate work is happening

### Easing Curves

Choose easing based on animation type:

**Ease-out** (Deceleration)
- **Use for:** Entering elements, objects coming to rest
- **Curve:** `cubic-bezier(0, 0, 0.2, 1)` or `ease-out`
- **Feel:** Snappy, responsive
- **Example:** Modal slides up from bottom

**Ease-in** (Acceleration)
- **Use for:** Exiting elements, objects leaving screen
- **Curve:** `cubic-bezier(0.4, 0, 1, 1)` or `ease-in`
- **Feel:** Quick exit
- **Example:** Toast dismisses

**Ease-in-out** (Acceleration + Deceleration)
- **Use for:** Transitions between states, position changes
- **Curve:** `cubic-bezier(0.4, 0, 0.2, 1)` or `ease-in-out`
- **Feel:** Smooth, natural
- **Example:** Expanding card to full screen

**Spring/Bounce**
- **Use for:** Playful interactions, emphasizing change
- **Implementation:** CSS `cubic-bezier()` or JavaScript spring physics
- **Example:** Pull-to-refresh rubber band effect

**Linear**
- **Use for:** Constant-speed animations, loading indicators
- **Curve:** `linear`
- **Feel:** Mechanical, predictable
- **Example:** Progress bar, spinner

**Mobile default recommendation:** Use ease-out (0, 0, 0.2, 1) for 80% of animations. It feels most responsive on touch devices.

### Motion Principles

Follow Disney's 12 principles adapted for mobile UI:

**1. Staging**
- [ ] One animation at a time (don't animate everything simultaneously)
- [ ] Focus attention on the important change
- [ ] Example: When opening modal, animate modal first, then fade in backdrop

**2. Follow-through & Overlapping Action**
- [ ] Elements continue moving slightly after main action stops
- [ ] Stagger animations for grouped elements (cards in a list)
- [ ] Example: List items fade in with 50ms stagger

**3. Ease In & Out**
- [ ] Nothing moves at constant speed in nature
- [ ] Always use easing curves, never linear (except spinners)
- [ ] Match easing to context (ease-out for entrances)

**4. Anticipation**
- [ ] Small movement before main action
- [ ] Example: Button scales down slightly before bouncing back on tap

**5. Exaggeration**
- [ ] Subtle overshot makes animation feel alive
- [ ] Don't overdo it (10-20% beyond target, then settle)
- [ ] Example: Modal slides up past resting point, then settles

**6. Secondary Action**
- [ ] Supporting animations enhance main action
- [ ] Example: When drawer opens, content dims behind it

### Platform-Specific Motion

**iOS Motion Patterns:**
- [ ] **Spring animations** preferred (bounce feel)
- [ ] **Slide transitions** for navigation (push/pop)
- [ ] **Modal from bottom** with handle for swipe-to-dismiss
- [ ] **Fade + scale** for alerts
- [ ] **Parallax scrolling** in headers (slow background layer)

**Android Material Motion:**
- [ ] **Sharper easing** (less bouncy than iOS)
- [ ] **Shared element transitions** between screens
- [ ] **FAB transforms** into full screen
- [ ] **Elevation changes** during transitions
- [ ] **Ripple effects** on tap

### Performance Optimization

Animations must be 60fps (16.67ms per frame):

- [ ] **Only animate transform and opacity** (GPU-accelerated)
- [ ] **Avoid animating:** width, height, top, left, margin, padding
- [ ] **Use will-change sparingly** (`will-change: transform` before animation)
- [ ] **Remove will-change** after animation completes
- [ ] **Debounce scroll animations** (use requestAnimationFrame)

**GPU-accelerated properties:**
```css
/* Good - GPU accelerated */
.animated {
  transform: translateX(100px);
  opacity: 0;
  transition: transform 300ms ease-out, opacity 300ms ease-out;
}

/* Bad - triggers layout reflow */
.animated {
  left: 100px;
  display: none;
  transition: left 300ms;
}
```

### Reduced Motion

Always respect user preferences:

```css
@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }
}
```

- [ ] All animations respect `prefers-reduced-motion`
- [ ] Alternative for motion: instant state changes with opacity fade
- [ ] Don't remove feedback entirely (still show state changes)

### Animation Checklist

- [ ] **Purpose clear** - Animation serves a functional purpose (not decoration)
- [ ] **Duration appropriate** - 50-350ms for most mobile interactions
- [ ] **Easing natural** - Ease-out for entrances, ease-in for exits
- [ ] **Performance maintained** - Only transform/opacity, 60fps
- [ ] **Reduced motion supported** - Animations shortened/removed
- [ ] **Consistent across app** - Same patterns for similar interactions
- [ ] **Stagger grouped elements** - 50-100ms delay between items
- [ ] **Loading states clear** - Skeleton screens or spinners for long operations

### Common Animation Patterns

**Page Transitions:**
```css
/* Slide in from right (push) */
.page-enter {
  transform: translateX(100%);
}
.page-enter-active {
  transform: translateX(0);
  transition: transform 300ms cubic-bezier(0, 0, 0.2, 1);
}

/* Fade out (pop) */
.page-exit {
  opacity: 1;
}
.page-exit-active {
  opacity: 0;
  transition: opacity 200ms ease-out;
}
```

**Modal Slide Up:**
```css
.modal-enter {
  transform: translateY(100%);
}
.modal-enter-active {
  transform: translateY(0);
  transition: transform 350ms cubic-bezier(0, 0, 0.2, 1);
}
```

**List Stagger:**
```css
.list-item {
  opacity: 0;
  transform: translateY(20px);
  animation: fadeInUp 300ms ease-out forwards;
}

/* Stagger delay */
.list-item:nth-child(1) { animation-delay: 0ms; }
.list-item:nth-child(2) { animation-delay: 50ms; }
.list-item:nth-child(3) { animation-delay: 100ms; }

@keyframes fadeInUp {
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
```

## Priority 6: Information Architecture for Mobile

Mobile IA requires ruthless prioritization and clear navigation.

### Content Hierarchy Principles

Mobile screens show ~40% of desktop content at once:

**Progressive Disclosure:**
- [ ] Show **essential info first**, details on demand
- [ ] Use **expand/collapse** for secondary information
- [ ] **Truncate long text** with "Read more"
- [ ] **Tabs** for grouping related content
- [ ] **Accordions** for FAQ/settings sections

**Priority levels:**
1. **Critical** (always visible): Page title, primary action, key data
2. **Important** (visible within 1-2 scrolls): Supporting info, secondary actions
3. **Optional** (behind tap/expand): Details, help text, advanced options

**Example: Product page**
```
Critical:
- Product name
- Price
- "Add to Cart" button
- Main product image

Important:
- Rating/reviews summary
- Key features (3-5 bullets)
- Size/color picker

Optional:
- Full description (expand)
- Shipping details (expand)
- Reviews list (separate page)
- Specifications (expand)
```

### Navigation Depth

Mobile navigation should be **shallow and wide**, not **deep and narrow**:

**Recommended structure:**
- **Max 3 levels deep** (Home → Category → Item)
- **5-7 main sections** in bottom nav or hamburger
- **Breadcrumb alternative:** Hierarchical back button with section name

**Navigation patterns:**

| Pattern | When to Use | Depth Limit |
|---------|-------------|-------------|
| **Bottom tabs** | 3-5 main sections, frequent switching | 2 levels (tab → detail) |
| **Hamburger menu** | 5+ sections, less frequent navigation | 3 levels max |
| **Top tabs** | 2-4 related views (Android pattern) | 2 levels |
| **Hub navigation** | 6-12 sections, infrequent access | 3 levels (hub → section → detail) |

**Bad IA example (too deep):**
```
Home → Shop → Categories → Electronics → Computers → Laptops → Gaming → Brand → Model
(8 levels - user gets lost)
```

**Good IA example (shallow):**
```
Home → Gaming Laptops → Model
(3 levels - direct access)
```

### Task Flows for Mobile

Design for **single-handed use** and **thumb-driven navigation**:

- [ ] **Primary actions at bottom** (thumb reach zone)
- [ ] **Back button always top-left** (or swipe from edge)
- [ ] **Cancel/close top-right** (less critical, harder to reach)
- [ ] **Confirm/submit bottom-right** (thumb-friendly, right-handed users)

**Thumb reach zones (right-handed):**
- **Easy reach:** Bottom 1/3 of screen, right side
- **Stretch reach:** Middle of screen, left side
- **Hard reach:** Top of screen (both sides)

Place important actions in easy reach zones.

### Search & Findability

Mobile search needs to be prominent and powerful:

- [ ] **Search icon always visible** (top-right or dedicated tab)
- [ ] **Recent searches** shown immediately
- [ ] **Autocomplete** with suggestions
- [ ] **Filters** accessible from search results (drawer or sheet)
- [ ] **Voice search** available (dictation icon)
- [ ] **Scoped search** when deep in app (search within section)

**Search results optimization:**
- Show **most relevant first** (not alphabetical)
- Include **thumbnail/icon** for visual recognition
- Show **breadcrumb path** for context
- Allow **sorting and filtering** without leaving results
- **Infinite scroll** with "Load more" option

### Multi-Step Flows

Forms and wizards need clear progress indicators:

**Step indicators:**
- [ ] **Progress bar at top** (always visible)
- [ ] **Step count** "Step 2 of 4"
- [ ] **Named steps** "Shipping → Payment → Review"
- [ ] **Non-linear when possible** (tap to jump to step)

**Flow best practices:**
- [ ] **One question per screen** for complex forms
- [ ] **Smart defaults** pre-filled when possible
- [ ] **Skip options** for optional steps
- [ ] **Save & exit** at any point
- [ ] **Review before submit** (summary of all inputs)

**Example: Checkout flow**
```
Step 1: Shipping (address autocomplete)
Step 2: Delivery (3 options: standard/express/pickup)
Step 3: Payment (saved cards + add new)
Step 4: Review (edit any section, then confirm)
```

### Navigation Patterns by App Type

**E-commerce:**
- Bottom tabs: Home, Categories, Cart, Account
- Search prominent in top bar
- Filters in slide-out drawer
- Product detail: sticky Add to Cart

**Social Media:**
- Bottom tabs: Feed, Search, Create, Notifications, Profile
- Infinite scroll on feed
- Swipe between tabs (Stories, Reels, etc.)
- Double-tap to like (gestural)

**Productivity:**
- Hamburger menu (many sections)
- FAB for primary action (compose, create)
- Swipe to archive/delete in lists
- Long-press for context menu

**Content/News:**
- Bottom tabs: For You, Following, Saved
- Vertical scroll (infinite feed)
- Swipe left/right for article navigation
- Header hides on scroll (more reading space)

### Information Scent

Users need clear cues about where taps will take them:

- [ ] **Link preview text** descriptive (not "Click here")
- [ ] **Icons match destination** (standard iconography)
- [ ] **Cards show preview** of content (image + headline + snippet)
- [ ] **Chevron/arrow indicates** deeper navigation (→)
- [ ] **External links** marked with icon (↗)

**Good link text:**
- "View shipping options" (clear destination)
- "Read full article" (clear action + destination)
- "Contact support" (clear purpose)

**Bad link text:**
- "Click here" (no context)
- "More" (more what?)
- "Learn more" (vague, overused)

### Empty States

Every list/feed needs a helpful empty state:

- [ ] **Illustration or icon** (visual interest)
- [ ] **Headline** explains why empty
- [ ] **Description** gives context
- [ ] **Primary action** to populate (if applicable)

**Empty state examples:**

```
No Notifications
You're all caught up! New notifications will appear here.
[Secondary empty state - no action needed]

No Items in Cart
Start shopping to add items to your cart.
[Browse Products] button
[Primary action - clear next step]

No Search Results for "xyz"
Try different keywords or browse categories.
[Browse Categories] button
[Helpful guidance + alternative action]
```

### IA Audit Questions

When reviewing mobile information architecture:

1. **Can I complete key tasks in 3 taps or less?**
2. **Is primary navigation obvious within 2 seconds?**
3. **Can I navigate one-handed with my thumb?**
4. **Is critical info visible without scrolling?**
5. **Can I go back from anywhere?**
6. **Do I understand where each link takes me before tapping?**
7. **Are multi-step flows clearly indicated?**
8. **Is search accessible from every screen?**

### Mobile IA Anti-Patterns

Avoid these common mistakes:

- ❌ **Mega menus** (impossible on mobile, use categorized hamburger)
- ❌ **Horizontal navigation** (requires scrolling, hard to discover)
- ❌ **Deep nesting** (>3 levels, users get lost)
- ❌ **Duplicate navigation** (bottom tabs + hamburger for same items)
- ❌ **No breadcrumbs/context** (user doesn't know where they are)
- ❌ **Mystery meat navigation** (icons without labels)
- ❌ **Infinite carousels** (users swipe past important content)
- ❌ **Hidden actions** (hamburger or ⋯ menu for critical features)

## Integration with Technical Checklist

Design and technical checklists work together:

| Technical Issue | Design Consideration |
|----------------|---------------------|
| 44x44px touch targets (technical) | Adequate visual padding around button text (design) |
| Input font-size 16px+ (technical) | Typography scale ensures readability (design) |
| `100dvh` viewport (technical) | Layout doesn't feel cramped in available space (design) |
| Keyboard handling (technical) | Form layout adapts gracefully when keyboard appears (design) |
| Platform detection (technical) | Design follows iOS vs Android conventions (design) |
| Color contrast ratio (technical) | Brand colors adjusted for mobile (design) |

When auditing, run both checklists and cross-reference findings.
