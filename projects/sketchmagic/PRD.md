# SketchMagic - Product Requirements Document

**Working Title:** SketchMagic (alt: DoodleAI)
**Version:** 1.0 MVP
**Last Updated:** February 27, 2026

## Vision

SketchMagic turns kids' drawings into stunning AI-generated art. Draw anything with your finger or Apple Pencil, pick an art style, and watch your sketch transform into a masterpiece. It's magic for creative kids (and adults who draw like kids).

The core experience is **Draw, Pick, Transform** in under 30 seconds.

## Target Audience

| Segment | Age | Why They Love It |
|---------|-----|-----------------|
| Primary: Kids | 6-14 | Draw anything, see it become "real" art instantly |
| Secondary: Parents | 25-45 | Safe, creative screen time. No social features, no chat. |
| Tertiary: Casual Artists | 15+ | Quick concept art, style exploration, fun creative tool |

## Core User Flow

```
[Open App] -> [Canvas: Draw Something] -> [Tap "Transform!"] -> [Style Picker: Choose Art Style] -> [Loading: Watch the Magic] -> [Result: See Your Art] -> [Save / Share / Try Another Style]
```

## Screens

### 1. Canvas Screen (Home)

The main screen. A full-screen drawing canvas.

**Components:**
- Full-screen PencilKit canvas (white background)
- Top toolbar:
  - Undo / Redo buttons
  - Clear canvas button (with confirmation)
  - Gallery button (top-left)
- Bottom toolbar:
  - Color picker (kid-friendly palette: 12 bold colors + black + white)
  - Brush size slider (3 sizes: thin, medium, thick)
  - Eraser toggle
  - Pen/marker toggle
- Floating "Transform!" button (bottom-right, large, colorful, animated)
  - Only appears after user has drawn something
  - Pulses gently to attract attention

**Behavior:**
- Apple Pencil draws by default, finger scrolls (standard PencilKit)
- Option to enable finger drawing (for kids without Pencil)
- Canvas exports as PNG with white background at 1024x1024

### 2. Style Picker (Modal Sheet)

Appears as a half-sheet modal after tapping "Transform!"

**Components:**
- Grid of style cards (2 columns)
- Each card: emoji icon, style name, 1-line description, gradient background
- "Go!" button at bottom (disabled until style selected)
- Close button (X) to go back to drawing

**Behavior:**
- Tapping a card selects it (highlighted border)
- Tapping "Go!" sends sketch + style to API
- Shows small preview of the sketch at the top

### 3. Generation / Loading Screen

Full-screen loading experience while the API works.

**Components:**
- User's sketch displayed at top (small)
- Animated progress indicator (sparkles, magic wand animation)
- Fun text cycling: "Adding magic...", "Mixing colors...", "Almost there...", "Creating your masterpiece..."
- Style name displayed: "Transforming into Watercolor..."
- Cancel button

**Behavior:**
- API call typically takes 5-15 seconds
- If >20 seconds, show "Taking a bit longer..." message
- On error, show friendly message + "Try Again" button
- On success, transition to Result View with a reveal animation

### 4. Result View

Shows the generated art alongside the original sketch.

**Components:**
- Generated image (large, center)
- Before/after comparison slider (drag to reveal original sketch underneath)
- Bottom action bar:
  - "Save" button (saves to Photos)
  - "Share" button (iOS share sheet)
  - "Try Another Style" button (back to Style Picker with same sketch)
  - "New Drawing" button (back to blank canvas)
- Style badge showing which style was used
- Star rating (optional, for future analytics)

**Behavior:**
- Images save at full resolution returned by NB2
- Share includes both the generated art and a small watermark "Made with SketchMagic"
- "Try Another Style" preserves the original sketch

### 5. Gallery Screen

Browse previously generated art.

**Components:**
- Grid of saved artworks (3 columns)
- Each item shows: generated image thumbnail, style badge, date
- Tap to view full-screen (same as Result View but from history)
- Long-press for delete
- Empty state: "No art yet! Start drawing to create your first masterpiece."

**Behavior:**
- Stored locally using SwiftData
- Saves both the original sketch and generated image
- Sort by date (newest first)

## Art Styles (10 Styles for MVP)

### 1. Photorealistic
- **Icon:** camera emoji
- **Color:** #2C3E50 (dark blue-gray)
- **Description:** "Make it look real"
- **Prompt Template:**
  ```
  Transform this sketch into a photorealistic image. Create a highly detailed, lifelike rendering with natural lighting, realistic textures, and accurate proportions. Maintain the exact composition and subject of the original drawing. The result should look like a professional photograph.
  ```

### 2. Watercolor Painting
- **Icon:** art palette emoji
- **Color:** #3498DB (blue)
- **Description:** "Soft, flowing colors"
- **Prompt Template:**
  ```
  Transform this sketch into a beautiful watercolor painting. Use soft, flowing washes of color with visible brushstrokes and gentle color bleeding at the edges. Include subtle paper texture. Maintain the composition and subject of the original drawing. The style should feel like a hand-painted watercolor artwork with translucent layers.
  ```

### 3. Anime / Manga
- **Icon:** sparkles emoji
- **Color:** #E91E63 (pink)
- **Description:** "Japanese animation style"
- **Prompt Template:**
  ```
  Transform this sketch into anime/manga style artwork. Use clean bold outlines, vibrant flat colors, large expressive eyes if characters are present, and dynamic shading typical of Japanese animation. Add subtle cel-shading and anime-style highlights. Maintain the composition and subject of the original drawing.
  ```

### 4. Pixel Art
- **Icon:** joystick emoji
- **Color:** #27AE60 (green)
- **Description:** "Retro video game pixels"
- **Prompt Template:**
  ```
  Transform this sketch into detailed pixel art. Use a visible pixel grid with carefully chosen colors in a limited palette. The style should evoke classic 16-bit era video games with clean, deliberate pixel placement. Maintain the composition and subject of the original drawing. Include subtle dithering for shading.
  ```

### 5. Fantasy / Magical
- **Icon:** crystal ball emoji
- **Color:** #9B59B6 (purple)
- **Description:** "Enchanted and mystical"
- **Prompt Template:**
  ```
  Transform this sketch into a magical fantasy illustration. Add glowing magical effects, ethereal lighting, sparkling particles, and an enchanted atmosphere. Use rich, vibrant colors with magical auras and fantasy-style rendering. Maintain the composition and subject of the original drawing. The result should feel like concept art from a fantasy world.
  ```

### 6. Cartoon / Comic
- **Icon:** speech balloon emoji
- **Color:** #F39C12 (orange)
- **Description:** "Bold and fun comic style"
- **Prompt Template:**
  ```
  Transform this sketch into a bold cartoon/comic book style illustration. Use thick black outlines, vibrant flat colors, exaggerated proportions, and dynamic comic-style shading with halftone dots. Maintain the composition and subject of the original drawing. The style should feel like a modern cartoon or comic book panel.
  ```

### 7. Oil Painting
- **Icon:** framed picture emoji
- **Color:** #8B4513 (brown)
- **Description:** "Classical museum quality"
- **Prompt Template:**
  ```
  Transform this sketch into a classical oil painting. Use rich, thick brushstrokes with visible texture and impasto technique. Include realistic lighting with dramatic chiaroscuro, warm tones, and the depth typical of old master paintings. Maintain the composition and subject of the original drawing. The result should look like it belongs in a museum.
  ```

### 8. Pencil Sketch (Enhanced)
- **Icon:** pencil emoji
- **Color:** #7F8C8D (gray)
- **Description:** "Professional artist sketch"
- **Prompt Template:**
  ```
  Transform this rough sketch into a professional artist's pencil drawing. Use precise graphite pencil techniques with varied line weight, detailed cross-hatching for shading, and subtle blending. Add depth through careful tonal values from light to dark. Maintain the composition and subject of the original drawing. The result should look like a skilled artist's finished pencil illustration.
  ```

### 9. Pop Art
- **Icon:** star emoji
- **Color:** #E74C3C (red)
- **Description:** "Bold like Warhol"
- **Prompt Template:**
  ```
  Transform this sketch into a vibrant pop art illustration in the style of Andy Warhol and Roy Lichtenstein. Use bold primary colors, thick black outlines, Ben-Day dots pattern, and high contrast. Include comic-style elements and dramatic color blocking. Maintain the composition and subject of the original drawing. The result should feel like iconic 1960s pop art.
  ```

### 10. Storybook Illustration
- **Icon:** open book emoji
- **Color:** #1ABC9C (teal)
- **Description:** "Like your favorite picture book"
- **Prompt Template:**
  ```
  Transform this sketch into a charming children's storybook illustration. Use warm, inviting colors with soft textures and gentle shading. The style should feel like a beloved picture book with whimsical details, approachable characters, and a cozy atmosphere. Maintain the composition and subject of the original drawing. Add subtle background details that enhance the storybook feel.
  ```

## API Integration

### Model
- **Model:** `gemini-3.1-flash-image-preview` (Nano Banana 2)
- **Endpoint:** `https://generativelanguage.googleapis.com/v1beta/models/gemini-3.1-flash-image-preview:generateContent`
- **Auth:** API key as query parameter `?key=API_KEY`

### Request Format
```json
{
  "contents": [{
    "parts": [
      {
        "inline_data": {
          "mime_type": "image/png",
          "data": "<base64-encoded-sketch>"
        }
      },
      {
        "text": "<style prompt template>"
      }
    ]
  }],
  "generationConfig": {
    "responseModalities": ["IMAGE", "TEXT"],
    "candidateCount": 1
  }
}
```

### Response Parsing
- Parse `candidates[0].content.parts`
- Find the part where `inline_data.mime_type` starts with `"image/"`
- Decode `inline_data.data` from base64 to get the generated image
- If no image part found, check for text error message

### Rate Limiting
- NB2 free tier: ~15 requests per minute
- MVP: No rate limiting in-app (rely on API limits)
- Production: Add rate limiting (5 generations per minute per user)

### Error Handling
- Network timeout: 30 second timeout, show retry button
- API error (4xx/5xx): Show friendly "Oops! The magic didn't work. Try again?"
- Content filtered: "Let's try a different drawing!" (NB2 has safety filters)
- No image in response: Retry once automatically, then show error

## Data Model

### Artwork (SwiftData)
```swift
@Model
class Artwork {
    var id: UUID
    var sketchData: Data        // Original sketch as PNG
    var generatedData: Data     // Generated art as PNG
    var styleName: String       // Art style used
    var createdAt: Date
    var isFavorite: Bool
}
```

### UserSettings (AppStorage)
```swift
// @AppStorage keys
"fingerDrawingEnabled": Bool    // Default: true (for kids without Pencil)
"defaultBrushSize": Double      // Default: 5.0
"hasSeenOnboarding": Bool       // Default: false
"generationCount": Int          // Track usage
"apiKey": String                // Stored in Keychain (production)
```

## App Store / COPPA Compliance

### COPPA (Children's Online Privacy Protection Act)
- **No account creation required** - app works fully offline except for API calls
- **No personal data collection** - no names, emails, ages collected
- **No social features** - no sharing to in-app feeds, no user profiles
- **No third-party analytics SDKs** in MVP (no Firebase, no Amplitude)
- **No advertising** - zero ads, especially no targeted ads
- **Parental gate** for any in-app purchases (simple math problem)
- **API calls send only the sketch image** - no metadata, no device info
- **Privacy policy required** - must state: "We do not collect personal information from children"

### App Store Guidelines
- Age rating: 4+ (no objectionable content)
- Category: Entertainment or Education
- Content descriptions: No objectionable content, no unrestricted web access
- Made for Kids designation: Yes (optional but recommended)
- If "Made for Kids": Cannot use third-party analytics, no IDFA

### API Key Security (Production)
- MVP: API key embedded in app (acceptable for TestFlight/development)
- Production: MUST use a backend proxy server
  - App calls your server, server calls Gemini API
  - Prevents API key extraction from app binary
  - Enables usage tracking and rate limiting per user/device

## Monetization Recommendation

### Freemium Model
- **Free tier:** 5 generations per day (resets at midnight local time)
- **SketchMagic Pro:** $4.99/month or $29.99/year
  - Unlimited generations
  - All art styles (free tier gets 5 styles)
  - High-resolution export (2x resolution)
  - No watermark on shared images
- **Style Packs:** $1.99 each (future expansion)
  - "Seasonal Pack" (holiday-themed styles)
  - "Famous Artists Pack" (impressionist, cubist, etc.)
  - "Game Art Pack" (isometric, low-poly, voxel)

### Why This Works
- Low barrier to entry: kids can try it for free
- Parents see value before paying
- Subscription covers API costs (~$0.01-0.03 per generation)
- Style packs add long-term revenue without being pushy

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Platform | iPad, iOS 17+ |
| UI Framework | SwiftUI |
| Drawing | PencilKit |
| AI Model | Gemini 3.1 Flash Image (NB2) |
| Storage | SwiftData |
| Networking | URLSession (async/await) |
| Image Processing | Core Image, UIKit |

## MVP Scope (v1.0)

### In Scope
- Full drawing canvas with PencilKit
- 10 art styles with NB2 generation
- Save to Photos
- Share sheet
- Local gallery
- Before/after comparison

### Out of Scope (v1.1+)
- User accounts / cloud sync
- Backend proxy server (use embedded key for MVP)
- In-app purchases / subscription
- Additional style packs
- Drawing templates / starter sketches
- Undo history visualization
- Time-lapse of drawing process
- Social sharing features
- iPad + iPhone universal (iPad only for MVP)

## Success Metrics

- **Core:** Generation success rate > 95%
- **Engagement:** Average 3+ generations per session
- **Retention:** D7 retention > 30%
- **Quality:** App Store rating > 4.5 stars
- **Growth:** 1,000 downloads in first month (organic)
