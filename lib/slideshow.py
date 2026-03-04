"""TikTok slideshow engine — Larry-inspired, adapted for our stack.

Generates 6-slide portrait slideshows with:
- Consistent scene architecture across all slides (only style changes)
- Text overlay on slide 1 (hook)
- Storytelling captions with strategic hashtags
- Export as individual images ready for TikTok draft upload

Supports multiple image models: OpenAI gpt-image-1.5, Gemini (Nano Banana),
Imagen 4, etc.
"""

import base64
import json
import os
import subprocess
import tempfile
import urllib.request
import urllib.parse
from pathlib import Path


# TikTok slideshow specs (from Larry's skill)
SLIDE_WIDTH = 1024
SLIDE_HEIGHT = 1536
NUM_SLIDES = 6
FONT = "/usr/share/fonts/truetype/liberation/LiberationSansNarrow-Bold.ttf"
FONT_FALLBACK = "/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed-Bold.ttf"

# Text overlay specs — tuned for viral TikTok look
HOOK_FONT_SIZE_RATIO = 0.075  # 7.5% of image height (~115px at 1536px) — big, punchy
HOOK_Y_POSITION = 0.30  # 30% from top (top 10% hidden by TikTok status bar)
MAX_WORDS_PER_LINE = 3  # 3 words per line — short, punchy, always fits at this font size
# Bottom 20% hidden behind TikTok caption/buttons — keep text above 80%
HOOK_MAX_Y = 0.78  # text must not extend below 78% of image height


# Image generation now lives in lib/imagegen.py — re-export for backwards compat
from imagegen import generate_image_gemini, generate_image, _get_openai_key, _get_gemini_key


def _wrap_text(text, max_words_per_line=MAX_WORDS_PER_LINE):
    """Break text into lines for readability on mobile."""
    words = text.split()
    lines = []
    current_line = []
    for word in words:
        current_line.append(word)
        if len(current_line) >= max_words_per_line:
            lines.append(" ".join(current_line))
            current_line = []
    if current_line:
        lines.append(" ".join(current_line))
    return "\n".join(lines)


def _get_font_path():
    """Return the best available font path."""
    if os.path.exists(FONT):
        return FONT
    if os.path.exists(FONT_FALLBACK):
        return FONT_FALLBACK
    return "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def _calculate_text_bounds(hook_text, fontsize, words_per_line=None):
    """Calculate how many lines the wrapped text will take and total height.

    Returns (num_lines, total_text_height) so we can dynamically position.
    """
    wpl = words_per_line or MAX_WORDS_PER_LINE
    wrapped = _wrap_text(hook_text, max_words_per_line=wpl)
    num_lines = len(wrapped.split("\n"))
    line_spacing = int(fontsize * 0.25)
    total_height = (num_lines * fontsize) + ((num_lines - 1) * line_spacing)
    return num_lines, total_height


def _verify_text_visible(image_path, hook_text, fontsize, y_pos):
    """Verify text wasn't clipped by checking the rendered image.

    Checks:
    1. Text block fits vertically in safe zone (using actual y_pos)
    2. White text pixels exist in expected region
    3. Text doesn't clip at left/right edges

    Returns True if text appears fully rendered within safe zone.
    """
    try:
        from PIL import Image
        img = Image.open(image_path)
        width, height = img.size

        safe_bottom = int(height * HOOK_MAX_Y)

        num_lines, text_height = _calculate_text_bounds(hook_text, fontsize)
        expected_bottom = y_pos + text_height

        if expected_bottom > safe_bottom:
            print(f"  WARNING: Text extends to y={expected_bottom} but safe zone ends at y={safe_bottom}")
            return False

        # Scan for white text pixels in the actual text region
        found_text = False
        scan_range_x = range(width // 4, 3 * width // 4, 10)
        scan_range_y = range(y_pos, min(expected_bottom, height), 5)
        for y in scan_range_y:
            for x in scan_range_x:
                r, g, b = img.getpixel((x, y))[:3]
                if r > 220 and g > 220 and b > 220:
                    found_text = True
                    break
            if found_text:
                break

        if not found_text:
            print(f"  WARNING: No white text pixels found in expected zone ({y_pos}-{expected_bottom})")
            return False

        # Check for horizontal clipping — white pixels within 15px of edges = clipped
        edge_zone = 15
        clipped = False
        for y in scan_range_y:
            for x in list(range(0, edge_zone)) + list(range(width - edge_zone, width)):
                r, g, b = img.getpixel((x, y))[:3]
                if r > 220 and g > 220 and b > 220:
                    clipped = True
                    break
            if clipped:
                break

        if clipped:
            print(f"  WARNING: Text appears clipped at horizontal edges")
            return False

        print(f"  Text verification PASSED ({num_lines} lines, {fontsize}px, y={y_pos})")
        return True
    except Exception as e:
        print(f"  Verification skipped: {e}")
        return True


def _get_image_size(image_path):
    """Get image width and height using ffprobe (no PIL needed)."""
    cmd = [
        "ffprobe", "-v", "error",
        "-select_streams", "v:0",
        "-show_entries", "stream=width,height",
        "-of", "csv=p=0:s=x",
        image_path,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
    if result.returncode != 0:
        return SLIDE_WIDTH, SLIDE_HEIGHT  # fallback to constants
    w, h = result.stdout.strip().split("x")
    return int(w), int(h)


def add_hook_overlay(image_path, output_path, hook_text):
    """Add hook text overlay to slide 1.

    - Font: Liberation Sans Narrow Bold (condensed, heavy — viral look)
    - Font size: 7.5% of actual image height
    - Dynamic Y: centers text in the safe zone (30%-75% of image)
    - White text with thick black stroke
    - Auto-scales font down if text won't fit
    - Verifies text is fully visible after render
    """
    img_w, img_h = _get_image_size(image_path)
    fontsize = int(img_h * HOOK_FONT_SIZE_RATIO)
    font_path = _get_font_path()

    # Adaptive words per line — longer hooks get more words per line
    # to keep font size large and readable instead of shrinking to tiny text
    word_count = len(hook_text.split())
    if word_count > 12:
        words_per_line = 4
    elif word_count > 8:
        words_per_line = 4
    else:
        words_per_line = MAX_WORDS_PER_LINE

    wrapped = _wrap_text(hook_text, max_words_per_line=words_per_line)
    num_lines, total_text_height = _calculate_text_bounds(hook_text, fontsize, words_per_line)

    # Dynamic Y: center the text block in the safe zone (30%-75%)
    safe_top = int(img_h * HOOK_Y_POSITION)
    safe_bottom = int(img_h * HOOK_MAX_Y)
    safe_zone_height = safe_bottom - safe_top

    if total_text_height >= safe_zone_height:
        # Text is too tall — reduce font size to fit
        scale = safe_zone_height / total_text_height * 0.9  # 90% to leave margin
        fontsize = int(fontsize * scale)
        num_lines, total_text_height = _calculate_text_bounds(hook_text, fontsize, words_per_line)
        print(f"  Font scaled down to {fontsize}px to fit {num_lines} lines")

    y_pos = safe_top + (safe_zone_height - total_text_height) // 2

    # Escape for ffmpeg drawtext
    escaped = wrapped.replace("'", "'\\''").replace(":", "\\:").replace("\\", "\\\\\\\\")
    line_spacing = int(fontsize * 0.25)
    border_w = max(4, fontsize // 18)  # scale border with font

    drawtext = (
        f"drawtext=text='{escaped}'"
        f":fontfile={font_path}"
        f":fontsize={fontsize}"
        f":fontcolor=white"
        f":borderw={border_w}:bordercolor=black"
        f":x=(w-text_w)/2"
        f":y={y_pos}"
        f":line_spacing={line_spacing}"
    )

    cmd = [
        "ffmpeg", "-y",
        "-i", image_path,
        "-vf", drawtext,
        "-q:v", "2",
        output_path,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    if result.returncode != 0:
        raise RuntimeError(f"FFmpeg overlay error: {result.stderr[-500:]}")

    # Verify text is visible — auto-retry with smaller font if clipped
    if not _verify_text_visible(output_path, hook_text, fontsize, y_pos):
        # Reduce font by 15% and retry once
        fontsize = int(fontsize * 0.85)
        num_lines, total_text_height = _calculate_text_bounds(hook_text, fontsize, words_per_line)
        y_pos = safe_top + (safe_zone_height - total_text_height) // 2
        line_spacing = int(fontsize * 0.25)
        border_w = max(4, fontsize // 18)
        escaped = wrapped.replace("'", "'\\''").replace(":", "\\:").replace("\\", "\\\\\\\\")
        print(f"  Retrying with {fontsize}px font...")

        drawtext = (
            f"drawtext=text='{escaped}'"
            f":fontfile={font_path}"
            f":fontsize={fontsize}"
            f":fontcolor=white"
            f":borderw={border_w}:bordercolor=black"
            f":x=(w-text_w)/2"
            f":y={y_pos}"
            f":line_spacing={line_spacing}"
        )
        cmd = [
            "ffmpeg", "-y",
            "-i", image_path,
            "-vf", drawtext,
            "-q:v", "2",
            output_path,
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if result.returncode != 0:
            raise RuntimeError(f"FFmpeg overlay error: {result.stderr[-500:]}")
        _verify_text_visible(output_path, hook_text, fontsize, y_pos)

    return output_path


def build_scene_prompt(base_description, slide_number, style_variation,
                       product_context=""):
    """Build a prompt for a single slide with consistent architecture.

    Larry's key insight: lock the architecture (scene description),
    only change the style between slides. This makes the transformation
    feel real.

    Args:
        base_description: The locked scene description (identical for all 6 slides)
        slide_number: 1-6
        style_variation: What changes about this slide (e.g., "before", "after modern", etc.)
        product_context: Optional product-specific context

    Returns:
        Full prompt string
    """
    prompt = (
        f"Create a portrait photograph (1024x1536 pixels). "
        f"Scene: {base_description}. "
        f"Style for this slide: {style_variation}. "
        f"The scene composition, camera angle, and all objects must remain "
        f"EXACTLY the same as other slides in this series — only the style/look changes. "
        f"Photorealistic, high quality, suitable for TikTok slideshow."
    )
    if product_context:
        prompt += f" Context: {product_context}"
    return prompt


def generate_caption(hook, product_name, niche, cta_style="soft"):
    """Generate a storytelling caption for the slideshow.

    Larry's rules:
    - Storytelling format, not feature lists
    - Mention product naturally, never "Download X now!"
    - Max 5 hashtags
    - Continue the narrative from the hook

    Args:
        hook: The hook text from slide 1
        product_name: Product being promoted
        niche: Content niche
        cta_style: "soft" (natural mention), "direct" (clear CTA), "question" (engagement)

    Returns:
        Caption string with hashtags
    """
    # This is a template — in production, we'd use Claude to generate these
    # For now, return a structured template
    if cta_style == "soft":
        cta = f"I used {product_name} and honestly wasn't expecting much but look at this."
    elif cta_style == "direct":
        cta = f"Try {product_name} — link in bio."
    else:
        cta = f"Would you try this? Let me know in the comments."

    caption = (
        f"{hook}\n\n"
        f"{cta}\n\n"
        f"#AI #{niche.replace(' ', '')} #fyp #viral #tech"
    )
    return caption


def add_label_overlay(image_path, output_path, label_text):
    """Add a short label to the bottom of a slide (above TikTok caption zone).

    Smaller than hook text — sits at ~70% from top, centered.
    Used for slides 2-6 to give each one context.
    """
    img_w, img_h = _get_image_size(image_path)
    fontsize = int(img_h * 0.05)  # 5% of height — smaller than hook
    font_path = _get_font_path()
    border_w = max(3, fontsize // 20)

    # Escape for ffmpeg drawtext
    escaped = label_text.replace("'", "'\\''").replace(":", "\\:").replace("\\", "\\\\\\\\")

    # Position at ~65% from top (above the TikTok caption/buttons zone)
    y_pos = int(img_h * 0.65)

    drawtext = (
        f"drawtext=text='{escaped}'"
        f":fontfile={font_path}"
        f":fontsize={fontsize}"
        f":fontcolor=white"
        f":borderw={border_w}:bordercolor=black"
        f":x=(w-text_w)/2"
        f":y={y_pos}"
    )

    cmd = [
        "ffmpeg", "-y",
        "-i", image_path,
        "-vf", drawtext,
        "-q:v", "2",
        output_path,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    if result.returncode != 0:
        raise RuntimeError(f"FFmpeg label error: {result.stderr[-500:]}")
    return output_path


def generate_slideshow(hook, base_scene, slide_styles, output_dir,
                       product_name="", niche="AI", cta_style="soft",
                       model="imagen-4.0-generate-001", quality="high",
                       slide_labels=None):
    """Generate a complete TikTok slideshow.

    Args:
        hook: Hook text for slide 1
        base_scene: Locked scene description (same for all slides)
        slide_styles: List of 6 style variations (one per slide)
        output_dir: Directory to save slides
        product_name: Product being promoted
        niche: Content niche for hashtags
        cta_style: Caption CTA style
        model: OpenAI image model
        quality: Image quality
        slide_labels: Optional list of 6 short labels for each slide.
                      Slide 1 label is ignored (hook is used instead).
                      If None, slides 2-6 get no label.

    Returns:
        dict with:
            slides: list of 6 image paths
            caption: generated caption
            hook: the hook text
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    if len(slide_styles) != NUM_SLIDES:
        raise ValueError(f"Need exactly {NUM_SLIDES} slide styles, got {len(slide_styles)}")

    slides = []
    for i, style in enumerate(slide_styles):
        slide_num = i + 1
        print(f"Generating slide {slide_num}/{NUM_SLIDES}: {style[:50]}...")

        prompt = build_scene_prompt(base_scene, slide_num, style,
                                    product_context=product_name)
        raw_path = str(output_dir / f"slide_{slide_num:02d}_raw.png")

        # Route to the right image generator based on model name
        if model.startswith("gemini") or model.startswith("imagen"):
            generate_image_gemini(prompt, raw_path, model=model, size="1024x1536")
        else:
            generate_image(prompt, raw_path, model=model, size="1024x1536",
                           quality=quality)

        final_path = str(output_dir / f"slide_{slide_num:02d}.png")

        if slide_num == 1 and hook:
            # Slide 1: hook text overlay
            add_hook_overlay(raw_path, final_path, hook)
        elif slide_labels and len(slide_labels) >= slide_num and slide_labels[i]:
            # Slides 2-6: short label overlay
            add_label_overlay(raw_path, final_path, slide_labels[i])
        else:
            os.rename(raw_path, final_path)

        slides.append(final_path)

        print(f"  Saved: {final_path}")

    # Generate caption
    caption = generate_caption(hook, product_name, niche, cta_style)
    caption_path = str(output_dir / "caption.txt")
    with open(caption_path, "w") as f:
        f.write(caption)

    # Save metadata
    metadata = {
        "hook": hook,
        "base_scene": base_scene,
        "slide_styles": slide_styles,
        "product_name": product_name,
        "niche": niche,
        "model": model,
        "slides": [str(s) for s in slides],
        "caption": caption,
    }
    meta_path = str(output_dir / "metadata.json")
    with open(meta_path, "w") as f:
        json.dump(metadata, f, indent=2)

    print(f"\nSlideshow complete! {len(slides)} slides saved to {output_dir}")
    print(f"Caption saved to {caption_path}")

    return metadata


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python slideshow.py test")
        print("       python slideshow.py generate <hook> <scene> <output_dir>")
        sys.exit(1)

    if sys.argv[1] == "test":
        key = _get_openai_key()
        print(f"OpenAI key: {'found' if key else 'MISSING'}")
        print(f"Font: {'found' if os.path.exists(FONT) else 'MISSING'}")
        ffmpeg = subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True)
        print(f"FFmpeg: {ffmpeg.stdout.split(chr(10))[0] if ffmpeg.returncode == 0 else 'MISSING'}")
        print(f"Slide dimensions: {SLIDE_WIDTH}x{SLIDE_HEIGHT}")
        print(f"Hook font size: {int(SLIDE_HEIGHT * HOOK_FONT_SIZE_RATIO)}px")
        print("Ready to generate slideshows!")
