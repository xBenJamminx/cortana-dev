# Platform-Specific Patterns: iOS vs Android

React Native/Expo apps should respect platform conventions to feel native on both iOS and Android.

## Detection and Conditional Code

### Platform Detection

```tsx
import { Platform } from 'react-native';

// Check platform
if (Platform.OS === 'ios') {
  // iOS-specific code
}

if (Platform.OS === 'android') {
  // Android-specific code
}

// Platform version
if (Platform.Version >= 29) {
  // Android API 29+ or iOS 13+
}
```

### Platform.select()

```tsx
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

// Or for values
const fontSize = Platform.select({
  ios: 17,
  android: 16,
});
```

## Navigation Patterns

### iOS Navigation

**Tab Bar (Bottom Navigation)**
- Position: Bottom of screen
- Items: 3-5 tabs
- Active indicator: Tinted icon + label
- Height: 49pt (iOS standard)
- Safe area: Respects home indicator

```tsx
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';

const Tab = createBottomTabNavigator();

<Tab.Navigator
  screenOptions={{
    tabBarActiveTintColor: Colors.light.primary,
    tabBarInactiveTintColor: Colors.light.secondary,
    tabBarStyle: { 
      height: Platform.OS === 'ios' ? 83 : 60, // iOS includes safe area
      paddingBottom: Platform.OS === 'ios' ? 20 : 0,
    },
  }}
>
  <Tab.Screen name="Home" component={HomeScreen} />
  <Tab.Screen name="Search" component={SearchScreen} />
  <Tab.Screen name="Profile" component={ProfileScreen} />
</Tab.Navigator>
```

**Navigation Bar (Top Bar)**
- Large title: 34pt, scrolls to small
- Small title: 17pt, centered or left-aligned
- Back button: Left side with "<" chevron
- Actions: Right side

```tsx
<Stack.Navigator
  screenOptions={{
    headerStyle: {
      backgroundColor: colors.background,
    },
    headerTintColor: colors.primary,
    headerTitleStyle: {
      fontSize: Platform.OS === 'ios' ? 17 : 20,
      fontWeight: Platform.OS === 'ios' ? '600' : '500',
    },
    headerLargeTitleStyle: Platform.OS === 'ios' && {
      fontSize: 34,
      fontWeight: '700',
    },
    headerBackTitle: '', // iOS shows back button with empty title
  }}
>
```

### Android Navigation

**Bottom Navigation**
- Position: Bottom of screen
- Items: 3-5 tabs
- Active indicator: Colored background pill
- Height: 56dp (Android standard)

```tsx
<Tab.Navigator
  screenOptions={{
    tabBarActiveTintColor: Colors.dark.primary,
    tabBarStyle: {
      height: 60,
      paddingBottom: 8,
    },
    tabBarLabelStyle: {
      fontSize: 12,
      fontWeight: '500',
    },
  }}
>
```

**Top App Bar**
- Fixed height: 56dp
- Title: Left-aligned, 20sp
- Navigation icon: Left (hamburger or back)
- Actions: Right side (icons only)

```tsx
<Stack.Navigator
  screenOptions={{
    headerStyle: {
      elevation: 4, // Android shadow
    },
    headerTitleAlign: 'left', // Android default
    headerTitleStyle: {
      fontSize: 20,
      fontWeight: '500',
    },
  }}
>
```

**Navigation Drawer (Hamburger Menu)**
- Swipe from left edge to open
- Full-screen overlay
- More common on Android than iOS

```tsx
import { createDrawerNavigator } from '@react-navigation/drawer';

const Drawer = createDrawerNavigator();

<Drawer.Navigator
  screenOptions={{
    drawerStyle: {
      width: 280,
    },
    drawerActiveTintColor: colors.primary,
  }}
>
```

## Button Styles

### iOS Buttons

**Characteristics:**
- Rounded corners (8-12px)
- Subtle shadows
- Filled primary, outline secondary
- Haptic feedback on press
- San Francisco font

```tsx
const iosButtonStyle = {
  paddingVertical: 12,
  paddingHorizontal: 24,
  borderRadius: 12,
  backgroundColor: colors.primary,
  shadowColor: '#000',
  shadowOffset: { width: 0, height: 2 },
  shadowOpacity: 0.1,
  shadowRadius: 4,
};
```

### Android Buttons

**Characteristics:**
- More squared corners (4-8px)
- Elevation (shadow)
- Material ripple effect
- All-caps text (optional, now deprecated)
- Roboto font

```tsx
const androidButtonStyle = {
  paddingVertical: 12,
  paddingHorizontal: 24,
  borderRadius: 4,
  backgroundColor: colors.primary,
  elevation: 2,
};

// Ripple effect (built into TouchableNativeFeedback)
import { TouchableNativeFeedback } from 'react-native';

<TouchableNativeFeedback
  background={TouchableNativeFeedback.Ripple(colors.primary, false)}
>
  <View style={styles.button}>
    <Text>Button</Text>
  </View>
</TouchableNativeFeedback>
```

## Typography

### iOS Typography (San Francisco)

```tsx
const iosTypography = {
  largeTitle: { fontSize: 34, fontWeight: '700', lineHeight: 41 },
  title1: { fontSize: 28, fontWeight: '700', lineHeight: 34 },
  title2: { fontSize: 22, fontWeight: '700', lineHeight: 28 },
  title3: { fontSize: 20, fontWeight: '600', lineHeight: 25 },
  headline: { fontSize: 17, fontWeight: '600', lineHeight: 22 },
  body: { fontSize: 17, fontWeight: '400', lineHeight: 22 },
  callout: { fontSize: 16, fontWeight: '400', lineHeight: 21 },
  subhead: { fontSize: 15, fontWeight: '400', lineHeight: 20 },
  footnote: { fontSize: 13, fontWeight: '400', lineHeight: 18 },
  caption1: { fontSize: 12, fontWeight: '400', lineHeight: 16 },
  caption2: { fontSize: 11, fontWeight: '400', lineHeight: 13 },
};

const iosFontFamily = Platform.select({
  ios: {
    regular: 'System',
    medium: 'System',
    semibold: 'System',
    bold: 'System',
  },
});
```

### Android Typography (Roboto)

```tsx
const androidTypography = {
  h1: { fontSize: 96, fontWeight: '300', lineHeight: 112 },
  h2: { fontSize: 60, fontWeight: '300', lineHeight: 72 },
  h3: { fontSize: 48, fontWeight: '400', lineHeight: 56 },
  h4: { fontSize: 34, fontWeight: '400', lineHeight: 42 },
  h5: { fontSize: 24, fontWeight: '400', lineHeight: 32 },
  h6: { fontSize: 20, fontWeight: '500', lineHeight: 32 },
  subtitle1: { fontSize: 16, fontWeight: '400', lineHeight: 28 },
  subtitle2: { fontSize: 14, fontWeight: '500', lineHeight: 22 },
  body1: { fontSize: 16, fontWeight: '400', lineHeight: 24 },
  body2: { fontSize: 14, fontWeight: '400', lineHeight: 20 },
  button: { fontSize: 14, fontWeight: '500', lineHeight: 16, textTransform: 'uppercase' },
  caption: { fontSize: 12, fontWeight: '400', lineHeight: 16 },
  overline: { fontSize: 10, fontWeight: '400', lineHeight: 16, textTransform: 'uppercase' },
};
```

## Gestures

### iOS Gestures

**Swipe Back:**
- Swipe from left edge to go back
- Built into React Navigation stack

```tsx
<Stack.Navigator
  screenOptions={{
    gestureEnabled: true, // Default on iOS
    gestureDirection: 'horizontal',
  }}
>
```

**Long Press:**
- Long press for context menus
- 500ms minimum

```tsx
<TouchableOpacity
  onLongPress={() => {
    // Show context menu
  }}
  delayLongPress={500}
>
```

### Android Gestures

**Back Button:**
- Hardware/software back button
- Must handle back navigation

```tsx
import { BackHandler } from 'react-native';

useEffect(() => {
  const backAction = () => {
    // Handle back button
    return true; // Prevent default back
  };

  const backHandler = BackHandler.addEventListener(
    'hardwareBackPress',
    backAction
  );

  return () => backHandler.remove();
}, []);
```

**Swipe Actions:**
- Less common than iOS
- When used, swipe from right edge

## Modals & Dialogs

### iOS Modals

**Sheet Modal:**
- Slides up from bottom
- Has drag handle for dismissal
- Rounded top corners

```tsx
<Stack.Navigator>
  <Stack.Screen
    name="Modal"
    component={ModalScreen}
    options={{
      presentation: 'modal', // iOS-style modal
      headerShown: false,
    }}
  />
</Stack.Navigator>

// Custom bottom sheet
import BottomSheet from '@gorhom/bottom-sheet';

<BottomSheet
  snapPoints={['25%', '50%', '90%']}
  enablePanDownToClose={true}
>
  <View>{/* Content */}</View>
</BottomSheet>
```

**Alert:**
- Centered on screen
- Rounded corners
- Stacked buttons (2+ actions)

```tsx
import { Alert } from 'react-native';

Alert.alert(
  'Delete Item',
  'Are you sure you want to delete this item?',
  [
    { text: 'Cancel', style: 'cancel' },
    { text: 'Delete', style: 'destructive', onPress: handleDelete },
  ]
);
```

### Android Dialogs

**Dialog:**
- Material Design dialog
- Sharp corners (default) or rounded
- Side-by-side buttons

```tsx
Alert.alert(
  'Delete Item',
  'Are you sure?',
  [
    { text: 'CANCEL' }, // All-caps on Android
    { text: 'DELETE', onPress: handleDelete },
  ]
);
```

**Bottom Sheet:**
- Less common than iOS
- When used, no drag handle
- Backdrop dismissal

## Forms & Inputs

### iOS Forms

**Text Input:**
- Rounded corners
- Light gray background
- Inset style

```tsx
const iosInputStyle = {
  backgroundColor: '#F2F2F7',
  borderRadius: 10,
  paddingHorizontal: 16,
  paddingVertical: 12,
  fontSize: 17,
};
```

**Picker/Selector:**
- Inline wheel picker
- Bottom sheet for selections

```tsx
import { Picker } from '@react-native-picker/picker';

<Picker
  selectedValue={value}
  onValueChange={setValue}
  style={{ height: 216 }} // iOS picker height
>
  <Picker.Item label="Option 1" value="1" />
  <Picker.Item label="Option 2" value="2" />
</Picker>
```

### Android Forms

**Text Input:**
- Underline style (Material)
- Or outlined style
- Label animates on focus

```tsx
const androidInputStyle = {
  borderBottomWidth: 1,
  borderBottomColor: colors.border,
  paddingHorizontal: 0,
  paddingVertical: 8,
  fontSize: 16,
};

// Or use React Native Paper
import { TextInput } from 'react-native-paper';

<TextInput
  mode="outlined" // or "flat"
  label="Email"
  value={email}
  onChangeText={setEmail}
/>
```

**Dropdown:**
- Dialog-style picker
- Overlays screen

## Lists & Cards

### iOS Lists

**List Style:**
- Inset grouped style
- Rounded corners
- White background
- Gray separator lines

```tsx
const iosListStyle = {
  backgroundColor: colors.background,
  borderRadius: 10,
  marginHorizontal: 16,
  marginVertical: 8,
  overflow: 'hidden',
};
```

**Swipe Actions:**
- Swipe left for actions
- Swipe right for primary action (archive, complete)

```tsx
import { Swipeable } from 'react-native-gesture-handler';

<Swipeable
  renderRightActions={() => (
    <TouchableOpacity onPress={handleDelete}>
      <Text>Delete</Text>
    </TouchableOpacity>
  )}
>
  <View>{/* List item */}</View>
</Swipeable>
```

### Android Lists

**List Style:**
- Full-width items
- Divider lines
- Material elevation on cards

```tsx
const androidListStyle = {
  paddingHorizontal: 16,
  paddingVertical: 12,
  borderBottomWidth: 1,
  borderBottomColor: colors.border,
};

const androidCardStyle = {
  elevation: 2,
  borderRadius: 4,
  margin: 8,
};
```

## Icons

### iOS Icons (SF Symbols Style)

- Outline style
- Rounded
- 24-28pt size

```tsx
import { Ionicons } from '@expo/vector-icons';

<Ionicons 
  name="heart-outline" 
  size={28} 
  color={colors.primary}
/>
```

### Android Icons (Material Icons)

- Filled or outline style
- 24dp size standard

```tsx
import { MaterialIcons } from '@expo/vector-icons';

<MaterialIcons
  name="favorite"
  size={24}
  color={colors.primary}
/>
```

## Colors & Theming

### iOS Colors

```tsx
const iosColors = {
  light: {
    systemBlue: '#007AFF',
    systemGreen: '#34C759',
    systemIndigo: '#5856D6',
    systemOrange: '#FF9500',
    systemPink: '#FF2D55',
    systemPurple: '#AF52DE',
    systemRed: '#FF3B30',
    systemTeal: '#5AC8FA',
    systemYellow: '#FFCC00',
    
    systemGray: '#8E8E93',
    systemGray2: '#AEAEB2',
    systemGray3: '#C7C7CC',
    systemGray4: '#D1D1D6',
    systemGray5: '#E5E5EA',
    systemGray6: '#F2F2F7',
  },
  dark: {
    systemBlue: '#0A84FF',
    systemGreen: '#30D158',
    // ... (same structure, different values)
  },
};
```

### Android Colors (Material)

```tsx
const androidColors = {
  light: {
    primary: '#6200EE',
    primaryVariant: '#3700B3',
    secondary: '#03DAC6',
    secondaryVariant: '#018786',
    background: '#FFFFFF',
    surface: '#FFFFFF',
    error: '#B00020',
    onPrimary: '#FFFFFF',
    onSecondary: '#000000',
    onBackground: '#000000',
    onSurface: '#000000',
    onError: '#FFFFFF',
  },
  dark: {
    primary: '#BB86FC',
    primaryVariant: '#3700B3',
    // ... (same structure)
  },
};
```

## Status Bar

### iOS Status Bar

```tsx
import { StatusBar } from 'expo-status-bar';

<StatusBar 
  style={colorScheme === 'dark' ? 'light' : 'dark'} // auto, light, dark
  backgroundColor="transparent" // iOS ignores this
/>
```

### Android Status Bar

```tsx
<StatusBar
  style={colorScheme === 'dark' ? 'light' : 'dark'}
  backgroundColor={colors.primary} // Android uses this
  translucent={true} // Draw behind status bar
/>
```

## Animations

### iOS Animation Curves

```tsx
import { Easing } from 'react-native-reanimated';

const iosEasing = {
  standard: Easing.bezier(0.4, 0.0, 0.2, 1),
  decelerate: Easing.bezier(0.0, 0.0, 0.2, 1),
  accelerate: Easing.bezier(0.4, 0.0, 1, 1),
};

const iosDurations = {
  short: 200,
  medium: 300,
  long: 400,
};
```

### Android Animation Curves

```tsx
const androidEasing = {
  standard: Easing.bezier(0.4, 0.0, 0.2, 1),
  decelerate: Easing.bezier(0.0, 0.0, 0.2, 1),
  accelerate: Easing.bezier(0.4, 0.0, 1, 1),
  sharp: Easing.bezier(0.4, 0.0, 0.6, 1),
};

const androidDurations = {
  short: 150,
  medium: 250,
  long: 350,
};
```

## Summary Table

| Feature | iOS | Android |
|---------|-----|---------|
| **Navigation** | Bottom tabs (49pt), swipe back | Bottom nav (56dp), top app bar |
| **Buttons** | Rounded (8-12px), subtle shadow | Squared (4-8px), elevation, ripple |
| **Typography** | San Francisco, 17pt body | Roboto, 16sp body |
| **Modals** | Sheet from bottom, drag to dismiss | Dialog centered, backdrop dismiss |
| **Forms** | Rounded, inset, light background | Outlined/underline, label animates |
| **Lists** | Inset grouped, rounded corners | Full-width, divider lines |
| **Icons** | Outline, rounded | Filled or outline |
| **Gestures** | Swipe back, long press | Back button, less swipe |
| **Shadows** | shadowColor, shadowOffset, shadowOpacity | elevation |
| **Haptics** | Integral to UX | Less common |
| **Animations** | Bouncier, spring-based | Sharper, material motion |

## When to Adapt vs Unify

**Adapt (platform-specific):**
- Navigation structure (tabs vs drawer)
- Button styles (rounded vs sharp)
- Shadows/elevation
- Platform icons (SF Symbols vs Material)
- Haptic feedback (iOS only)
- Gestures (swipe back, back button)

**Unify (same across platforms):**
- Color palette (brand colors)
- Typography scale (with minor size adjustments)
- Spacing system
- Component hierarchy
- Content strategy
- User flows

**Best practice:** Design for one platform first, then adapt thoughtfully for the other. Don't just average the two—users expect platform conventions.
