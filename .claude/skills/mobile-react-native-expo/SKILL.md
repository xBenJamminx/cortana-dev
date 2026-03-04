---
name: mobile-react-native-expo
description: Optimize React Native Expo apps for iOS and Android. Use when working on React Native/Expo mobile apps to audit code quality, implement accessibility, optimize performance, and ensure native-feeling UX. Covers technical implementation (accessibility APIs, performance patterns, platform-specific features, theme systems) and design considerations (typography, spacing, component patterns, navigation). For React/Next.js web apps, use the mobile-react-web skill instead.
---

# Mobile React Native Expo Optimization

Make React Native/Expo apps accessible, performant, and platform-appropriate.

## Core Philosophy

Native mobile apps succeed when they:

**Technical Excellence:**
1. **Accessibility** - Screen readers work perfectly, keyboard navigation supported
2. **Performance** - 60fps animations, instant interactions, minimal re-renders
3. **Platform Integration** - Use native APIs (haptics, sensors, permissions) appropriately

**Design & UX:**
4. **Platform Conventions** - Follow iOS and Android design patterns
5. **Feedback** - Loading states, error handling, haptics are consistent
6. **Theming** - Dark mode, system settings respected

## Workflow

### 1. Technical Audit Mode
Run through `references/checklist.md` to find code quality issues:
- Missing accessibility labels
- Hardcoded colors and spacing
- Performance anti-patterns
- Missing error boundaries
- Inconsistent haptic feedback

### 2. Design Audit Mode
Run through `references/design-checklist.md` for UX patterns:
- Typography and spacing consistency
- Component composition
- Loading and empty states
- Navigation patterns
- Platform-appropriate design

### 3. Build Mode
Apply patterns from `references/patterns.md` when building new features:
- Accessible components
- Themed styling
- Performance-optimized lists
- Error boundaries
- Consistent feedback patterns

### 4. Platform-Specific Mode
Check `references/platform-patterns.md` for iOS vs Android differences:
- Navigation patterns (tabs, drawers, headers)
- Gesture handling
- System integration
- Design conventions

## Quick Reference

### Accessibility Essentials

**Every interactive element needs:**
```tsx
<TouchableOpacity
  accessible={true}
  accessibilityLabel="Add to cart"
  accessibilityRole="button"
  accessibilityState={{ disabled: false }}
  accessibilityHint="Adds this item to your shopping cart"
>
  <Text>Add to Cart</Text>
</TouchableOpacity>
```

**Image accessibility:**
```tsx
<Image 
  source={avatar}
  accessible={true}
  accessibilityLabel="Profile picture"
/>
```

**Reduce motion:**
```tsx
import { useReduceMotion } from 'react-native-reanimated';

const reduceMotion = useReduceMotion();
const animationDuration = reduceMotion ? 0 : 300;
```

### Theme System Essentials

**Never hardcode colors:**
```tsx
// Bad
<View style={{ backgroundColor: '#FFFFFF' }}>

// Good
<View style={{ backgroundColor: Colors.light.background }}>

// Best (respects dark mode)
const colorScheme = useColorScheme();
const colors = Colors[colorScheme ?? 'light'];
<View style={{ backgroundColor: colors.background }}>
```

**Design tokens structure:**
```typescript
// colors.ts
export const Colors = {
  light: {
    background: '#FFFFFF',
    text: '#000000',
    primary: '#007AFF',
    secondary: '#8E8E93',
    border: '#C6C6C8',
  },
  dark: {
    background: '#000000',
    text: '#FFFFFF',
    primary: '#0A84FF',
    secondary: '#98989D',
    border: '#38383A',
  },
};

// spacing.ts
export const Spacing = {
  xs: 4,
  sm: 8,
  md: 16,
  lg: 24,
  xl: 32,
  xxl: 48,
};
```

### Performance Essentials

**Lists:**
```tsx
// Use FlatList, not ScrollView + map
<FlatList
  data={items}
  renderItem={({ item }) => <ItemCard item={item} />}
  keyExtractor={(item) => item.id}
  removeClippedSubviews={true}
  maxToRenderPerBatch={10}
  windowSize={10}
  initialNumToRender={10}
/>
```

**Memoization:**
```tsx
// Expensive component
const ItemCard = React.memo(({ item }) => {
  return <View>...</View>;
});

// Expensive calculation
const sortedItems = useMemo(() => {
  return items.sort((a, b) => a.date - b.date);
}, [items]);
```

**Image optimization:**
```tsx
<Image
  source={{ uri: imageUrl }}
  style={styles.image}
  resizeMode="cover"
  // Expo-specific optimization
  cachePolicy="memory-disk"
  priority="high"
/>
```

### Haptics Essentials

**Consistent haptic feedback:**
```tsx
import * as Haptics from 'expo-haptics';

// Light tap (navigation, selection)
Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);

// Medium tap (buttons, toggles)
Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);

// Heavy tap (important actions, errors)
Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Heavy);

// Success feedback
Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);

// Error feedback
Haptics.notificationAsync(Haptics.NotificationFeedbackType.Error);
```

### Loading States Essentials

**Skeleton screens (not spinners):**
```tsx
import { Skeleton } from '@rneui/themed'; // or build custom

// Good - content-shaped placeholder
<View>
  <Skeleton circle width={40} height={40} />
  <Skeleton width="80%" height={20} style={{ marginTop: 8 }} />
  <Skeleton width="60%" height={16} style={{ marginTop: 4 }} />
</View>

// Avoid - generic spinner
<ActivityIndicator /> // Only for small, quick operations
```

### Error Handling Essentials

**Global error boundary:**
```tsx
import { ErrorBoundary } from 'react-error-boundary';

function ErrorFallback({ error, resetErrorBoundary }) {
  return (
    <View style={styles.errorContainer}>
      <Text style={styles.errorTitle}>Something went wrong</Text>
      <Text style={styles.errorMessage}>{error.message}</Text>
      <Button onPress={resetErrorBoundary}>Try Again</Button>
    </View>
  );
}

// Wrap your app
<ErrorBoundary FallbackComponent={ErrorFallback}>
  <App />
</ErrorBoundary>
```

### Platform-Specific Essentials

**Detect and adapt:**
```tsx
import { Platform } from 'react-native';

const styles = StyleSheet.create({
  container: {
    ...Platform.select({
      ios: {
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 2 },
        shadowOpacity: 0.1,
        shadowRadius: 4,
      },
      android: {
        elevation: 4,
      },
    }),
  },
});
```

**Safe areas:**
```tsx
import { SafeAreaView } from 'react-native-safe-area-context';

<SafeAreaView style={styles.container} edges={['top', 'left', 'right']}>
  <ScrollView>
    {/* Content */}
  </ScrollView>
</SafeAreaView>
```

## Common Anti-Patterns

### Code Quality Issues

| Anti-Pattern | Problem | Solution |
|--------------|---------|----------|
| Hardcoded colors (`#FFFFFF`) | Breaks dark mode, inconsistent | Use theme system (`Colors[colorScheme].background`) |
| Magic numbers (`marginTop: 12`) | Inconsistent spacing | Use spacing tokens (`Spacing.md`) |
| Missing accessibility labels | Screen readers can't navigate | Add `accessibilityLabel` to all interactive elements |
| `ScrollView` + `.map()` | Poor performance on long lists | Use `FlatList` with virtualization |
| No error boundaries | App crashes show white screen | Wrap components in `ErrorBoundary` |
| Generic loading (spinner only) | Jarring layout shift | Use skeleton screens |
| Inconsistent haptics | Some buttons vibrate, others don't | Centralize haptic feedback in components |

### Design Issues

| Anti-Pattern | Problem | Solution |
|--------------|---------|----------|
| Ignoring reduced motion | Causes motion sickness | Check `useReduceMotion()`, disable animations |
| No empty states | Users see blank screens | Add illustrations + helpful messages |
| Alert for all feedback | Disruptive, not native-feeling | Use toast/snackbar for non-critical feedback |
| Same design on iOS/Android | Feels foreign on both platforms | Adapt navigation, gestures, visual style |
| Tiny touch targets (<44px) | Hard to tap accurately | Minimum 44x44px for all interactive elements |

## File References

**Technical Implementation:**
- **`references/checklist.md`** - Code quality audit (accessibility, performance, theme system, error handling)
- **`references/patterns.md`** - Copy-paste React Native/Expo patterns
- **`references/platform-patterns.md`** - iOS vs Android specific patterns

**Design & UX:**
- **`references/design-checklist.md`** - Design audit adapted for React Native (typography, spacing, component patterns, navigation)

## Quick Audit Commands

Find common issues in your codebase:

```bash
# Find hardcoded colors (should use theme)
grep -r "#[0-9A-Fa-f]\{6\}" --include="*.tsx" --include="*.ts" src/

# Find magic numbers (should use spacing tokens)
grep -rE "(margin|padding|gap|top|left|right|bottom):\s*[0-9]+" --include="*.tsx" src/

# Find missing accessibility labels (interactive without labels)
grep -r "Touchable\|Pressable" --include="*.tsx" src/ | grep -v "accessibilityLabel"

# Find ActivityIndicator usage (prefer skeletons)
grep -r "ActivityIndicator" --include="*.tsx" src/

# Find Alert.alert usage (prefer toast)
grep -r "Alert\.alert" --include="*.tsx" src/
```

## Integration Notes

This skill focuses on React Native/Expo specifics. The design principles (typography, spacing, color contrast, component composition, animation, information architecture) from `references/design-checklist.md` apply to both web and native - only the implementation differs.

For web-specific mobile optimization (viewport units, touch-action, momentum scrolling, keyboard handling), use the `mobile-react-web` skill instead.
