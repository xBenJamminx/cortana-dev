# Mobile Audit Checklist

Run through this checklist when auditing existing code for mobile issues.

## Priority 1: Breaking Issues

These cause the app to be unusable on mobile.

### Viewport
- [ ] No `100vh` for full-height layouts (use `100dvh` or `100svh`)
- [ ] `<meta name="viewport" content="width=device-width, initial-scale=1">` present
- [ ] No `user-scalable=no` or `maximum-scale=1` (accessibility violation)
- [ ] Form inputs have `font-size: 16px` or larger (prevents iOS zoom)

### Touch Targets
- [ ] All buttons/links at least 44x44px tap area
- [ ] Adequate spacing between adjacent touch targets (8px minimum)
- [ ] No critical actions hidden behind hover-only interactions

### Keyboard
- [ ] Inputs don't get hidden behind keyboard
- [ ] Fixed/sticky elements don't overlap input when keyboard opens
- [ ] Form can be submitted without scrolling past keyboard

## Priority 2: Degraded Experience

These make the app feel non-native.

### Scrolling
- [ ] Scroll containers have `-webkit-overflow-scrolling: touch`
- [ ] No scroll chaining where unintended (`overscroll-behavior: contain`)
- [ ] Pull-to-refresh disabled if custom implementation exists
- [ ] Horizontal scroll areas have visible scroll indicators or hints

### Touch Feedback
- [ ] Interactive elements have visible tap feedback
- [ ] No lingering `:hover` states after tap
- [ ] No 300ms tap delay (`touch-action: manipulation`)
- [ ] Tap highlight removed or styled (`-webkit-tap-highlight-color`)

### Layout
- [ ] No horizontal overflow causing accidental side-scroll
- [ ] Tables converted to stacked/card layout on mobile
- [ ] Modals don't exceed viewport height
- [ ] Sidebars collapse to drawer pattern on mobile

### Images & Media
- [ ] Images use responsive sizing (`max-width: 100%`)
- [ ] Large images lazy loaded
- [ ] No fixed-width images breaking layout
- [ ] Videos have `playsinline` attribute for iOS

## Priority 3: Polish

These make the app feel truly native.

### Platform Conventions
- [ ] Safe areas respected (notch, home indicator)
- [ ] System font stack matches platform (`-apple-system, system-ui`)
- [ ] Correct input types (`type="tel"`, `type="email"`, etc.)
- [ ] `inputmode` attribute for appropriate keyboard

### Gestures
- [ ] Swipe gestures for common actions (dismiss, navigate)
- [ ] Long-press for contextual actions (where expected)
- [ ] Pinch-to-zoom only where appropriate (maps, images)
- [ ] Pull-to-refresh for list content (where expected)

### Animations
- [ ] Transitions use `transform` and `opacity` (GPU accelerated)
- [ ] Animations respect `prefers-reduced-motion`
- [ ] No layout shifts during animations
- [ ] Spring/ease-out curves for native feel

### PWA Considerations
- [ ] `theme-color` meta tag matches app header
- [ ] Standalone mode handles status bar correctly
- [ ] Home screen icon provided
- [ ] Splash screen configured

## Quick Grep Patterns

Find potential issues in codebase:

```bash
# Find 100vh usage (potential viewport issue)
grep -r "100vh" --include="*.css" --include="*.scss" --include="*.tsx" --include="*.jsx"

# Find hover-only patterns
grep -r ":hover" --include="*.css" --include="*.scss" | grep -v "@media"

# Find fixed positioning (keyboard issues)
grep -r "position: fixed" --include="*.css" --include="*.scss"

# Find small font sizes in inputs (zoom trigger)
grep -rE "font-size:\s*(1[0-5]|[0-9])px" --include="*.css" --include="*.scss"
```
