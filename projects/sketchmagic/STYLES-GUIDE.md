# SketchMagic - Art Styles Guide

## How NB2 Sketch-to-Art Works

SketchMagic uses Google's Nano Banana 2 model (`gemini-3.1-flash-image-preview`) for image-to-image transformation. We send:
1. The user's sketch as a PNG (base64 inline_data)
2. A style-specific text prompt

NB2 interprets the sketch's composition, subjects, and layout, then regenerates the image in the requested style.

## All 10 Styles with Prompts

### 1. Photorealistic
- **Icon:** SF Symbol `camera.fill`
- **Color:** #2C3E50 (dark blue-gray)
- **Description:** "Make it look real"
- **Best for:** Animals, landscapes, objects, portraits

```
Transform this sketch into a photorealistic image. Create a highly detailed,
lifelike rendering with natural lighting, realistic textures, and accurate
proportions. Maintain the exact composition and subject of the original drawing.
The result should look like a professional photograph.
```

### 2. Watercolor
- **Icon:** SF Symbol `paintpalette.fill`
- **Color:** #3498DB (blue)
- **Description:** "Soft, flowing colors"
- **Best for:** Flowers, landscapes, animals, abstract shapes

```
Transform this sketch into a beautiful watercolor painting. Use soft, flowing
washes of color with visible brushstrokes and gentle color bleeding at the edges.
Include subtle paper texture. Maintain the composition and subject of the original
drawing. The style should feel like a hand-painted watercolor artwork with
translucent layers.
```

### 3. Anime
- **Icon:** SF Symbol `sparkles`
- **Color:** #E91E63 (pink)
- **Description:** "Japanese animation style"
- **Best for:** Characters, faces, action scenes, fantasy creatures

```
Transform this sketch into anime/manga style artwork. Use clean bold outlines,
vibrant flat colors, large expressive eyes if characters are present, and dynamic
shading typical of Japanese animation. Add subtle cel-shading and anime-style
highlights. Maintain the composition and subject of the original drawing.
```

### 4. Pixel Art
- **Icon:** SF Symbol `gamecontroller.fill`
- **Color:** #27AE60 (green)
- **Description:** "Retro video game pixels"
- **Best for:** Characters, simple objects, icons, game sprites

```
Transform this sketch into detailed pixel art. Use a visible pixel grid with
carefully chosen colors in a limited palette. The style should evoke classic
16-bit era video games with clean, deliberate pixel placement. Maintain the
composition and subject of the original drawing. Include subtle dithering
for shading.
```

### 5. Fantasy
- **Icon:** SF Symbol `wand.and.stars`
- **Color:** #9B59B6 (purple)
- **Description:** "Enchanted and mystical"
- **Best for:** Creatures, castles, magical scenes, characters with powers

```
Transform this sketch into a magical fantasy illustration. Add glowing magical
effects, ethereal lighting, sparkling particles, and an enchanted atmosphere.
Use rich, vibrant colors with magical auras and fantasy-style rendering. Maintain
the composition and subject of the original drawing. The result should feel like
concept art from a fantasy world.
```

### 6. Cartoon
- **Icon:** SF Symbol `bubble.left.fill`
- **Color:** #F39C12 (orange)
- **Description:** "Bold and fun comic style"
- **Best for:** People, animals, funny scenes, action

```
Transform this sketch into a bold cartoon/comic book style illustration. Use
thick black outlines, vibrant flat colors, exaggerated proportions, and dynamic
comic-style shading with halftone dots. Maintain the composition and subject of
the original drawing. The style should feel like a modern cartoon or comic book panel.
```

### 7. Oil Painting
- **Icon:** SF Symbol `paintbrush.fill`
- **Color:** #8B4513 (brown)
- **Description:** "Classical museum quality"
- **Best for:** Portraits, landscapes, still life, dramatic scenes

```
Transform this sketch into a classical oil painting. Use rich, thick brushstrokes
with visible texture and impasto technique. Include realistic lighting with dramatic
chiaroscuro, warm tones, and the depth typical of old master paintings. Maintain
the composition and subject of the original drawing. The result should look like
it belongs in a museum.
```

### 8. Pencil Sketch (Enhanced)
- **Icon:** SF Symbol `pencil.and.outline`
- **Color:** #7F8C8D (gray)
- **Description:** "Professional artist sketch"
- **Best for:** Portraits, architecture, detailed objects, studies

```
Transform this rough sketch into a professional artist's pencil drawing. Use
precise graphite pencil techniques with varied line weight, detailed cross-hatching
for shading, and subtle blending. Add depth through careful tonal values from
light to dark. Maintain the composition and subject of the original drawing. The
result should look like a skilled artist's finished pencil illustration.
```

### 9. Pop Art
- **Icon:** SF Symbol `star.fill`
- **Color:** #E74C3C (red)
- **Description:** "Bold like Warhol"
- **Best for:** Faces, everyday objects, food, bold subjects

```
Transform this sketch into a vibrant pop art illustration in the style of Andy
Warhol and Roy Lichtenstein. Use bold primary colors, thick black outlines,
Ben-Day dots pattern, and high contrast. Include comic-style elements and dramatic
color blocking. Maintain the composition and subject of the original drawing. The
result should feel like iconic 1960s pop art.
```

### 10. Storybook
- **Icon:** SF Symbol `book.fill`
- **Color:** #1ABC9C (teal)
- **Description:** "Like your favorite picture book"
- **Best for:** Animals, characters, scenes, whimsical subjects

```
Transform this sketch into a charming children's storybook illustration. Use warm,
inviting colors with soft textures and gentle shading. The style should feel like
a beloved picture book with whimsical details, approachable characters, and a cozy
atmosphere. Maintain the composition and subject of the original drawing. Add subtle
background details that enhance the storybook feel.
```

## Prompt Engineering Tips for NB2 Sketch-to-Art

### What Works Well
1. **Always start with "Transform this sketch into..."** - This anchors NB2 to treat the input as a sketch to be transformed, not a reference photo.
2. **End with "Maintain the composition and subject of the original drawing."** - This prevents NB2 from going off-script and generating something unrelated.
3. **Be specific about visual techniques** - "thick brushstrokes", "cel-shading", "Ben-Day dots" give NB2 concrete visual targets.
4. **Include texture/material references** - "paper texture", "impasto technique", "visible pixel grid" ground the output in physical media.

### What to Avoid
1. **Don't say "improve" or "fix"** - NB2 might try to "correct" the sketch rather than transform it into art.
2. **Don't reference specific copyrighted characters** - "Like Studio Ghibli" is borderline. Use technique descriptions instead.
3. **Don't use negative prompts** - NB2 doesn't support negative prompting in the same way as Stable Diffusion. State what you want, not what you don't.
4. **Don't ask for text in the image** - NB2 handles text poorly. If the sketch contains writing, it may get garbled.

### Sketch Quality Tips (for users)
- **Bold, clear lines work best** - Use the medium or thick brush. Faint sketches produce weaker results.
- **Fill in major areas** - A stick figure works, but a filled-in character with some shading produces dramatically better results.
- **White background is key** - The canvas exports with white bg, which NB2 handles well. Don't fill the background with color.
- **Simple is fine** - Even a basic house with a tree transforms beautifully. Kids' drawings are actually ideal input.
- **Close your shapes** - Open outlines can confuse NB2 about what's foreground vs background.

### Advanced: Custom Prompt Modifications (Future Feature)
For power users, consider exposing a "prompt modifier" text field:
- "...in the rain" adds weather
- "...at sunset" changes lighting
- "...with a galaxy background" changes the backdrop
- "...as a baby version" makes the subject cuter

These modifiers append to the base style prompt before the "Maintain the composition..." line.

### NB2 Behavior Notes
- **Response time:** 5-15 seconds typical, up to 30 seconds for complex scenes
- **Safety filters:** NB2 will refuse to generate violent, explicit, or harmful content. Simple kid drawings always pass.
- **Resolution:** NB2 returns images at roughly 1024px resolution by default
- **Consistency:** Running the same sketch + prompt twice will produce similar but not identical results (this is a feature, not a bug, users can regenerate to get variations)
- **Edge cases:** Very abstract/minimal sketches (single line, dots) may produce unexpected results. The loading screen should set expectations.

## Adding New Styles

To add a new style, update `ArtStyle.swift` with:
1. New enum case
2. Display name, icon (SF Symbol), accent color, description
3. Full prompt template following the pattern above

Key prompt structure: `"Transform this sketch into [style]. [Style-specific details]. Maintain the composition and subject of the original drawing."`

### Future Style Ideas
- **Cyberpunk** - Neon lights, dark backgrounds, holographic effects
- **Impressionist** - Dappled brushstrokes, broken color, light-focused
- **Claymation** - 3D clay-like appearance, soft shadows
- **Neon/Blacklight** - Glowing lines on dark background
- **Vintage Photo** - Sepia tones, film grain, faded edges
- **Low Poly** - Geometric triangulated 3D look
- **Ukiyo-e** - Japanese woodblock print style
