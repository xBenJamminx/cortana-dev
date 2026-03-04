# React Native Expo Technical Checklist

Run through this checklist when auditing React Native/Expo code for technical issues.

## Priority 1: Critical Issues (Breaks Accessibility/UX)

These make the app unusable for many users or cause crashes.

### Accessibility

- [ ] **All interactive elements have `accessibilityLabel`** (buttons, links, cards, tabs)
  ```tsx
  <TouchableOpacity accessibilityLabel="Add to cart">
  ```
- [ ] **All interactive elements have `accessibilityRole`** (button, link, tab, etc.)
  ```tsx
  <TouchableOpacity accessibilityRole="button">
  ```
- [ ] **Images have `accessibilityLabel`** (decorative images can be empty)
  ```tsx
  <Image accessibilityLabel="Product photo" />
  <Image accessibilityLabel="" /> {/* Decorative */}
  ```
- [ ] **Form inputs have labels and hints**
  ```tsx
  <TextInput
    accessibilityLabel="Email address"
    accessibilityHint="Enter your email to sign in"
  />
  ```
- [ ] **Dynamic content announces changes** (loading states, errors)
  ```tsx
  <View accessible={true} accessibilityLiveRegion="polite">
    <Text>{statusMessage}</Text>
  </View>
  ```
- [ ] **Disabled states are communicated**
  ```tsx
  <Button accessibilityState={{ disabled: true }} />
  ```

**Grep commands:**
```bash
# Find Touchables without accessibilityLabel
grep -r "Touchable\|Pressable" --include="*.tsx" src/ | grep -v "accessibilityLabel"

# Find Images without accessibilityLabel  
grep -r "<Image" --include="*.tsx" src/ | grep -v "accessibilityLabel"

# Find TextInput without labels
grep -r "TextInput" --include="*.tsx" src/ | grep -v "accessibilityLabel"
```

### Dark Mode Implementation

- [ ] **All colors use theme system** (no hardcoded hex colors)
  ```tsx
  // Bad
  style={{ backgroundColor: '#FFFFFF' }}
  
  // Good
  const colorScheme = useColorScheme();
  const colors = Colors[colorScheme ?? 'light'];
  style={{ backgroundColor: colors.background }}
  ```
- [ ] **`Colors.dark` is actually used** (not just defined)
- [ ] **useColorScheme() hook used** throughout app
- [ ] **StatusBar adapts to theme**
  ```tsx
  <StatusBar barStyle={colorScheme === 'dark' ? 'light-content' : 'dark-content'} />
  ```
- [ ] **Images have dark mode variants** if needed
  ```tsx
  const logo = colorScheme === 'dark' ? logoDark : logoLight;
  ```

**Grep commands:**
```bash
# Find hardcoded colors
grep -rE "#[0-9A-Fa-f]{6}|#[0-9A-Fa-f]{3}" --include="*.tsx" --include="*.ts" src/

# Find 'white'/'black' strings  
grep -rE "'(white|black|#fff|#000)'" --include="*.tsx" src/

# Check if Colors.dark is used
grep -r "Colors\.dark\|Colors\[.*dark" --include="*.tsx" src/
```

### Error Boundaries

- [ ] **Global error boundary wraps app** (`react-error-boundary`)
- [ ] **Error fallback is user-friendly** (not technical stack trace)
- [ ] **Error boundary around async operations** (data fetching)
- [ ] **Errors logged to monitoring service** (Sentry, Bugsnag)

**Implementation:**
```tsx
import { ErrorBoundary } from 'react-error-boundary';

function ErrorFallback({ error, resetErrorBoundary }) {
  return (
    <View style={styles.container}>
      <Text style={styles.title}>Oops! Something went wrong</Text>
      <Text style={styles.message}>
        {__DEV__ ? error.message : "We're working on fixing this."}
      </Text>
      <Button title="Try Again" onPress={resetErrorBoundary} />
    </View>
  );
}

// In App.tsx
<ErrorBoundary
  FallbackComponent={ErrorFallback}
  onError={(error, errorInfo) => {
    // Log to monitoring service
    console.error('Error boundary caught:', error, errorInfo);
  }}
>
  <AppNavigator />
</ErrorBoundary>
```

## Priority 2: Polish Issues (Affects UX Quality)

These make the app feel unpolished or non-native.

### Loading States

- [ ] **Skeleton screens used instead of spinners** (for content-shaped placeholders)
  ```tsx
  // Use library like @rneui/themed or build custom
  <Skeleton circle width={40} height={40} />
  <Skeleton width="80%" height={20} style={{ marginTop: 8 }} />
  ```
- [ ] **ActivityIndicator only for quick operations** (<2 seconds)
- [ ] **Skeleton screens match content layout** (cards, lists, text blocks)
- [ ] **Loading state doesn't cause layout shift**

**Implementation:**
```tsx
// Custom skeleton
function Skeleton({ width, height, borderRadius = 4, style }) {
  const opacity = useSharedValue(0.3);
  
  useEffect(() => {
    opacity.value = withRepeat(
      withTiming(1, { duration: 1000 }),
      -1,
      true
    );
  }, []);
  
  return (
    <Animated.View
      style={[
        {
          width,
          height,
          borderRadius,
          backgroundColor: '#E0E0E0',
          opacity,
        },
        style,
      ]}
    />
  );
}
```

### Empty States

- [ ] **All lists/feeds have empty states** (not blank screen)
- [ ] **Empty state has illustration/icon**
- [ ] **Empty state has helpful message**
- [ ] **Empty state has primary action** (if applicable)
- [ ] **EmptyState component used consistently**

**Template:**
```tsx
<EmptyState
  icon={<MaterialIcons name="inbox" size={64} color="#999" />}
  title="No messages yet"
  description="When someone sends you a message, it will appear here."
  action={<Button title="Invite Friends" onPress={handleInvite} />}
/>
```

**Grep command:**
```bash
# Find FlatList without ListEmptyComponent
grep -r "FlatList" --include="*.tsx" src/ | grep -v "ListEmptyComponent"
```

### Haptic Feedback

- [ ] **All buttons have haptic feedback**
  ```tsx
  import * as Haptics from 'expo-haptics';
  
  <Button
    onPress={() => {
      Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);
      handlePress();
    }}
  />
  ```
- [ ] **Haptic intensity matches action importance**
  - Light: Navigation, selection, tab switch
  - Medium: Button press, toggle, form submit
  - Heavy: Delete, error, important action
- [ ] **Success/error use notification haptics**
  ```tsx
  Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
  Haptics.notificationAsync(Haptics.NotificationFeedbackType.Error);
  ```
- [ ] **Haptics can be disabled** (user preference)

**Centralized haptic utility:**
```tsx
// utils/haptics.ts
import * as Haptics from 'expo-haptics';
import { Platform } from 'react-native';

let hapticsEnabled = true;

export const HapticFeedback = {
  enable: () => { hapticsEnabled = true; },
  disable: () => { hapticsEnabled = false; },
  
  light: () => {
    if (Platform.OS === 'ios' && hapticsEnabled) {
      Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
    }
  },
  
  medium: () => {
    if (Platform.OS === 'ios' && hapticsEnabled) {
      Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);
    }
  },
  
  heavy: () => {
    if (Platform.OS === 'ios' && hapticsEnabled) {
      Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Heavy);
    }
  },
  
  success: () => {
    if (Platform.OS === 'ios' && hapticsEnabled) {
      Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
    }
  },
  
  error: () => {
    if (Platform.OS === 'ios' && hapticsEnabled) {
      Haptics.notificationAsync(Haptics.NotificationFeedbackType.Error);
    }
  },
};
```

### Toast/Snackbar System

- [ ] **Toast component exists** (not using `Alert.alert()` for feedback)
- [ ] **Toast shows at bottom** (above navigation, thumb-reachable)
- [ ] **Toast auto-dismisses** (3-5 seconds)
- [ ] **Toast is accessible** (screen reader announces)
- [ ] **Toast doesn't block interaction** (non-modal)

**Implementation options:**
- Use library: `react-native-toast-message`, `react-native-paper` Snackbar
- Build custom with React Native Reanimated

**Toast vs Alert decision:**
```typescript
// Use Toast for:
- Success messages ("Saved!", "Item added")
- Info messages ("New version available")
- Non-critical errors ("Network timeout")

// Use Alert for:
- Confirmations ("Delete this item?")
- Critical errors ("Payment failed")
- Permissions requests
```

**Grep command:**
```bash
# Find Alert.alert usage (should be replaced with Toast)
grep -r "Alert\.alert" --include="*.tsx" src/
```

### Reduced Motion Support

- [ ] **Animations check `useReduceMotion()`**
  ```tsx
  import { useReduceMotion } from 'react-native-reanimated';
  
  const reduceMotion = useReduceMotion();
  const duration = reduceMotion ? 0 : 300;
  ```
- [ ] **Critical animations still show state change** (instant, no motion)
- [ ] **Non-critical animations are skipped entirely**

**Reanimated support:**
```tsx
const fadeIn = useAnimatedStyle(() => {
  const reduceMotion = useReduceMotion();
  
  return {
    opacity: reduceMotion 
      ? 1  // Instant appearance
      : withTiming(opacity.value, { duration: 300 }),
  };
});
```

## Priority 3: Code Quality Issues (Technical Debt)

These indicate maintainability problems and inconsistency.

### Design Tokens & Theming

- [ ] **No hardcoded colors** (all use `Colors.*`)
- [ ] **No magic numbers** (all spacing uses `Spacing.*`)
- [ ] **Consistent component usage** (use `Card` component, not inline styles)
- [ ] **Font sizes use typography scale**
- [ ] **Border radius uses design tokens**
- [ ] **Shadow/elevation uses design tokens**

**Design tokens structure:**
```typescript
// constants/Colors.ts
export const Colors = {
  light: {
    background: '#FFFFFF',
    surface: '#F5F5F5',
    text: '#000000',
    textSecondary: '#666666',
    primary: '#007AFF',
    primaryDark: '#0051D5',
    secondary: '#8E8E93',
    border: '#C6C6C8',
    error: '#FF3B30',
    success: '#34C759',
    warning: '#FF9500',
  },
  dark: {
    background: '#000000',
    surface: '#1C1C1E',
    text: '#FFFFFF',
    textSecondary: '#A0A0A0',
    primary: '#0A84FF',
    primaryDark: '#0066CC',
    secondary: '#98989D',
    border: '#38383A',
    error: '#FF453A',
    success: '#30D158',
    warning: '#FF9F0A',
  },
};

// constants/Spacing.ts
export const Spacing = {
  xs: 4,
  sm: 8,
  md: 16,
  lg: 24,
  xl: 32,
  xxl: 48,
};

// constants/Typography.ts
export const Typography = {
  sizes: {
    xs: 12,
    sm: 14,
    md: 16,
    lg: 18,
    xl: 20,
    xxl: 24,
    xxxl: 28,
  },
  weights: {
    regular: '400',
    medium: '500',
    semibold: '600',
    bold: '700',
  },
};

// constants/BorderRadius.ts
export const BorderRadius = {
  sm: 4,
  md: 8,
  lg: 12,
  xl: 16,
  full: 9999,
};
```

**Grep commands:**
```bash
# Find hardcoded colors
grep -rE "#[0-9A-Fa-f]{6}" --include="*.tsx" src/

# Find magic numbers in styles
grep -rE "(margin|padding|gap|fontSize):\s*[0-9]+" --include="*.tsx" src/ | grep -v "Spacing\|Typography\|BorderRadius"

# Find hardcoded border radius
grep -rE "borderRadius:\s*[0-9]+" --include="*.tsx" src/ | grep -v "BorderRadius"
```

### Performance Optimization

- [ ] **FlatList used instead of ScrollView + map** (for lists >10 items)
- [ ] **List items memoized** (`React.memo`)
- [ ] **Expensive calculations memoized** (`useMemo`)
- [ ] **Callbacks memoized** (`useCallback`)
- [ ] **Images optimized** (compressed, correct resolution)
- [ ] **Large images lazy loaded** (`expo-image` with lazy loading)
- [ ] **Unnecessary re-renders prevented** (use React DevTools Profiler)

**FlatList optimization:**
```tsx
<FlatList
  data={items}
  renderItem={({ item }) => <MemoizedItemCard item={item} />}
  keyExtractor={(item) => item.id}
  // Performance props
  removeClippedSubviews={true}
  maxToRenderPerBatch={10}
  windowSize={10}
  initialNumToRender={10}
  updateCellsBatchingPeriod={50}
  getItemLayout={(data, index) => ({
    length: ITEM_HEIGHT,
    offset: ITEM_HEIGHT * index,
    index,
  })}
/>

const MemoizedItemCard = React.memo(ItemCard, (prev, next) => {
  return prev.item.id === next.item.id;
});
```

**Grep commands:**
```bash
# Find ScrollView with map (should be FlatList)
grep -r "ScrollView" --include="*.tsx" src/ -A 5 | grep "\.map("

# Find components that could be memoized
grep -r "function.*Component\|const.*Component.*=.*(" --include="*.tsx" src/ | grep -v "memo"
```

### Navigation Patterns

- [ ] **Stack navigation for hierarchical flow** (drill-down)
- [ ] **Tab navigation for main sections** (3-5 tabs)
- [ ] **Drawer navigation for many sections** (5+ sections)
- [ ] **Modal navigation for temporary tasks**
- [ ] **Header back button always works**
- [ ] **Navigation state persisted** (user returns to same screen)

### Safe Areas

- [ ] **SafeAreaView from `react-native-safe-area-context`** (not RN core)
- [ ] **Safe area respected on all screens**
- [ ] **Modals respect safe area**
- [ ] **Edges specified appropriately**
  ```tsx
  <SafeAreaView edges={['top', 'left', 'right']}> // Not bottom (keyboard)
  ```

## Code Review Checklist

When reviewing pull requests, check for:

- [ ] All new interactive elements have accessibility labels
- [ ] All new colors use theme system (no hex codes)
- [ ] All new spacing uses `Spacing.*` tokens
- [ ] Loading states use skeletons (not spinners)
- [ ] Haptic feedback added to new buttons
- [ ] Empty states implemented for new lists
- [ ] Error boundaries wrap new async operations
- [ ] New animations respect reduced motion
- [ ] Platform-specific code uses `Platform.select()`
- [ ] Images have proper `resizeMode` and caching

## Automated Checks

Consider adding these to your CI/CD:

**ESLint rules:**
```json
{
  "rules": {
    "react-native/no-inline-styles": "error",
    "react-native/no-color-literals": "error",
    "react-native/no-raw-text": "warn"
  }
}
```

**TypeScript strict mode:**
```json
{
  "compilerOptions": {
    "strict": true,
    "noImplicitAny": true,
    "strictNullChecks": true
  }
}
```

**Pre-commit hooks:**
```bash
# Run before every commit
- ESLint with auto-fix
- TypeScript type checking
- Grep for hardcoded colors
- Grep for missing accessibility labels
```

## Migration Guide

If you have existing code with these issues:

### 1. Add Accessibility (1-2 days)
- Create script to find all Touchables
- Add `accessibilityLabel` and `accessibilityRole` to each
- Test with screen reader (iOS VoiceOver, Android TalkBack)

### 2. Implement Dark Mode (2-3 days)
- Create `Colors` constant with light/dark
- Find/replace all hex colors with theme references
- Add `useColorScheme()` hook to all screens
- Test in both modes

### 3. Replace Spinners with Skeletons (1 day)
- Create `Skeleton` component
- Replace `ActivityIndicator` in long-loading screens
- Keep spinners only for quick operations

### 4. Add Error Boundaries (1 day)
- Install `react-error-boundary`
- Wrap app in global boundary
- Add boundaries around data-fetching components
- Implement error logging

### 5. Centralize Haptics (1 day)
- Create `HapticFeedback` utility
- Add to all button components
- Add preference toggle in settings

### 6. Build Toast System (1 day)
- Install `react-native-toast-message` or build custom
- Replace `Alert.alert()` for non-critical feedback
- Keep alerts only for confirmations

### 7. Clean Up Design Tokens (2-3 days)
- Create `Spacing`, `Typography`, `BorderRadius` constants
- Find/replace magic numbers
- Enforce via ESLint

Priority order: Accessibility → Dark Mode → Error Boundaries → Haptics → Loading States → Design Tokens
