# Platform Quirks

iOS Safari and Android Chrome behave differently. This reference covers platform-specific issues and fixes.

## iOS Safari

### The Notorious `100vh` Problem

**Issue:** `100vh` includes the address bar height, causing content to be hidden behind it.

**Fix:**
```css
/* Modern solution */
height: 100dvh;

/* Fallback for older iOS */
height: 100vh;
height: -webkit-fill-available;
```

### Input Zoom

**Issue:** iOS zooms in when focusing inputs with font-size < 16px.

**Fix:**
```css
input, select, textarea {
  font-size: 16px;
}

/* Or use transform to fake smaller text */
input {
  font-size: 16px;
  transform: scale(0.875);
  transform-origin: left center;
}
```

### Momentum Scrolling

**Issue:** Scroll containers feel "dead" without momentum.

**Fix:**
```css
.scroll-container {
  -webkit-overflow-scrolling: touch;
  overflow-y: auto;
}
```

### Position Fixed + Keyboard

**Issue:** Fixed elements jump or get pushed when keyboard opens.

**Fix:** Use `visualViewport` API:
```tsx
useEffect(() => {
  const viewport = window.visualViewport;
  const fixedEl = document.querySelector('.fixed-footer');
  
  const onResize = () => {
    if (fixedEl) {
      fixedEl.style.bottom = `${window.innerHeight - viewport.height}px`;
    }
  };
  
  viewport?.addEventListener('resize', onResize);
  return () => viewport?.removeEventListener('resize', onResize);
}, []);
```

### Rubber Banding / Bounce

**Issue:** Page bounces when scrolling past edges, can feel broken.

**Fix (to disable):**
```css
html, body {
  overscroll-behavior: none;
}
```

**Fix (for scroll containers):**
```css
.container {
  overscroll-behavior: contain;
}
```

### Safe Areas (Notch, Home Indicator)

**Issue:** Content hidden behind notch or home indicator.

**Fix:**
```html
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
```

```css
.header {
  padding-top: env(safe-area-inset-top);
}

.footer {
  padding-bottom: env(safe-area-inset-bottom);
}
```

### Video Autoplay

**Issue:** Videos don't autoplay, open fullscreen by default.

**Fix:**
```html
<video autoplay muted playsinline>
```

All three attributes required for inline autoplay.

### Date Input

**Issue:** `<input type="date">` opens native picker but styling is limited.

**Fix:** Often better to use a custom date picker component, or accept the native picker's appearance.

### Scroll Position on Back Navigation

**Issue:** iOS restores scroll position inconsistently.

**Fix:**
```tsx
// Save position before navigation
sessionStorage.setItem('scrollPos', window.scrollY.toString());

// Restore on mount
useEffect(() => {
  const saved = sessionStorage.getItem('scrollPos');
  if (saved) {
    window.scrollTo(0, parseInt(saved));
  }
}, []);
```

### 300ms Tap Delay

**Issue:** Old iOS had 300ms delay waiting for double-tap zoom.

**Fix:**
```css
* {
  touch-action: manipulation;
}
```

### Click vs Touch Events

**Issue:** `onClick` fires after touch with delay.

**Fix:** For time-sensitive interactions, use `onTouchEnd`:
```tsx
<button
  onTouchEnd={(e) => {
    e.preventDefault();
    handleAction();
  }}
  onClick={handleAction} // Fallback for non-touch
>
```

---

## Android Chrome

### Viewport Units

**Issue:** Android handles viewport units more consistently than iOS, but older versions may not support `dvh`.

**Fix:**
```css
height: 100dvh;
height: 100vh; /* Fallback */
```

### Pull to Refresh

**Issue:** Chrome's native pull-to-refresh interferes with custom implementations.

**Fix:**
```css
body {
  overscroll-behavior-y: contain;
}
```

### Address Bar Hide/Show

**Issue:** Address bar hides on scroll, changing viewport height.

**Fix:** Same `visualViewport` approach as iOS, but Android is more predictable.

### Input Types

**Issue:** Keyboard type varies more across Android devices.

**Fix:** Be explicit with `inputmode`:
```html
<input type="text" inputmode="numeric" pattern="[0-9]*">
```

### Font Rendering

**Issue:** Fonts render differently, especially custom fonts.

**Fix:**
```css
body {
  -webkit-font-smoothing: antialiased;
  text-rendering: optimizeLegibility;
}
```

### Tap Highlight

**Issue:** Blue highlight on tap is more prominent on Android.

**Fix:**
```css
* {
  -webkit-tap-highlight-color: transparent;
}
```

### Back Button

**Issue:** Hardware/gesture back button behavior.

**Fix:** Handle with History API:
```tsx
useEffect(() => {
  const handleBack = () => {
    // Custom back behavior
    if (isModalOpen) {
      closeModal();
      return;
    }
    // Default: navigate back
  };

  window.addEventListener('popstate', handleBack);
  return () => window.removeEventListener('popstate', handleBack);
}, [isModalOpen]);

// Push state when opening modal
const openModal = () => {
  history.pushState({ modal: true }, '');
  setIsModalOpen(true);
};
```

---

## Cross-Platform Gotchas

### Hover States

**Issue:** `:hover` is "sticky" on touch devices.

**Fix:**
```css
@media (hover: hover) and (pointer: fine) {
  .button:hover {
    background: blue;
  }
}

/* For touch, use active */
@media (hover: none) {
  .button:active {
    background: blue;
  }
}
```

### Selection

**Issue:** Text selection behaves differently, can interfere with gestures.

**Fix (disable on interactive elements):**
```css
.button, .card {
  -webkit-user-select: none;
  user-select: none;
}
```

### Orientation Change

**Issue:** Layout breaks or text resizes on rotation.

**Fix:**
```css
html {
  -webkit-text-size-adjust: 100%;
}
```

```tsx
useEffect(() => {
  const handleOrientationChange = () => {
    // Force reflow if needed
    document.body.style.display = 'none';
    document.body.offsetHeight; // Trigger reflow
    document.body.style.display = '';
  };

  window.addEventListener('orientationchange', handleOrientationChange);
  return () => window.removeEventListener('orientationchange', handleOrientationChange);
}, []);
```

### PWA vs Browser

| Behavior | Browser | PWA Standalone |
|----------|---------|----------------|
| Safe areas | May include browser chrome | Only device safe areas |
| Status bar | Managed by browser | App controls theme-color |
| Navigation | Browser back/forward | App must handle |
| Viewport | Dynamic with chrome | Fixed |

---

## Detection Patterns

```tsx
// Detect iOS
const isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent);

// Detect Safari specifically
const isSafari = /^((?!chrome|android).)*safari/i.test(navigator.userAgent);

// Detect if running as PWA
const isPWA = window.matchMedia('(display-mode: standalone)').matches;

// Detect touch capability
const isTouchDevice = 'ontouchstart' in window || navigator.maxTouchPoints > 0;

// Detect if keyboard likely visible (heuristic)
const isKeyboardVisible = window.visualViewport 
  && window.visualViewport.height < window.innerHeight * 0.75;
```

**Note:** User agent detection is fragile. Prefer feature detection when possible:
```tsx
// Better: Feature detection
const supportsHover = window.matchMedia('(hover: hover)').matches;
const supportsTouchAction = CSS.supports('touch-action', 'manipulation');
const supportsDvh = CSS.supports('height', '100dvh');
```
