# React/Next.js Mobile Patterns

Copy-paste patterns for common mobile optimizations.

## Viewport Height Hook

Handle dynamic viewport height (keyboard, browser chrome):

```tsx
import { useState, useEffect } from 'react';

export function useViewportHeight() {
  const [height, setHeight] = useState<string>('100dvh');

  useEffect(() => {
    const viewport = window.visualViewport;
    if (!viewport) return;

    const updateHeight = () => {
      setHeight(`${viewport.height}px`);
    };

    updateHeight();
    viewport.addEventListener('resize', updateHeight);
    viewport.addEventListener('scroll', updateHeight);

    return () => {
      viewport.removeEventListener('resize', updateHeight);
      viewport.removeEventListener('scroll', updateHeight);
    };
  }, []);

  return height;
}

// Usage
function FullHeightContainer({ children }) {
  const height = useViewportHeight();
  return <div style={{ height }}>{children}</div>;
}
```

## Safe Area Provider

Access safe area insets in React:

```tsx
import { createContext, useContext, useState, useEffect } from 'react';

const SafeAreaContext = createContext({
  top: 0, right: 0, bottom: 0, left: 0
});

export function SafeAreaProvider({ children }) {
  const [insets, setInsets] = useState({ top: 0, right: 0, bottom: 0, left: 0 });

  useEffect(() => {
    const update = () => {
      const style = getComputedStyle(document.documentElement);
      setInsets({
        top: parseInt(style.getPropertyValue('--sat') || '0'),
        right: parseInt(style.getPropertyValue('--sar') || '0'),
        bottom: parseInt(style.getPropertyValue('--sab') || '0'),
        left: parseInt(style.getPropertyValue('--sal') || '0'),
      });
    };

    // Set CSS variables from env()
    document.documentElement.style.setProperty('--sat', 'env(safe-area-inset-top)');
    document.documentElement.style.setProperty('--sar', 'env(safe-area-inset-right)');
    document.documentElement.style.setProperty('--sab', 'env(safe-area-inset-bottom)');
    document.documentElement.style.setProperty('--sal', 'env(safe-area-inset-left)');

    update();
    window.addEventListener('resize', update);
    return () => window.removeEventListener('resize', update);
  }, []);

  return (
    <SafeAreaContext.Provider value={insets}>
      {children}
    </SafeAreaContext.Provider>
  );
}

export const useSafeArea = () => useContext(SafeAreaContext);
```

## Touch-Friendly Button

Button with proper touch target and feedback:

```tsx
import { forwardRef } from 'react';

interface TouchButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary';
}

export const TouchButton = forwardRef<HTMLButtonElement, TouchButtonProps>(
  ({ className, children, ...props }, ref) => {
    return (
      <button
        ref={ref}
        className={`
          min-h-[44px] min-w-[44px] px-4
          touch-manipulation
          select-none
          [-webkit-tap-highlight-color:transparent]
          active:scale-[0.97] active:opacity-90
          transition-transform duration-100
          ${className}
        `}
        {...props}
      >
        {children}
      </button>
    );
  }
);
```

## Hover-Safe Styles

Apply hover only on devices that support it:

```tsx
// Tailwind approach
<button className="hover:bg-blue-600 hover:[@media(hover:hover)]:bg-blue-600">
  Click me
</button>

// CSS Module approach
/* styles.module.css */
.button:hover {
  /* Fallback for all */
}

@media (hover: hover) and (pointer: fine) {
  .button:hover {
    background-color: blue;
  }
}

@media (hover: none) {
  .button:active {
    background-color: blue;
  }
}
```

## Mobile Modal

Modal that works with keyboard and respects viewport:

```tsx
import { useEffect, useRef } from 'react';
import { useViewportHeight } from './useViewportHeight';

export function MobileModal({ isOpen, onClose, children }) {
  const height = useViewportHeight();
  const contentRef = useRef<HTMLDivElement>(null);

  // Prevent body scroll when modal open
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden';
      document.body.style.position = 'fixed';
      document.body.style.width = '100%';
    }
    return () => {
      document.body.style.overflow = '';
      document.body.style.position = '';
      document.body.style.width = '';
    };
  }, [isOpen]);

  if (!isOpen) return null;

  return (
    <div
      className="fixed inset-0 z-50 bg-black/50"
      style={{ height }}
      onClick={onClose}
    >
      <div
        ref={contentRef}
        className="absolute bottom-0 left-0 right-0 bg-white rounded-t-2xl max-h-[90%] overflow-y-auto overscroll-contain"
        style={{ paddingBottom: 'env(safe-area-inset-bottom)' }}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Drag handle */}
        <div className="sticky top-0 flex justify-center py-2 bg-white">
          <div className="w-10 h-1 bg-gray-300 rounded-full" />
        </div>
        {children}
      </div>
    </div>
  );
}
```

## Pull to Refresh

Native-feeling pull to refresh:

```tsx
import { useRef, useState } from 'react';

export function PullToRefresh({ onRefresh, children }) {
  const [pulling, setPulling] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const startY = useRef(0);
  const pullDistance = useRef(0);

  const handleTouchStart = (e: React.TouchEvent) => {
    if (window.scrollY === 0) {
      startY.current = e.touches[0].clientY;
      setPulling(true);
    }
  };

  const handleTouchMove = (e: React.TouchEvent) => {
    if (!pulling) return;
    pullDistance.current = Math.max(0, e.touches[0].clientY - startY.current);
  };

  const handleTouchEnd = async () => {
    if (pullDistance.current > 80) {
      setRefreshing(true);
      await onRefresh();
      setRefreshing(false);
    }
    setPulling(false);
    pullDistance.current = 0;
  };

  return (
    <div
      onTouchStart={handleTouchStart}
      onTouchMove={handleTouchMove}
      onTouchEnd={handleTouchEnd}
      className="overscroll-contain"
    >
      {refreshing && (
        <div className="flex justify-center py-4">
          <div className="animate-spin h-6 w-6 border-2 border-blue-500 border-t-transparent rounded-full" />
        </div>
      )}
      {children}
    </div>
  );
}
```

## Input with Keyboard Handling

Input that stays visible when keyboard opens:

```tsx
import { useRef, useEffect } from 'react';

export function MobileInput(props: React.InputHTMLAttributes<HTMLInputElement>) {
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    const input = inputRef.current;
    if (!input) return;

    const handleFocus = () => {
      // Wait for keyboard to open
      setTimeout(() => {
        input.scrollIntoView({ behavior: 'smooth', block: 'center' });
      }, 300);
    };

    input.addEventListener('focus', handleFocus);
    return () => input.removeEventListener('focus', handleFocus);
  }, []);

  return (
    <input
      ref={inputRef}
      className="text-[16px]" // Prevent iOS zoom
      {...props}
    />
  );
}
```

## Swipe to Dismiss

Swipeable component for cards/items:

```tsx
import { useRef, useState } from 'react';

export function SwipeToDismiss({ onDismiss, children }) {
  const [offset, setOffset] = useState(0);
  const startX = useRef(0);
  const threshold = 100;

  const handleTouchStart = (e: React.TouchEvent) => {
    startX.current = e.touches[0].clientX;
  };

  const handleTouchMove = (e: React.TouchEvent) => {
    const diff = e.touches[0].clientX - startX.current;
    setOffset(diff);
  };

  const handleTouchEnd = () => {
    if (Math.abs(offset) > threshold) {
      onDismiss();
    }
    setOffset(0);
  };

  return (
    <div
      onTouchStart={handleTouchStart}
      onTouchMove={handleTouchMove}
      onTouchEnd={handleTouchEnd}
      style={{
        transform: `translateX(${offset}px)`,
        opacity: 1 - Math.abs(offset) / 200,
        transition: offset === 0 ? 'all 0.2s' : 'none',
      }}
    >
      {children}
    </div>
  );
}
```

## Tailwind Mobile Utilities

Add to `tailwind.config.js`:

```js
module.exports = {
  theme: {
    extend: {
      spacing: {
        'safe-top': 'env(safe-area-inset-top)',
        'safe-bottom': 'env(safe-area-inset-bottom)',
        'safe-left': 'env(safe-area-inset-left)',
        'safe-right': 'env(safe-area-inset-right)',
      },
      height: {
        'screen-dvh': '100dvh',
        'screen-svh': '100svh',
        'screen-lvh': '100lvh',
      },
      minHeight: {
        'screen-dvh': '100dvh',
        'touch': '44px',
      },
      minWidth: {
        'touch': '44px',
      },
    },
  },
  plugins: [
    // Touch target plugin
    function({ addUtilities }) {
      addUtilities({
        '.touch-target': {
          'min-height': '44px',
          'min-width': '44px',
        },
        '.no-tap-highlight': {
          '-webkit-tap-highlight-color': 'transparent',
        },
        '.touch-pan-x': {
          'touch-action': 'pan-x',
        },
        '.touch-pan-y': {
          'touch-action': 'pan-y',
        },
      });
    },
  ],
};
```

## Global CSS Reset for Mobile

Add to your global CSS:

```css
/* Prevent pull-to-refresh on whole page if custom implementation */
html {
  overscroll-behavior: none;
}

/* Smooth scrolling with momentum */
* {
  -webkit-overflow-scrolling: touch;
}

/* Prevent text size adjustment on orientation change */
html {
  -webkit-text-size-adjust: 100%;
  text-size-adjust: 100%;
}

/* Safe input styling */
input, textarea, select {
  font-size: 16px; /* Prevent iOS zoom */
  -webkit-appearance: none;
  appearance: none;
  border-radius: 0; /* iOS default override */
}

/* Remove default touch feedback */
button, a, [role="button"] {
  -webkit-tap-highlight-color: transparent;
  touch-action: manipulation;
}
```
