# SketchMagic Style Guide

## Art Styles & NB2 Prompt Templates

Each style transforms the user's sketch using a carefully crafted prompt sent to Nano Banana 2 (gemini-3.1-flash-image-preview).

### Tips for Best Results with NB2

- **Simple sketches work best** - NB2 excels at interpreting rough drawings, not detailed ones
- **Clear subjects** - A recognizable shape (person, house, tree, animal) gives NB2 something to work with
- **White background** - PencilKit exports with white bg, which NB2 handles well
- **Composition matters** - Where things are placed in the sketch is preserved in the output
- **Black pen recommended** - High contrast sketches give the clearest signal to NB2

### Style Definitions

#### 1. Photorealistic
- **Best for:** Landscapes, portraits, animals, architecture
- **Prompt:** "Transform this sketch into a photorealistic image. Make it look like a high-quality photograph with realistic lighting, textures, materials, and depth of field. Maintain the exact composition, subjects, and layout of the original drawing. Add realistic environmental details, shadows, and atmosphere."

#### 2. Watercolor
- **Best for:** Nature scenes, flowers, soft subjects
- **Prompt:** "Transform this sketch into a beautiful watercolor painting. Use soft, translucent washes of color with visible paper texture. Include gentle color bleeds at edges, wet-on-wet effects, and subtle granulation. Maintain the composition of the original drawing."

#### 3. Anime
- **Best for:** Characters, action scenes, fantasy creatures
- **Prompt:** "Transform this sketch into anime/manga style artwork. Use clean bold outlines, flat cel-shaded colors with sharp shadows, large expressive features, and vibrant saturated colors. Include anime-style highlights and shading. Maintain the composition of the original drawing. Style similar to Studio Ghibli or modern anime."

#### 4. Pixel Art
- **Best for:** Characters, simple objects, retro game scenes
- **Prompt:** "Transform this sketch into pixel art. Use a limited color palette with clearly visible square pixels. Include pixel-perfect edges, dithering for gradients, and retro video game aesthetics. Maintain the composition of the original drawing. Style similar to 16-bit era SNES/Genesis games with rich detail."

#### 5. Fantasy
- **Best for:** Castles, dragons, magical scenes, epic landscapes
- **Prompt:** "Transform this sketch into epic fantasy artwork. Add magical glowing elements, dramatic lighting with volumetric rays, rich saturated colors, and an enchanted atmosphere. Include subtle magical particles, mystical fog, and ethereal lighting effects. Maintain the composition of the original drawing."

#### 6. Cartoon
- **Best for:** Characters, funny scenes, animals, everyday objects
- **Prompt:** "Transform this sketch into a vibrant cartoon illustration. Use bold black outlines, bright flat colors, exaggerated proportions, and playful details. Add fun expressions and dynamic energy. Maintain the composition of the original drawing."

#### 7. Oil Painting
- **Best for:** Portraits, landscapes, still life
- **Prompt:** "Transform this sketch into a classical oil painting. Show visible impasto brushstrokes with thick paint texture, rich deep colors, dramatic chiaroscuro lighting, and masterful color blending. Maintain the composition of the original drawing."

#### 8. Pencil Sketch (Enhanced)
- **Best for:** Portraits, architecture, detailed subjects
- **Prompt:** "Transform this sketch into a detailed, professional pencil drawing. Use precise graphite shading with smooth gradients, cross-hatching for shadows, fine linework for details, and realistic tonal values. Show paper texture beneath. Maintain the composition of the original drawing."

#### 9. Pop Art
- **Best for:** Portraits, everyday objects, bold subjects
- **Prompt:** "Transform this sketch into bold pop art. Use bright primary colors, thick black outlines, Ben-Day dots pattern, high contrast graphic shapes, and comic book aesthetics. Include halftone effects and bold color blocks. Maintain the composition of the original drawing."

#### 10. Storybook
- **Best for:** Characters, animals, whimsical scenes (most kid-friendly)
- **Prompt:** "Transform this sketch into a charming children's storybook illustration. Use warm, inviting colors with soft edges, gentle lighting, whimsical details, and a cozy magical atmosphere. Include delicate textures and hand-crafted feeling. Maintain the composition of the original drawing."

#### 11. Cyberpunk
- **Best for:** City scenes, robots, futuristic subjects
- **Prompt:** "Transform this sketch into cyberpunk artwork. Add neon glowing lights in pink, blue, and purple, dark atmospheric backgrounds, futuristic technology elements, rain-slicked reflective surfaces, and holographic effects. Maintain the composition of the original drawing."

#### 12. Impressionist
- **Best for:** Outdoor scenes, gardens, water, light-focused subjects
- **Prompt:** "Transform this sketch into an Impressionist painting. Use visible dappled brushstrokes, vibrant broken color, soft natural lighting capturing a specific moment, and a dreamy luminous quality. Show the interplay of light and color. Maintain the composition of the original drawing."

## Adding New Styles

To add a new style, update `ArtStyle.swift` with:
1. New enum case
2. Display name, icon (SF Symbol), accent color, description
3. Full prompt template following the pattern above

Key prompt structure: "Transform this sketch into [style]. [Style-specific details]. Maintain the composition of the original drawing. [Reference to known artists/styles]."
