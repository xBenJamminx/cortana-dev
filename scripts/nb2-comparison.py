"""Side-by-side comparison: Imagen 4.0 Ultra vs Nano Banana 2 (Gemini 3.1 Flash Image)"""

import os
import sys
import time
import subprocess

sys.path.insert(0, "/root/.openclaw/workspace")
from lib.imagegen import generate_image_gemini

OUTPUT_DIR = "/root/.openclaw/workspace/output/nb2-comparison"

# Expanded test: different styles and use cases
PROMPTS = [
    # --- SLEEP VIDEO SCENES (our main use case) ---
    {
        "name": "01_sleep_ancient_library",
        "category": "Sleep Video",
        "prompt": "A vast ancient library at twilight, towering bookshelves stretching into darkness, warm candlelight casting golden shadows on leather-bound books, dust motes floating in beams of fading sunlight through arched windows, photorealistic, cinematic lighting, 8K detail"
    },
    {
        "name": "02_sleep_ocean_night",
        "category": "Sleep Video",
        "prompt": "A vast calm ocean at night under a brilliant Milky Way galaxy, bioluminescent plankton glowing blue along the shoreline, gentle waves reflecting starlight, long exposure photography style, ultra high detail, serene and ethereal atmosphere"
    },
    # --- YOUTUBE THUMBNAILS ---
    {
        "name": "03_thumb_ai_automation",
        "category": "YT Thumbnail",
        "prompt": "A dramatic YouTube thumbnail style image: a confident business professional looking at a holographic dashboard of automated workflows, bold lighting with blue and orange contrast, clean modern office background, ultra sharp, eye-catching composition, professional photography"
    },
    {
        "name": "04_thumb_before_after",
        "category": "YT Thumbnail",
        "prompt": "Split-screen concept: left side shows a stressed person buried in paperwork and sticky notes in a messy office, right side shows the same person relaxed at a clean minimalist desk with a laptop showing green checkmarks, dramatic lighting contrast, professional photography, vivid colors"
    },
    # --- TEXT RENDERING (key differentiator) ---
    {
        "name": "05_text_quote_stoic",
        "category": "Text Rendering",
        "prompt": "An elegant motivational quote card on dark textured background: 'The obstacle is the way' in clean white serif typography, subtle golden ornamental border, stoic philosophy aesthetic, professional graphic design, sharp text rendering"
    },
    {
        "name": "06_text_social_post",
        "category": "Text Rendering",
        "prompt": "A modern social media graphic with the text 'AI won't replace you. A person using AI will.' in bold sans-serif white font on a gradient background of deep purple to electric blue, minimal clean design, Instagram post style"
    },
    # --- PORTRAIT / PERSON ---
    {
        "name": "07_portrait_founder",
        "category": "Portrait",
        "prompt": "A photorealistic portrait of a 30-something male entrepreneur in a modern co-working space, natural window light, wearing a casual button-down shirt, confident but approachable expression, shallow depth of field, shot on 85mm lens, editorial photography style"
    },
    # --- PRODUCT / MARKETING ---
    {
        "name": "08_product_saas_hero",
        "category": "Product/Marketing",
        "prompt": "A sleek SaaS product hero image showing a floating laptop with a beautiful dashboard interface, surrounded by abstract geometric shapes and soft gradient orbs in purple and blue, clean white background, modern tech aesthetic, product photography meets 3D render"
    },
    # --- ILLUSTRATION / CREATIVE ---
    {
        "name": "09_illustration_workflow",
        "category": "Illustration",
        "prompt": "A flat illustration of an AI-powered workflow: emails flowing into a brain-shaped AI processor, then splitting into organized categories with checkmarks, arrows, and icons, modern vector art style, blue and teal color palette, clean lines, infographic quality"
    },
    # --- CINEMATIC / DRAMATIC ---
    {
        "name": "10_cinematic_stoic",
        "category": "Cinematic",
        "prompt": "Marcus Aurelius standing alone on a Roman balcony overlooking a vast empire at golden hour, dramatic volumetric light through storm clouds, toga billowing in wind, epic scale, cinematic composition like a Ridley Scott film, photorealistic, anamorphic lens flare"
    },
]

def load_env():
    env_path = "/root/.openclaw/.env"
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    os.environ.setdefault(k, v)

def send_telegram(msg, topic=22):
    subprocess.run([
        "python3", "/root/.openclaw/workspace/lib/telegram.py",
        "--topic", str(topic), msg
    ], capture_output=True)

def send_photo(path, caption, topic=22):
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID", "")
    if not token or not chat_id:
        print(f"[WARN] Missing Telegram creds, skipping photo send for {path}")
        return
    cmd = [
        "curl", "-s", "-X", "POST",
        f"https://api.telegram.org/bot{token}/sendPhoto",
        "-F", f"chat_id={chat_id}",
        "-F", f"message_thread_id={topic}",
        "-F", f"photo=@{path}",
        "-F", f"caption={caption}",
    ]
    subprocess.run(cmd, capture_output=True)

def main():
    load_env()
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    results = []

    total = len(PROMPTS)
    for i, p in enumerate(PROMPTS):
        name = p["name"]
        prompt = p["prompt"]
        category = p.get("category", "")
        print(f"\n{'='*60}")
        print(f"[{i+1}/{total}] {name} ({category})")
        print(f"{'='*60}")

        # --- Imagen 4.0 Ultra ---
        imagen_path = os.path.join(OUTPUT_DIR, f"{name}_imagen_ultra.png")
        print(f"  Generating Imagen Ultra...")
        t0 = time.time()
        try:
            generate_image_gemini(
                prompt, imagen_path,
                model="imagen-4.0-ultra-generate-001",
                aspect_ratio="16:9"
            )
            imagen_time = round(time.time() - t0, 1)
            print(f"  Imagen Ultra: {imagen_time}s ✅")
        except Exception as e:
            imagen_time = None
            print(f"  Imagen Ultra FAILED: {e}")

        # --- Nano Banana 2 (Gemini 3.1 Flash Image) ---
        nb2_path = os.path.join(OUTPUT_DIR, f"{name}_nb2.png")
        print(f"  Generating Nano Banana 2...")
        t0 = time.time()
        try:
            generate_image_gemini(
                prompt, nb2_path,
                model="gemini-3.1-flash-image-preview",
                aspect_ratio="16:9"
            )
            nb2_time = round(time.time() - t0, 1)
            print(f"  Nano Banana 2: {nb2_time}s ✅")
        except Exception as e:
            nb2_time = None
            print(f"  Nano Banana 2 FAILED: {e}")

        results.append({
            "name": name,
            "category": category,
            "imagen_path": imagen_path,
            "imagen_time": imagen_time,
            "nb2_path": nb2_path,
            "nb2_time": nb2_time,
        })

        # Send pair to Telegram
        # Strip number prefix for display
        label = name.split("_", 1)[1].replace("_", " ").title() if "_" in name else name
        cat = f"[{category}] " if category else ""
        if imagen_time is not None:
            send_photo(imagen_path, f"🅰️ IMAGEN ULTRA - {cat}{label}\n⏱ {imagen_time}s | $0.06")
            time.sleep(1)
        if nb2_time is not None:
            send_photo(nb2_path, f"🅱️ NANO BANANA 2 - {cat}{label}\n⏱ {nb2_time}s | $0.067")
            time.sleep(1)

    # Summary
    print("\n" + "="*60)
    print("RESULTS SUMMARY")
    print("="*60)
    summary_lines = ["📊 Comparison Complete! 10 prompts x 2 models = 20 images\n"]

    # Group by category
    categories = {}
    for r in results:
        cat = r.get("category", "Other")
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(r)

    for cat, items in categories.items():
        summary_lines.append(f"\n{cat}:")
        for r in items:
            it = f"{r['imagen_time']}s" if r['imagen_time'] else "FAIL"
            nt = f"{r['nb2_time']}s" if r['nb2_time'] else "FAIL"
            label = r['name'].split("_", 1)[1].replace('_', ' ').title() if "_" in r['name'] else r['name']
            summary_lines.append(f"  • {label}: Imagen {it} vs NB2 {nt}")
            print(f"  {label}: Imagen={it}  NB2={nt}")

    # Speed totals
    imagen_total = sum(r['imagen_time'] for r in results if r['imagen_time'])
    nb2_total = sum(r['nb2_time'] for r in results if r['nb2_time'])
    imagen_count = sum(1 for r in results if r['imagen_time'])
    nb2_count = sum(1 for r in results if r['nb2_time'])

    summary_lines.append(f"\n⏱ Avg Speed:")
    if imagen_count: summary_lines.append(f"  Imagen Ultra: {round(imagen_total/imagen_count, 1)}s avg")
    if nb2_count: summary_lines.append(f"  Nano Banana 2: {round(nb2_total/nb2_count, 1)}s avg")

    summary_lines.append("\n🅰️ = Imagen 4.0 Ultra ($0.06/img)")
    summary_lines.append("🅱️ = Nano Banana 2 ($0.067/img)")
    summary_lines.append("\nScroll up to see all pairs. Which model wins for each use case? 💜")

    send_telegram("\n".join(summary_lines), topic=22)
    print("\nDone! Results sent to Telegram.")

if __name__ == "__main__":
    main()
