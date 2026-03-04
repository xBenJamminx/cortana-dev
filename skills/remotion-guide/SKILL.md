# Remotion Guide - Complete Video Composition Reference

## Parameters
$ARGUMENTS

---

You are an expert Remotion developer helping create professional video compositions. This guide covers all essential patterns for writing high-quality Remotion code.

Use this skill when working with Remotion compositions, animations, transitions, audio, or any video-related code in the codebase.

====================================================
1. CRITICAL RULES (MUST FOLLOW)
====================================================

These rules are non-negotiable. Violations will cause rendering failures or inconsistent output.

### 1.1 Use `random('seed')` NOT `Math.random()`

Remotion renders frames in parallel across workers. `Math.random()` produces different values on different workers, breaking determinism.

```tsx
// BEFORE - Non-deterministic, breaks rendering
const x = Math.random() * 100;
const particles = Array(10).fill(0).map(() => ({
  x: Math.random() * width,
  y: Math.random() * height,
}));

// AFTER - Deterministic, safe for parallel rendering
import { random } from 'remotion';

const x = random('my-seed') * 100;
const particles = Array(10).fill(0).map((_, i) => ({
  x: random(`particle-${i}-x`) * width,
  y: random(`particle-${i}-y`) * height,
}));
```

### 1.2 Use Remotion Components, NOT HTML Tags

HTML media elements don't sync with Remotion's frame system.

```tsx
// BEFORE - HTML elements (WRONG)
<img src="image.png" />
<video src="video.mp4" />
<audio src="audio.mp3" />

// AFTER - Remotion components (CORRECT)
import { Img, Audio, OffthreadVideo, staticFile } from 'remotion';

<Img src={staticFile('image.png')} />
<OffthreadVideo src={staticFile('video.mp4')} />
<Audio src={staticFile('audio.mp3')} />
```

### 1.3 NO CSS Transitions or Tailwind Animation Classes

CSS animations run on browser time, not Remotion frame time. They will NOT render correctly.

```tsx
// BEFORE - CSS transitions (WRONG)
<div style={{ transition: 'opacity 0.5s' }} />
<div className="animate-bounce" />
<div className="transition-all duration-300" />

// AFTER - Frame-driven animation (CORRECT)
import { interpolate, useCurrentFrame } from 'remotion';

const frame = useCurrentFrame();
const opacity = interpolate(frame, [0, 15], [0, 1], {
  extrapolateRight: 'clamp',
});
<div style={{ opacity }} />
```

### 1.4 Always Clamp interpolate() Values

Without clamping, values extend beyond your specified range.

```tsx
// BEFORE - No clamping (values can exceed 0-1)
const opacity = interpolate(frame, [0, 30], [0, 1]);

// AFTER - Properly clamped
const opacity = interpolate(frame, [0, 30], [0, 1], {
  extrapolateLeft: 'clamp',
  extrapolateRight: 'clamp',
});
```

### 1.5 Use `staticFile()` for public/ Assets

```tsx
// BEFORE - Direct path (WRONG)
<Img src="/images/photo.jpg" />
<Img src="public/images/photo.jpg" />

// AFTER - staticFile() (CORRECT)
import { staticFile } from 'remotion';
<Img src={staticFile('images/photo.jpg')} />
```

### 1.6 Derive All Animation from `useCurrentFrame()` Only

Never use state, useEffect, or external timing for animations.

```tsx
// BEFORE - State-based animation (WRONG)
const [position, setPosition] = useState(0);
useEffect(() => {
  setPosition(p => p + 1);
}, [frame]);

// AFTER - Frame-derived (CORRECT)
const frame = useCurrentFrame();
const position = frame * 2;
```

### 1.7 Use `delayRender()`/`continueRender()` for Async Operations

```tsx
import { delayRender, continueRender } from 'remotion';

const MyComponent = () => {
  const [data, setData] = useState(null);
  const [handle] = useState(() => delayRender());

  useEffect(() => {
    fetchData().then((result) => {
      setData(result);
      continueRender(handle);
    });
  }, [handle]);

  if (!data) return null;
  return <div>{data.title}</div>;
};
```

====================================================
2. ANIMATION PATTERNS
====================================================

### 2.1 interpolate() with Proper Clamping

```tsx
import { interpolate, useCurrentFrame } from 'remotion';

const frame = useCurrentFrame();

// Fade in over 30 frames
const opacity = interpolate(frame, [0, 30], [0, 1], {
  extrapolateRight: 'clamp',
});

// Scale from 0.5 to 1 between frames 15-45
const scale = interpolate(frame, [15, 45], [0.5, 1], {
  extrapolateLeft: 'clamp',
  extrapolateRight: 'clamp',
});

// Multi-point: fade in, hold, fade out
const visibility = interpolate(
  frame,
  [0, 30, 270, 300],
  [0, 1, 1, 0],
  { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' }
);
```

### 2.2 spring() with Damping Config

```tsx
import { spring, useCurrentFrame, useVideoConfig } from 'remotion';

const frame = useCurrentFrame();
const { fps } = useVideoConfig();

// Basic spring (0 to 1)
const progress = spring({
  frame,
  fps,
  config: { damping: 200 },  // Higher = less bounce
});

// Custom range
const scale = spring({
  frame,
  fps,
  from: 0.8,
  to: 1,
  config: { damping: 100 },
});

// Delayed spring
const delayed = spring({
  frame: frame - 30,  // Start after 30 frames
  fps,
  config: { damping: 200 },
});

// Exit animation (reverse)
const exit = spring({
  frame: frame - 120,
  fps,
  config: { damping: 200 },
  reverse: true,
});
```

**Damping Guidelines:**
- 5-10: Very bouncy (playful)
- 10-50: Moderate bounce (general UI)
- 50-100: Slight overshoot (subtle)
- 100-200: No oscillation (professional)
- 200+: Very stiff (quick snaps)

### 2.3 Enter/Exit Pattern

```tsx
const frame = useCurrentFrame();
const { fps } = useVideoConfig();

// Enter animation (0 to 1)
const enter = spring({
  frame,
  fps,
  config: { damping: 200 },
});

// Exit animation starts at frame 120
const exit = spring({
  frame: frame - 120,
  fps,
  config: { damping: 200 },
});

// Combined: enter minus exit
const scale = enter - exit;
```

### 2.4 @remotion/animation-utils

```tsx
import { makeTransform, rotate, translate, scale } from '@remotion/animation-utils';

const transform = makeTransform([
  rotate(45),           // "rotate(45deg)"
  translate(50, 50),    // "translate(50px, 50px)"
  scale(1.2),           // "scale(1.2)"
]);

<div style={{ transform }}>Hello</div>
```

### 2.5 Easing Functions

```tsx
import { Easing, interpolate } from 'remotion';

// Common easings
interpolate(frame, [0, 30], [0, 1], {
  easing: Easing.ease,                    // Gentle
  extrapolateRight: 'clamp',
});

interpolate(frame, [0, 30], [0, 1], {
  easing: Easing.out(Easing.cubic),       // Smooth deceleration
  extrapolateRight: 'clamp',
});

interpolate(frame, [0, 30], [0, 1], {
  easing: Easing.bezier(0.25, 0.1, 0.25, 1),  // Custom curve
  extrapolateRight: 'clamp',
});
```

====================================================
3. TRANSITIONS
====================================================

### 3.1 TransitionSeries Setup

```tsx
import { TransitionSeries, linearTiming, springTiming } from '@remotion/transitions';
import { fade } from '@remotion/transitions/fade';
import { slide } from '@remotion/transitions/slide';

<TransitionSeries>
  <TransitionSeries.Sequence durationInFrames={90}>
    <SceneOne />
  </TransitionSeries.Sequence>

  <TransitionSeries.Transition
    presentation={fade()}
    timing={linearTiming({ durationInFrames: 30 })}
  />

  <TransitionSeries.Sequence durationInFrames={90}>
    <SceneTwo />
  </TransitionSeries.Sequence>
</TransitionSeries>
```

### 3.2 Built-in Transitions

```tsx
// fade() - Crossfade
import { fade } from '@remotion/transitions/fade';
<TransitionSeries.Transition
  presentation={fade()}
  timing={linearTiming({ durationInFrames: 30 })}
/>

// slide() - Push in/out
import { slide } from '@remotion/transitions/slide';
<TransitionSeries.Transition
  presentation={slide({ direction: 'from-right' })}
  timing={linearTiming({ durationInFrames: 30 })}
/>

// wipe() - Reveal wipe (8 directions)
import { wipe } from '@remotion/transitions/wipe';
<TransitionSeries.Transition
  presentation={wipe({ direction: 'from-left' })}
  timing={linearTiming({ durationInFrames: 30 })}
/>

// flip() - 3D flip
import { flip } from '@remotion/transitions/flip';
<TransitionSeries.Transition
  presentation={flip({ direction: 'from-right' })}
  timing={linearTiming({ durationInFrames: 30 })}
/>

// clockWipe() - Radial clock wipe
import { clockWipe } from '@remotion/transitions/clock-wipe';
<TransitionSeries.Transition
  presentation={clockWipe({})}
  timing={linearTiming({ durationInFrames: 30 })}
/>
```

### 3.3 Timing Functions

```tsx
// Linear timing with optional easing
linearTiming({
  durationInFrames: 30,
  easing: Easing.ease,
})

// Spring-based timing
springTiming({
  config: { damping: 200, stiffness: 100 },
})
```

### 3.4 Manual Transitions (Without TransitionSeries)

```tsx
// BEFORE - Conditional rendering (basic, no animation)
{frame < 30 && <Scene1 />}
{frame >= 30 && <Scene2 />}

// AFTER - Proper crossfade
const progress = interpolate(
  frame,
  [TRANSITION_START, TRANSITION_START + 30],
  [0, 1],
  { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' }
);

{frame < TRANSITION_START + 30 && (
  <AbsoluteFill style={{ opacity: 1 - progress }}>
    <Scene1 />
  </AbsoluteFill>
)}
{frame >= TRANSITION_START && (
  <AbsoluteFill style={{ opacity: progress }}>
    <Scene2 />
  </AbsoluteFill>
)}
```

====================================================
4. AUDIO & CAPTIONS
====================================================

### 4.1 Audio Volume Automation

```tsx
// BEFORE - Static volume
<Audio src={music} volume={0.5} />

// AFTER - Animated volume with fade in/out
<Audio
  src={music}
  volume={(f) => {
    const fadeIn = interpolate(f, [0, 30], [0, 1], {
      extrapolateRight: 'clamp',
    });
    const fadeOut = interpolate(
      f,
      [durationInFrames - 30, durationInFrames],
      [1, 0],
      { extrapolateLeft: 'clamp' }
    );
    return 0.5 * fadeIn * fadeOut;
  }}
/>
```

### 4.2 Audio Data Visualization

```tsx
import { useAudioData, visualizeAudio } from '@remotion/media-utils';

const audioData = useAudioData(staticFile('audio.mp3'));

if (!audioData) return null;

const visualization = visualizeAudio({
  fps,
  frame,
  audioData,
  numberOfSamples: 256,
});

// visualization is array of amplitude values (0-1)
```

### 4.3 @remotion/captions

```tsx
import { parseSrt, createTikTokStyleCaptions } from '@remotion/captions';

// Parse SRT file
const { captions } = parseSrt({ input: srtContent });

// Create TikTok-style word highlighting
const { pages } = createTikTokStyleCaptions({
  captions,
  combineTokensWithinMilliseconds: 100,
});

// Display with word highlighting
const currentTimeMs = (frame / fps) * 1000;
const currentPage = pages.find(
  (page) => currentTimeMs >= page.startMs &&
            currentTimeMs < page.startMs + page.durationMs
);

// CRITICAL: Use white-space: pre to preserve spacing
<div style={{ whiteSpace: 'pre' }}>
  {currentPage?.tokens.map((token, i) => (
    <span
      key={i}
      style={{
        color: currentTimeMs >= token.fromMs ? '#FFD700' : '#FFF',
      }}
    >
      {token.text}
    </span>
  ))}
</div>
```

### 4.4 Typewriter Effect

```tsx
// BEFORE - Per-character opacity (WRONG - causes rendering issues)
text.split('').map((char, i) => (
  <span style={{ opacity: frame > i * 2 ? 1 : 0 }}>{char}</span>
))

// AFTER - String slicing (CORRECT)
const text = 'Hello World';
const charsPerFrame = 0.5;
const visibleChars = Math.floor(frame * charsPerFrame);
const displayText = text.slice(0, Math.min(visibleChars, text.length));

<span>{displayText}</span>
```

====================================================
5. SHAPES & PATHS
====================================================

### 5.1 @remotion/shapes Components

```tsx
import { Circle, Rect, Triangle, Star, Pie, Polygon } from '@remotion/shapes';

<Circle radius={100} fill="green" stroke="red" strokeWidth={2} />
<Rect width={200} height={100} fill="blue" cornerRadius={10} />
<Triangle length={100} fill="red" direction="up" />
<Star points={5} innerRadius={50} outerRadius={100} fill="gold" />
<Pie radius={100} progress={0.75} fill="green" />
<Polygon points={6} radius={80} fill="purple" />
```

### 5.2 @remotion/paths Animations

```tsx
import { evolvePath, interpolatePath, getLength, getPointAtLength } from '@remotion/paths';

// Animate path drawing
const progress = frame / durationInFrames;
const evolution = evolvePath(progress, pathData);

<svg>
  <path
    d={pathData}
    stroke="blue"
    fill="none"
    strokeDasharray={evolution.strokeDasharray}
    strokeDashoffset={evolution.strokeDashoffset}
  />
</svg>

// Morph between paths
const morphed = interpolatePath(progress, squarePath, circlePath);
<path d={morphed} fill="blue" />

// Object following path
const pathLength = getLength(path);
const position = getPointAtLength(path, pathLength * progress);
<g transform={`translate(${position.x}, ${position.y})`}>
  <circle r={10} fill="red" />
</g>
```

====================================================
6. 3D GRAPHICS
====================================================

### 6.1 ThreeCanvas Setup

```tsx
import { ThreeCanvas } from '@remotion/three';

<ThreeCanvas camera={{ position: [0, 0, 5], fov: 50 }}>
  <ambientLight intensity={0.5} />
  <pointLight position={[10, 10, 10]} />
  <mesh>
    <boxGeometry args={[1, 1, 1]} />
    <meshStandardMaterial color="orange" />
  </mesh>
</ThreeCanvas>
```

### 6.2 CRITICAL: Use useCurrentFrame() NOT useFrame()

```tsx
// BEFORE - Three.js timing (WRONG - doesn't sync with Remotion)
import { useFrame } from '@react-three/fiber';

useFrame((state, delta) => {
  meshRef.current.rotation.x += delta;  // WRONG!
});

// AFTER - Remotion timing (CORRECT)
import { useCurrentFrame, useVideoConfig } from 'remotion';

const frame = useCurrentFrame();
const { fps } = useVideoConfig();
const rotation = (frame / fps) * Math.PI * 2;

<mesh rotation={[rotation, rotation * 0.5, 0]}>
  <boxGeometry args={[1, 1, 1]} />
  <meshStandardMaterial color="orange" />
</mesh>
```

### 6.3 Video Textures

```tsx
import { useVideoTexture, useOffthreadVideoTexture } from '@remotion/three';

// Standard video texture
const texture = useVideoTexture(staticFile('video.mp4'));

// Precise frame rendering (recommended for final renders)
const preciseTexture = useOffthreadVideoTexture(staticFile('video.mp4'));

<mesh>
  <planeGeometry args={[16, 9]} />
  <meshBasicMaterial map={texture} toneMapped={false} />
</mesh>
```

### 6.4 Chromium OpenGL Config for Rendering

```tsx
// In renderMedia()
await renderMedia({
  composition,
  serveUrl,
  codec: 'h264',
  chromiumOptions: {
    gl: 'angle',  // Required for 3D
  },
});

// Or in remotion.config.ts
import { Config } from '@remotion/cli/config';
Config.setChromiumOpenGlRenderer('angle');
```

====================================================
7. MEDIA & ASSETS
====================================================

### 7.1 Media Components

```tsx
import { Img, Audio, OffthreadVideo, staticFile } from 'remotion';

// Images
<Img src={staticFile('photo.jpg')} />

// Audio with volume automation
<Audio
  src={staticFile('music.mp3')}
  volume={(f) => interpolate(f, [0, 30], [0, 0.5], { extrapolateRight: 'clamp' })}
/>

// Video (OffthreadVideo recommended)
<OffthreadVideo
  src={staticFile('video.mp4')}
  volume={0.5}
  pauseWhenBuffering
/>
```

### 7.2 Preloading Assets

```tsx
import { prefetch } from 'remotion';

// Prefetch for smooth playback
const { free, waitUntilDone } = prefetch(staticFile('video.mp4'));
await waitUntilDone();
// ... use asset
free();  // Clean up when done
```

### 7.3 Media Trimming

```tsx
const { fps } = useVideoConfig();

// Trim audio/video (values in FRAMES, not seconds)
<Audio
  src={staticFile('audio.mp3')}
  trimBefore={2 * fps}   // Skip first 2 seconds
  trimAfter={10 * fps}   // End at 10 seconds
/>

<OffthreadVideo
  src={staticFile('video.mp4')}
  trimBefore={60}    // Skip first 2 seconds (at 30fps)
  trimAfter={300}    // End at 10 seconds (at 30fps)
/>
```

====================================================
8. COMPOSITION PATTERNS
====================================================

### 8.1 calculateMetadata for Dynamic Duration

```tsx
export const calculateMetadata = async ({ props, abortSignal }) => {
  const data = await fetch(props.apiUrl, { signal: abortSignal });
  const items = await data.json();

  return {
    durationInFrames: items.length * 90 + 180,
    props: { ...props, items },
  };
};

<Composition
  id="dynamic-video"
  component={MyComponent}
  calculateMetadata={calculateMetadata}
  width={1920}
  height={1080}
  fps={30}
  durationInFrames={300}  // Fallback
  defaultProps={{ apiUrl: 'https://api.example.com' }}
/>
```

### 8.2 AbsoluteFill Stacking

Later elements appear on top (use DOM order, not z-index).

```tsx
<AbsoluteFill>
  {/* Bottom layer */}
  <AbsoluteFill style={{ backgroundColor: '#000' }}>
    <BackgroundVideo />
  </AbsoluteFill>

  {/* Middle layer */}
  <AbsoluteFill>
    <ParticleEffect />
  </AbsoluteFill>

  {/* Top layer (rendered last = on top) */}
  <AbsoluteFill>
    <TextOverlay />
  </AbsoluteFill>
</AbsoluteFill>
```

### 8.3 Sequence Timing

```tsx
import { Sequence } from 'remotion';

<>
  {/* Relative frames - frame resets to 0 inside Sequence */}
  <Sequence from={0} durationInFrames={90}>
    <Intro />  {/* useCurrentFrame() returns 0-89 */}
  </Sequence>

  <Sequence from={90} durationInFrames={120}>
    <MainContent />  {/* useCurrentFrame() returns 0-119 */}
  </Sequence>

  <Sequence from={210} durationInFrames={90}>
    <Outro />  {/* useCurrentFrame() returns 0-89 */}
  </Sequence>
</>
```

### 8.4 Series for Sequential Playback

```tsx
import { Series } from 'remotion';

<Series>
  <Series.Sequence durationInFrames={90}>
    <Intro />
  </Series.Sequence>

  <Series.Sequence durationInFrames={120}>
    <MainContent />
  </Series.Sequence>

  <Series.Sequence durationInFrames={90}>
    <Outro />
  </Series.Sequence>
</Series>

{/* Total duration = 90 + 120 + 90 = 300 frames */}
```

====================================================
QUICK REFERENCE TABLE
====================================================

| Pattern | BEFORE (Wrong) | AFTER (Correct) |
|---------|----------------|-----------------|
| Random | `Math.random()` | `random('seed')` |
| Images | `<img src="...">` | `<Img src={staticFile('...')} />` |
| Video | `<video src="...">` | `<OffthreadVideo src={staticFile('...')} />` |
| Audio | `<audio src="...">` | `<Audio src={staticFile('...')} />` |
| Animation | `animate-bounce` | `interpolate(frame, ...)` |
| Interpolate | `interpolate(f, [...], [...])` | `interpolate(f, [...], [...], {extrapolateRight:'clamp'})` |
| Audio volume | `volume={0.5}` | `volume={(f) => interpolate(f, ...)}` |
| Transitions | `{frame < 30 && <Scene1 />}` | `<TransitionSeries>...</TransitionSeries>` |
| 3D timing | `useFrame((state) => {...})` | `const frame = useCurrentFrame()` |
| Typewriter | Per-char opacity | `text.slice(0, chars)` |

====================================================
WHEN TO USE THIS SKILL
====================================================

Invoke this skill when:
- Creating new Remotion compositions
- Debugging animation issues
- Adding transitions between scenes
- Working with audio/video assets
- Implementing captions or text effects
- Adding 3D graphics with @remotion/three
- Troubleshooting rendering inconsistencies

The patterns above represent tested, production-ready approaches used throughout the VideoMind codebase.
