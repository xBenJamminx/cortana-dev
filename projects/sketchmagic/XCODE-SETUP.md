# SketchMagic - Xcode Project Setup Guide

## Prerequisites

- macOS 15+ (Sequoia)
- Xcode 26.3+
- iPad running iOS 17+ (or Simulator)
- Google Gemini API key (get one at https://aistudio.google.com/apikey)

## Step 1: Create the Xcode Project

1. Open Xcode
2. File > New > Project
3. Choose **App** under iOS
4. Settings:
   - Product Name: **SketchMagic**
   - Team: Your developer team
   - Organization Identifier: `com.yourname` (e.g., `com.benjoselson`)
   - Interface: **SwiftUI**
   - Language: **Swift**
   - Storage: **SwiftData**
   - Testing System: **Swift Testing**
5. Click **Create**

## Step 2: Copy Source Files

Copy the Swift files from this repo into the Xcode project:

```
SketchMagic/
  App/
    SketchMagicApp.swift      -> Replace the default App file
  Models/
    ArtStyle.swift
  Services/
    GeminiAPIClient.swift
  Views/
    CanvasView.swift
    StylePickerView.swift
    GenerationView.swift
```

**How to add files in Xcode:**
1. In the Project Navigator (left sidebar), right-click the SketchMagic folder
2. Select "Add Files to SketchMagic..."
3. Navigate to each file and add it
4. Make sure "Copy items if needed" is checked
5. Ensure target "SketchMagic" is checked

**Or** drag and drop from Finder directly into the Xcode project navigator.

## Step 3: Set Up the API Key

For MVP/development, set the API key directly in the app:

1. Open `GeminiAPIClient.swift`
2. Find the line: `var apiKey: String = ""`
3. Replace with your Gemini API key:
   ```swift
   var apiKey: String = "YOUR_GEMINI_API_KEY_HERE"
   ```

**Production alternative (recommended before App Store):**
- Create a `Config.plist` file with the key
- Or better: set up a backend proxy server so the key never ships in the app binary

## Step 4: Configure Capabilities

1. Select the project in the Navigator
2. Select the SketchMagic target
3. Go to the "Signing & Capabilities" tab
4. Ensure these are configured:

### Required Frameworks
The following are automatically linked when you use them in code:
- **PencilKit** (drawing canvas)
- **Photos** (save to camera roll)

### Info.plist Keys
Add these to your Info.plist (or the "Info" tab in target settings):

| Key | Value |
|-----|-------|
| `NSPhotoLibraryAddUsageDescription` | "SketchMagic saves your generated art to your photo library." |

## Step 5: Configure Build Settings

1. Select the SketchMagic target
2. Build Settings tab:
   - **iOS Deployment Target:** 17.0
   - **Targeted Device Families:** iPad (2)
   - **Swift Language Version:** Swift 6
3. General tab:
   - **Supported Destinations:** iPad
   - **Device Orientation:** All (Portrait, Landscape Left, Landscape Right)

## Step 6: Run the App

1. Select an iPad Simulator (iPad Pro 13-inch recommended)
2. Press Cmd+R to build and run
3. Draw something on the canvas
4. Tap "Make it Magic!" / "Transform!"
5. Pick a style and watch the magic happen

## Step 7: Test with Apple Pencil

If you have a physical iPad with Apple Pencil:
1. Connect your iPad
2. Select it as the run destination
3. Build and run
4. PencilKit automatically handles Pencil input with pressure sensitivity

## Connecting Claude Agent in Xcode 26.3

Xcode 26.3 includes Claude Agent for AI-assisted development. Here's how to use it:

### Enable Claude Agent
1. Xcode > Settings > AI > Claude Agent
2. Sign in with your Anthropic account (or use the built-in integration)
3. Enable "Allow Claude to edit files" and "Allow Claude to run builds"

### What to Tell Claude Agent Next

Once you have the project running, ask Claude Agent to help with these next steps:

**Priority 1 - Core Polish:**
```
"Add a proper onboarding flow with 3 screens showing how the app works.
Include animated examples of drawing, picking a style, and seeing the result."
```

**Priority 2 - App State Management:**
```
"The CanvasView uses @EnvironmentObject var appState: AppState. Create the
AppState class as an ObservableObject with: currentScreen (enum: canvas,
stylePicker, generation, gallery), currentSketch (UIImage?), selectedStyle
(ArtStyle?), and generatedImage (UIImage?). Wire it up in the App entry point."
```

**Priority 3 - Generation Limits (Freemium):**
```
"Add a daily generation limit of 5 free generations. Track the count in
UserDefaults with the date. Show a paywall sheet when limit is reached.
Use StoreKit 2 for subscription management."
```

**Priority 4 - UI Polish:**
```
"Add haptic feedback when the Transform button is tapped and when generation
completes. Add a confetti animation when the generated image appears. Make
the style cards animate in with a staggered spring animation."
```

**Priority 5 - Offline Gallery:**
```
"Make the Gallery screen show both the original sketch and generated image.
Add swipe-to-delete, a favorites filter, and the ability to re-generate
a saved sketch with a different style."
```

## Project Structure

```
SketchMagic/
├── App/
│   └── SketchMagicApp.swift      # App entry point + navigation + SwiftData model
├── Models/
│   └── ArtStyle.swift            # 10 art styles with prompts + Color hex extension
├── Services/
│   └── GeminiAPIClient.swift     # Gemini API client (NB2 image-to-image)
└── Views/
    ├── CanvasView.swift          # PencilKit drawing canvas + toolbar
    ├── StylePickerView.swift     # Art style selection grid
    └── GenerationView.swift      # Loading, result, compare, save/share
```

## Troubleshooting

### "No image was generated"
- Check your API key is correct
- The Gemini API has safety filters. Very abstract sketches sometimes don't produce results. Try drawing something recognizable.

### PencilKit not responding
- Make sure `drawingPolicy` is set to `.anyInput` for finger drawing
- On simulator, use mouse clicks as finger touches

### Build errors about SwiftData
- Ensure deployment target is iOS 17+
- Make sure you selected SwiftData when creating the project

### API rate limits
- Free tier: ~15 requests/minute
- If you hit limits, wait a minute and try again
- Consider upgrading to a paid Gemini API plan for production
