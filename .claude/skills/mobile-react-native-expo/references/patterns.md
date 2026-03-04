# React Native Expo Code Patterns

Copy-paste patterns for common mobile app needs. All patterns include TypeScript, accessibility, theming, and performance optimization.

## Theme System

### Setup Theme Provider

```tsx
// contexts/ThemeContext.tsx
import React, { createContext, useContext, ReactNode } from 'react';
import { useColorScheme as useRNColorScheme } from 'react-native';
import { Colors } from '@/constants/Colors';

type ColorScheme = 'light' | 'dark';

interface ThemeContextType {
  colorScheme: ColorScheme;
  colors: typeof Colors.light;
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

export function ThemeProvider({ children }: { children: ReactNode }) {
  const systemColorScheme = useRNColorScheme();
  const colorScheme: ColorScheme = systemColorScheme === 'dark' ? 'dark' : 'light';
  const colors = Colors[colorScheme];

  return (
    <ThemeContext.Provider value={{ colorScheme, colors }}>
      {children}
    </ThemeContext.Provider>
  );
}

export function useTheme() {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within ThemeProvider');
  }
  return context;
}
```

### Theme Constants

```tsx
// constants/Colors.ts
export const Colors = {
  light: {
    background: '#FFFFFF',
    surface: '#F5F5F5',
    surfaceVariant: '#E8E8E8',
    text: '#000000',
    textSecondary: '#666666',
    textTertiary: '#999999',
    primary: '#007AFF',
    primaryDark: '#0051D5',
    secondary: '#8E8E93',
    border: '#C6C6C8',
    borderLight: '#E5E5E5',
    error: '#FF3B30',
    errorLight: '#FFE5E5',
    success: '#34C759',
    successLight: '#E5F9E5',
    warning: '#FF9500',
    warningLight: '#FFF3E5',
    info: '#5AC8FA',
    infoLight: '#E5F6FF',
  },
  dark: {
    background: '#000000',
    surface: '#1C1C1E',
    surfaceVariant: '#2C2C2E',
    text: '#FFFFFF',
    textSecondary: '#A0A0A0',
    textTertiary: '#6C6C6C',
    primary: '#0A84FF',
    primaryDark: '#0066CC',
    secondary: '#98989D',
    border: '#38383A',
    borderLight: '#2C2C2E',
    error: '#FF453A',
    errorLight: '#3A1C1C',
    success: '#30D158',
    successLight: '#1C3A1C',
    warning: '#FF9F0A',
    warningLight: '#3A2C1C',
    info: '#64D2FF',
    infoLight: '#1C2C3A',
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
    xxxxl: 32,
  },
  weights: {
    regular: '400' as const,
    medium: '500' as const,
    semibold: '600' as const,
    bold: '700' as const,
  },
  lineHeights: {
    tight: 1.2,
    normal: 1.5,
    relaxed: 1.75,
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

// constants/Shadows.ts (iOS only)
export const Shadows = {
  sm: {
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
  },
  md: {
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.15,
    shadowRadius: 4,
  },
  lg: {
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.2,
    shadowRadius: 8,
  },
};

// constants/Elevation.ts (Android only)
export const Elevation = {
  sm: 2,
  md: 4,
  lg: 8,
  xl: 16,
};
```

## Button Components

### Primary Button with Haptics

```tsx
// components/Button.tsx
import React from 'react';
import {
  TouchableOpacity,
  Text,
  StyleSheet,
  ActivityIndicator,
  ViewStyle,
  TextStyle,
} from 'react-native';
import * as Haptics from 'expo-haptics';
import { useTheme } from '@/contexts/ThemeContext';
import { Spacing, Typography, BorderRadius } from '@/constants';

interface ButtonProps {
  title: string;
  onPress: () => void;
  variant?: 'primary' | 'secondary' | 'tertiary' | 'destructive';
  size?: 'small' | 'medium' | 'large';
  loading?: boolean;
  disabled?: boolean;
  fullWidth?: boolean;
  icon?: React.ReactNode;
  accessibilityLabel?: string;
  accessibilityHint?: string;
  style?: ViewStyle;
  textStyle?: TextStyle;
}

export function Button({
  title,
  onPress,
  variant = 'primary',
  size = 'medium',
  loading = false,
  disabled = false,
  fullWidth = false,
  icon,
  accessibilityLabel,
  accessibilityHint,
  style,
  textStyle,
}: ButtonProps) {
  const { colors } = useTheme();

  const handlePress = () => {
    if (!disabled && !loading) {
      Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);
      onPress();
    }
  };

  const buttonStyle = getButtonStyle(variant, size, colors, fullWidth, disabled);
  const textStyleFinal = getTextStyle(variant, size, colors, disabled);

  return (
    <TouchableOpacity
      onPress={handlePress}
      disabled={disabled || loading}
      accessible={true}
      accessibilityLabel={accessibilityLabel || title}
      accessibilityHint={accessibilityHint}
      accessibilityRole="button"
      accessibilityState={{ disabled: disabled || loading, busy: loading }}
      style={[buttonStyle, style]}
    >
      {loading ? (
        <ActivityIndicator
          color={variant === 'primary' ? colors.background : colors.primary}
        />
      ) : (
        <>
          {icon}
          <Text style={[textStyleFinal, textStyle]}>{title}</Text>
        </>
      )}
    </TouchableOpacity>
  );
}

function getButtonStyle(
  variant: string,
  size: string,
  colors: any,
  fullWidth: boolean,
  disabled: boolean
): ViewStyle {
  const baseStyle: ViewStyle = {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    borderRadius: BorderRadius.md,
    gap: Spacing.sm,
  };

  // Size
  const sizeStyles = {
    small: { paddingVertical: Spacing.sm, paddingHorizontal: Spacing.md, minHeight: 36 },
    medium: { paddingVertical: Spacing.md, paddingHorizontal: Spacing.lg, minHeight: 44 },
    large: { paddingVertical: Spacing.lg, paddingHorizontal: Spacing.xl, minHeight: 56 },
  };

  // Variant
  const variantStyles = {
    primary: {
      backgroundColor: disabled ? colors.border : colors.primary,
    },
    secondary: {
      backgroundColor: 'transparent',
      borderWidth: 1,
      borderColor: disabled ? colors.border : colors.primary,
    },
    tertiary: {
      backgroundColor: 'transparent',
    },
    destructive: {
      backgroundColor: disabled ? colors.border : colors.error,
    },
  };

  return {
    ...baseStyle,
    ...sizeStyles[size as keyof typeof sizeStyles],
    ...variantStyles[variant as keyof typeof variantStyles],
    ...(fullWidth && { width: '100%' }),
    ...(disabled && { opacity: 0.5 }),
  };
}

function getTextStyle(
  variant: string,
  size: string,
  colors: any,
  disabled: boolean
): TextStyle {
  const sizeStyles = {
    small: { fontSize: Typography.sizes.sm },
    medium: { fontSize: Typography.sizes.md },
    large: { fontSize: Typography.sizes.lg },
  };

  const variantStyles = {
    primary: { color: colors.background },
    secondary: { color: disabled ? colors.textSecondary : colors.primary },
    tertiary: { color: disabled ? colors.textSecondary : colors.primary },
    destructive: { color: colors.background },
  };

  return {
    fontWeight: Typography.weights.semibold,
    ...sizeStyles[size as keyof typeof sizeStyles],
    ...variantStyles[variant as keyof typeof variantStyles],
  };
}
```

## Input Components

### Themed Text Input

```tsx
// components/TextInput.tsx
import React, { useState } from 'react';
import {
  TextInput as RNTextInput,
  View,
  Text,
  StyleSheet,
  TextInputProps as RNTextInputProps,
} from 'react-native';
import { useTheme } from '@/contexts/ThemeContext';
import { Spacing, Typography, BorderRadius } from '@/constants';

interface TextInputProps extends RNTextInputProps {
  label?: string;
  error?: string;
  helperText?: string;
  required?: boolean;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
}

export function TextInput({
  label,
  error,
  helperText,
  required,
  leftIcon,
  rightIcon,
  style,
  ...props
}: TextInputProps) {
  const { colors } = useTheme();
  const [isFocused, setIsFocused] = useState(false);

  const borderColor = error
    ? colors.error
    : isFocused
    ? colors.primary
    : colors.border;

  return (
    <View style={styles.container}>
      {label && (
        <Text
          style={[styles.label, { color: colors.text }]}
          accessibilityLabel={`${label}${required ? ', required' : ''}`}
        >
          {label}
          {required && <Text style={{ color: colors.error }}> *</Text>}
        </Text>
      )}
      <View style={[styles.inputContainer, { borderColor, backgroundColor: colors.surface }]}>
        {leftIcon && <View style={styles.icon}>{leftIcon}</View>}
        <RNTextInput
          style={[
            styles.input,
            { color: colors.text },
            style,
          ]}
          placeholderTextColor={colors.textSecondary}
          onFocus={() => setIsFocused(true)}
          onBlur={() => setIsFocused(false)}
          accessible={true}
          accessibilityLabel={label}
          accessibilityHint={helperText}
          accessibilityState={{ disabled: props.editable === false }}
          {...props}
        />
        {rightIcon && <View style={styles.icon}>{rightIcon}</View>}
      </View>
      {error && (
        <Text
          style={[styles.helperText, { color: colors.error }]}
          accessible={true}
          accessibilityLiveRegion="polite"
          accessibilityRole="alert"
        >
          {error}
        </Text>
      )}
      {!error && helperText && (
        <Text style={[styles.helperText, { color: colors.textSecondary }]}>
          {helperText}
        </Text>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    marginBottom: Spacing.md,
  },
  label: {
    fontSize: Typography.sizes.sm,
    fontWeight: Typography.weights.medium,
    marginBottom: Spacing.xs,
  },
  inputContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    borderWidth: 1,
    borderRadius: BorderRadius.md,
    paddingHorizontal: Spacing.md,
    minHeight: 48,
  },
  input: {
    flex: 1,
    fontSize: Typography.sizes.md,
    paddingVertical: Spacing.sm,
  },
  icon: {
    marginHorizontal: Spacing.xs,
  },
  helperText: {
    fontSize: Typography.sizes.xs,
    marginTop: Spacing.xs,
  },
});
```

## Card Component

### Themed Card with Platform Shadows

```tsx
// components/Card.tsx
import React, { ReactNode } from 'react';
import {
  View,
  StyleSheet,
  TouchableOpacity,
  Platform,
  ViewStyle,
} from 'react-native';
import * as Haptics from 'expo-haptics';
import { useTheme } from '@/contexts/ThemeContext';
import { Spacing, BorderRadius, Shadows, Elevation } from '@/constants';

interface CardProps {
  children: ReactNode;
  onPress?: () => void;
  variant?: 'default' | 'outlined' | 'elevated';
  padding?: keyof typeof Spacing;
  style?: ViewStyle;
  accessibilityLabel?: string;
  accessibilityHint?: string;
}

export function Card({
  children,
  onPress,
  variant = 'default',
  padding = 'md',
  style,
  accessibilityLabel,
  accessibilityHint,
}: CardProps) {
  const { colors } = useTheme();

  const cardStyle = getCardStyle(variant, colors);
  const Container = onPress ? TouchableOpacity : View;

  const handlePress = () => {
    if (onPress) {
      Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
      onPress();
    }
  };

  return (
    <Container
      onPress={handlePress}
      accessible={!!onPress}
      accessibilityLabel={accessibilityLabel}
      accessibilityHint={accessibilityHint}
      accessibilityRole={onPress ? 'button' : undefined}
      style={[
        styles.card,
        cardStyle,
        { padding: Spacing[padding] },
        style,
      ]}
    >
      {children}
    </Container>
  );
}

function getCardStyle(variant: string, colors: any): ViewStyle {
  const baseStyle: ViewStyle = {
    backgroundColor: colors.surface,
    borderRadius: BorderRadius.lg,
  };

  switch (variant) {
    case 'outlined':
      return {
        ...baseStyle,
        borderWidth: 1,
        borderColor: colors.border,
      };
    case 'elevated':
      return {
        ...baseStyle,
        ...Platform.select({
          ios: Shadows.md,
          android: { elevation: Elevation.md },
        }),
      };
    default:
      return baseStyle;
  }
}

const styles = StyleSheet.create({
  card: {
    overflow: 'hidden',
  },
});
```

## Loading States

### Skeleton Component

```tsx
// components/Skeleton.tsx
import React, { useEffect } from 'react';
import { View, StyleSheet, ViewStyle } from 'react-native';
import Animated, {
  useSharedValue,
  useAnimatedStyle,
  withRepeat,
  withTiming,
  interpolate,
  useReduceMotion,
} from 'react-native-reanimated';
import { useTheme } from '@/contexts/ThemeContext';
import { BorderRadius } from '@/constants';

interface SkeletonProps {
  width?: number | string;
  height?: number;
  circle?: boolean;
  borderRadius?: keyof typeof BorderRadius;
  style?: ViewStyle;
}

export function Skeleton({
  width = '100%',
  height = 20,
  circle = false,
  borderRadius = 'sm',
  style,
}: SkeletonProps) {
  const { colors } = useTheme();
  const opacity = useSharedValue(0.3);
  const reduceMotion = useReduceMotion();

  useEffect(() => {
    if (!reduceMotion) {
      opacity.value = withRepeat(
        withTiming(1, { duration: 1000 }),
        -1,
        true
      );
    }
  }, [reduceMotion]);

  const animatedStyle = useAnimatedStyle(() => ({
    opacity: reduceMotion ? 0.3 : opacity.value,
  }));

  return (
    <Animated.View
      style={[
        styles.skeleton,
        {
          width: circle ? height : width,
          height,
          borderRadius: circle ? height / 2 : BorderRadius[borderRadius],
          backgroundColor: colors.surfaceVariant,
        },
        animatedStyle,
        style,
      ]}
    />
  );
}

const styles = StyleSheet.create({
  skeleton: {},
});
```

### Skeleton Screen Template

```tsx
// components/SkeletonCard.tsx
import React from 'react';
import { View, StyleSheet } from 'react-native';
import { Skeleton } from './Skeleton';
import { Card } from './Card';
import { Spacing } from '@/constants';

export function SkeletonCard() {
  return (
    <Card padding="md">
      <View style={styles.header}>
        <Skeleton circle width={40} height={40} />
        <View style={styles.headerText}>
          <Skeleton width="60%" height={16} />
          <Skeleton width="40%" height={12} style={{ marginTop: Spacing.xs }} />
        </View>
      </View>
      <Skeleton width="100%" height={120} style={{ marginTop: Spacing.md }} />
      <Skeleton width="80%" height={16} style={{ marginTop: Spacing.md }} />
      <Skeleton width="60%" height={16} style={{ marginTop: Spacing.xs }} />
    </Card>
  );
}

const styles = StyleSheet.create({
  header: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  headerText: {
    marginLeft: Spacing.md,
    flex: 1,
  },
});
```

## Empty States

### Empty State Component

```tsx
// components/EmptyState.tsx
import React, { ReactNode } from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { useTheme } from '@/contexts/ThemeContext';
import { Spacing, Typography } from '@/constants';
import { Button } from './Button';

interface EmptyStateProps {
  icon: ReactNode;
  title: string;
  description?: string;
  action?: {
    label: string;
    onPress: () => void;
  };
}

export function EmptyState({ icon, title, description, action }: EmptyStateProps) {
  const { colors } = useTheme();

  return (
    <View style={styles.container} accessible={true} accessibilityRole="text">
      <View style={styles.icon}>{icon}</View>
      <Text style={[styles.title, { color: colors.text }]}>{title}</Text>
      {description && (
        <Text style={[styles.description, { color: colors.textSecondary }]}>
          {description}
        </Text>
      )}
      {action && (
        <Button
          title={action.label}
          onPress={action.onPress}
          variant="primary"
          style={styles.button}
        />
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: Spacing.xl,
  },
  icon: {
    marginBottom: Spacing.lg,
    opacity: 0.5,
  },
  title: {
    fontSize: Typography.sizes.xl,
    fontWeight: Typography.weights.semibold,
    textAlign: 'center',
    marginBottom: Spacing.sm,
  },
  description: {
    fontSize: Typography.sizes.md,
    textAlign: 'center',
    marginBottom: Spacing.xl,
    lineHeight: Typography.lineHeights.normal * Typography.sizes.md,
  },
  button: {
    marginTop: Spacing.md,
  },
});
```

## Error Handling

### Error Boundary Setup

```tsx
// components/ErrorBoundary.tsx
import React from 'react';
import { ErrorBoundary as ReactErrorBoundary } from 'react-error-boundary';
import { View, Text, StyleSheet } from 'react-native';
import { useTheme } from '@/contexts/ThemeContext';
import { Button } from './Button';
import { Spacing, Typography } from '@/constants';

interface ErrorFallbackProps {
  error: Error;
  resetErrorBoundary: () => void;
}

function ErrorFallback({ error, resetErrorBoundary }: ErrorFallbackProps) {
  const { colors } = useTheme();

  return (
    <View style={[styles.container, { backgroundColor: colors.background }]}>
      <Text style={[styles.title, { color: colors.text }]}>
        Oops! Something went wrong
      </Text>
      <Text style={[styles.message, { color: colors.textSecondary }]}>
        {__DEV__ ? error.message : "We're working on fixing this issue."}
      </Text>
      <Button
        title="Try Again"
        onPress={resetErrorBoundary}
        variant="primary"
      />
    </View>
  );
}

export function ErrorBoundary({ children }: { children: React.ReactNode }) {
  return (
    <ReactErrorBoundary
      FallbackComponent={ErrorFallback}
      onError={(error, errorInfo) => {
        // Log to monitoring service (Sentry, Bugsnag, etc.)
        console.error('Error boundary caught:', error, errorInfo);
      }}
    >
      {children}
    </ReactErrorBoundary>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: Spacing.xl,
  },
  title: {
    fontSize: Typography.sizes.xxl,
    fontWeight: Typography.weights.bold,
    marginBottom: Spacing.md,
    textAlign: 'center',
  },
  message: {
    fontSize: Typography.sizes.md,
    textAlign: 'center',
    marginBottom: Spacing.xl,
    lineHeight: Typography.lineHeights.normal * Typography.sizes.md,
  },
});
```

## Toast System

### Toast with React Native Reanimated

```tsx
// components/Toast.tsx
import React, { useEffect } from 'react';
import { View, Text, StyleSheet, Platform } from 'react-native';
import Animated, {
  useSharedValue,
  useAnimatedStyle,
  withSpring,
  withDelay,
  runOnJS,
  useReduceMotion,
} from 'react-native-reanimated';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { useTheme } from '@/contexts/ThemeContext';
import { Spacing, Typography, BorderRadius, Shadows } from '@/constants';

interface ToastProps {
  message: string;
  type?: 'success' | 'error' | 'info' | 'warning';
  duration?: number;
  onDismiss: () => void;
}

export function Toast({ message, type = 'info', duration = 3000, onDismiss }: ToastProps) {
  const { colors } = useTheme();
  const insets = useSafeAreaInsets();
  const translateY = useSharedValue(100);
  const reduceMotion = useReduceMotion();

  useEffect(() => {
    if (reduceMotion) {
      translateY.value = 0;
    } else {
      translateY.value = withSpring(0, { damping: 15 });
    }

    const timeout = setTimeout(() => {
      if (reduceMotion) {
        translateY.value = 100;
        runOnJS(onDismiss)();
      } else {
        translateY.value = withSpring(100, { damping: 15 }, () => {
          runOnJS(onDismiss)();
        });
      }
    }, duration);

    return () => clearTimeout(timeout);
  }, [duration, onDismiss, reduceMotion]);

  const animatedStyle = useAnimatedStyle(() => ({
    transform: [{ translateY: translateY.value }],
  }));

  const backgroundColor = {
    success: colors.success,
    error: colors.error,
    warning: colors.warning,
    info: colors.info,
  }[type];

  return (
    <Animated.View
      style={[
        styles.container,
        {
          bottom: insets.bottom + Spacing.md,
          backgroundColor,
        },
        Platform.OS === 'ios' && Shadows.lg,
        animatedStyle,
      ]}
      accessible={true}
      accessibilityLiveRegion="polite"
      accessibilityRole="alert"
    >
      <Text style={styles.message}>{message}</Text>
    </Animated.View>
  );
}

const styles = StyleSheet.create({
  container: {
    position: 'absolute',
    left: Spacing.md,
    right: Spacing.md,
    paddingVertical: Spacing.md,
    paddingHorizontal: Spacing.lg,
    borderRadius: BorderRadius.lg,
    ...Platform.select({
      android: { elevation: 8 },
    }),
  },
  message: {
    color: '#FFFFFF',
    fontSize: Typography.sizes.md,
    fontWeight: Typography.weights.medium,
    textAlign: 'center',
  },
});
```

### Toast Manager

```tsx
// contexts/ToastContext.tsx
import React, { createContext, useContext, useState, ReactNode } from 'react';
import { Toast } from '@/components/Toast';

interface ToastOptions {
  message: string;
  type?: 'success' | 'error' | 'info' | 'warning';
  duration?: number;
}

interface ToastContextType {
  showToast: (options: ToastOptions) => void;
}

const ToastContext = createContext<ToastContextType | undefined>(undefined);

export function ToastProvider({ children }: { children: ReactNode }) {
  const [toast, setToast] = useState<ToastOptions | null>(null);

  const showToast = (options: ToastOptions) => {
    setToast(options);
  };

  return (
    <ToastContext.Provider value={{ showToast }}>
      {children}
      {toast && (
        <Toast
          message={toast.message}
          type={toast.type}
          duration={toast.duration}
          onDismiss={() => setToast(null)}
        />
      )}
    </ToastContext.Provider>
  );
}

export function useToast() {
  const context = useContext(ToastContext);
  if (!context) {
    throw new Error('useToast must be used within ToastProvider');
  }
  return context;
}

// Usage:
// const { showToast } = useToast();
// showToast({ message: 'Saved!', type: 'success' });
```

## Performance Patterns

### Optimized FlatList

```tsx
// components/OptimizedList.tsx
import React, { useCallback } from 'react';
import { FlatList, FlatListProps, ListRenderItem } from 'react-native';

interface OptimizedListProps<T> extends Omit<FlatListProps<T>, 'renderItem'> {
  data: T[];
  renderItem: ListRenderItem<T>;
  itemHeight?: number;
}

export function OptimizedList<T extends { id: string }>({
  data,
  renderItem,
  itemHeight,
  ...props
}: OptimizedListProps<T>) {
  const keyExtractor = useCallback((item: T) => item.id, []);

  const getItemLayout = itemHeight
    ? (_: any, index: number) => ({
        length: itemHeight,
        offset: itemHeight * index,
        index,
      })
    : undefined;

  return (
    <FlatList
      data={data}
      renderItem={renderItem}
      keyExtractor={keyExtractor}
      removeClippedSubviews={true}
      maxToRenderPerBatch={10}
      windowSize={10}
      initialNumToRender={10}
      updateCellsBatchingPeriod={50}
      getItemLayout={getItemLayout}
      {...props}
    />
  );
}
```

### Memoized List Item

```tsx
// components/ListItem.tsx
import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';
import * as Haptics from 'expo-haptics';
import { useTheme } from '@/contexts/ThemeContext';
import { Spacing, Typography } from '@/constants';

interface ListItemProps {
  title: string;
  subtitle?: string;
  onPress?: () => void;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
}

export const ListItem = React.memo(
  ({ title, subtitle, onPress, leftIcon, rightIcon }: ListItemProps) => {
    const { colors } = useTheme();

    const handlePress = () => {
      if (onPress) {
        Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
        onPress();
      }
    };

    return (
      <TouchableOpacity
        onPress={handlePress}
        disabled={!onPress}
        accessible={true}
        accessibilityLabel={`${title}${subtitle ? `, ${subtitle}` : ''}`}
        accessibilityRole="button"
        style={[styles.container, { backgroundColor: colors.surface }]}
      >
        {leftIcon && <View style={styles.leftIcon}>{leftIcon}</View>}
        <View style={styles.content}>
          <Text style={[styles.title, { color: colors.text }]}>{title}</Text>
          {subtitle && (
            <Text style={[styles.subtitle, { color: colors.textSecondary }]}>
              {subtitle}
            </Text>
          )}
        </View>
        {rightIcon && <View style={styles.rightIcon}>{rightIcon}</View>}
      </TouchableOpacity>
    );
  },
  (prev, next) => {
    return (
      prev.title === next.title &&
      prev.subtitle === next.subtitle &&
      prev.onPress === next.onPress
    );
  }
);

const styles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: Spacing.md,
    paddingHorizontal: Spacing.lg,
    minHeight: 60,
  },
  leftIcon: {
    marginRight: Spacing.md,
  },
  content: {
    flex: 1,
  },
  title: {
    fontSize: Typography.sizes.md,
    fontWeight: Typography.weights.medium,
  },
  subtitle: {
    fontSize: Typography.sizes.sm,
    marginTop: Spacing.xs,
  },
  rightIcon: {
    marginLeft: Spacing.md,
  },
});
```

## Safe Area Handling

### Screen Container with Safe Areas

```tsx
// components/ScreenContainer.tsx
import React, { ReactNode } from 'react';
import { View, StyleSheet, ScrollView, ViewStyle } from 'react-native';
import { SafeAreaView, Edge } from 'react-native-safe-area-context';
import { useTheme } from '@/contexts/ThemeContext';

interface ScreenContainerProps {
  children: ReactNode;
  edges?: Edge[];
  scrollable?: boolean;
  style?: ViewStyle;
}

export function ScreenContainer({
  children,
  edges = ['top', 'left', 'right'],
  scrollable = false,
  style,
}: ScreenContainerProps) {
  const { colors } = useTheme();

  const Container = scrollable ? ScrollView : View;

  return (
    <SafeAreaView
      edges={edges}
      style={[styles.safeArea, { backgroundColor: colors.background }]}
    >
      <Container
        style={[styles.container, style]}
        contentContainerStyle={scrollable ? styles.scrollContent : undefined}
      >
        {children}
      </Container>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
  },
  container: {
    flex: 1,
  },
  scrollContent: {
    flexGrow: 1,
  },
});
```

## Haptic Utilities

### Centralized Haptic Feedback

```tsx
// utils/haptics.ts
import * as Haptics from 'expo-haptics';
import { Platform } from 'react-native';

class HapticService {
  private enabled = true;

  enable() {
    this.enabled = true;
  }

  disable() {
    this.enabled = false;
  }

  private trigger(feedback: () => void) {
    if (Platform.OS === 'ios' && this.enabled) {
      feedback();
    }
  }

  light() {
    this.trigger(() =>
      Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light)
    );
  }

  medium() {
    this.trigger(() =>
      Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium)
    );
  }

  heavy() {
    this.trigger(() =>
      Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Heavy)
    );
  }

  success() {
    this.trigger(() =>
      Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success)
    );
  }

  error() {
    this.trigger(() =>
      Haptics.notificationAsync(Haptics.NotificationFeedbackType.Error)
    );
  }

  warning() {
    this.trigger(() =>
      Haptics.notificationAsync(Haptics.NotificationFeedbackType.Warning)
    );
  }

  selection() {
    this.trigger(() => Haptics.selectionAsync());
  }
}

export const HapticFeedback = new HapticService();

// Usage:
// import { HapticFeedback } from '@/utils/haptics';
// HapticFeedback.medium(); // On button press
// HapticFeedback.success(); // On successful action
```

## All Patterns Applied

### Complete Screen Example

```tsx
// screens/ExampleScreen.tsx
import React, { useState } from 'react';
import { View, StyleSheet } from 'react-native';
import { ScreenContainer } from '@/components/ScreenContainer';
import { Button } from '@/components/Button';
import { TextInput } from '@/components/TextInput';
import { Card } from '@/components/Card';
import { OptimizedList } from '@/components/OptimizedList';
import { ListItem } from '@/components/ListItem';
import { EmptyState } from '@/components/EmptyState';
import { useToast } from '@/contexts/ToastContext';
import { Spacing } from '@/constants';
import { MaterialIcons } from '@expo/vector-icons';

export function ExampleScreen() {
  const [items, setItems] = useState([]);
  const { showToast } = useToast();

  const handleSubmit = () => {
    showToast({ message: 'Saved successfully!', type: 'success' });
  };

  return (
    <ScreenContainer scrollable edges={['top', 'left', 'right']}>
      <Card padding="lg" style={styles.card}>
        <TextInput
          label="Email"
          placeholder="Enter your email"
          keyboardType="email-address"
          autoCapitalize="none"
          required
          accessibilityLabel="Email address"
          accessibilityHint="Enter your email to continue"
        />
        <Button
          title="Submit"
          onPress={handleSubmit}
          variant="primary"
          fullWidth
        />
      </Card>

      <OptimizedList
        data={items}
        renderItem={({ item }) => (
          <ListItem
            title={item.title}
            subtitle={item.subtitle}
            onPress={() => console.log('Tapped', item.id)}
            rightIcon={<MaterialIcons name="chevron-right" size={24} />}
          />
        )}
        ListEmptyComponent={
          <EmptyState
            icon={<MaterialIcons name="inbox" size={64} color="#999" />}
            title="No items yet"
            description="Items will appear here once you add them."
          />
        }
      />
    </ScreenContainer>
  );
}

const styles = StyleSheet.create({
  card: {
    margin: Spacing.md,
  },
});
```
