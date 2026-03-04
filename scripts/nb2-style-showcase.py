"""NB2 Style Showcase: 10 creative styles, Nano Banana 2 only"""

import os
import sys
import time
import subprocess

sys.path.insert(0, "/root/.openclaw/workspace")
from lib.imagegen import generate_image_gemini

OUTPUT_DIR = "/root/.openclaw/workspace/output/nb2-styles"

PROMPTS = [
    {
        "name": "pixar_robot",
        "style": "Pixar 3D",
        "prompt": "A adorable Pixar-style 3D rendered robot sitting on a park bench reading a tiny book, big expressive glossy eyes, soft ambient occlusion, subsurface scattering, warm sunset lighting, Pixar movie quality rendering, cute and heartwarming scene"
    },
    {
        "name": "ghibli_forest",
        "style": "Studio Ghibli",
        "prompt": "A magical forest spirit standing in a lush enchanted woodland, Studio Ghibli animation style, soft watercolor-like colors, dappled sunlight through enormous ancient trees, mystical floating particles, Hayao Miyazaki aesthetic, hand-painted feel, whimsical and serene"
    },
    {
        "name": "watercolor_venice",
        "style": "Watercolor",
        "prompt": "A loose impressionist watercolor painting of Venice canals at golden hour, gondolas on shimmering water, warm ochre and terracotta buildings, wet-on-wet technique with paint bleeding naturally, visible paper texture, artistic and painterly, gallery quality watercolor"
    },
    {
        "name": "oil_painting_storm",
        "style": "Oil Painting",
        "prompt": "A dramatic oil painting of a ship battling a massive storm at sea, in the style of J.M.W. Turner, thick impasto brushstrokes of crashing waves, dark moody clouds with breaks of golden light, classical maritime painting, museum quality, visible canvas texture"
    },
    {
        "name": "retro_mars_poster",
        "style": "Retro Poster",
        "prompt": "A vintage 1960s space age travel poster advertising 'VISIT MARS', retro futurism style, bold flat colors in burnt orange and teal, stylized rocket ship and red planet landscape, art deco inspired typography, grainy texture overlay, mid-century modern graphic design"
    },
    {
        "name": "isometric_city",
        "style": "Isometric",
        "prompt": "A detailed isometric illustration of a futuristic smart city block, flying cars between buildings, rooftop gardens, holographic billboards, tiny people walking on elevated walkways, warm evening lighting, cute miniature style with incredible detail, clean vector-like rendering"
    },
    {
        "name": "flat_vector_workflow",
        "style": "Flat Vector",
        "prompt": "A clean flat vector illustration of an AI assistant managing someone's daily life, email icons, calendar blocks, task lists, and chat bubbles all flowing into a friendly robot character in the center, modern SaaS illustration style, limited color palette of blue teal and coral, geometric shapes"
    },
    {
        "name": "comic_book_hero",
        "style": "Comic Book",
        "prompt": "A dynamic comic book panel of a superhero landing on a rooftop at night, dramatic foreshortening, bold black ink outlines, halftone dot shading, speed lines radiating outward, city skyline in background, classic Marvel/DC comic art style, vibrant primary colors, POW energy"
    },
    {
        "name": "cyberpunk_street",
        "style": "Cyberpunk Neon",
        "prompt": "A rain-soaked cyberpunk street at night, towering neon signs in Japanese and English reflecting off wet pavement, a lone figure with an umbrella walking past steaming food stalls, holographic advertisements, dense urban atmosphere, Blade Runner aesthetic, electric pink and cyan color palette"
    },
    {
        "name": "lowpoly_landscape",
        "style": "Low-Poly Geometric",
        "prompt": "A beautiful low-poly geometric landscape of mountains, a lake, and pine trees at sunset, faceted triangular shapes creating depth, soft gradient sky from purple to orange, crystal-clear geometric water reflections, modern digital art, clean edges, stylized minimalism"
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
        style = p["style"]
        print(f"\n{'='*60}")
        print(f"[{i+1}/{total}] {style}: {name}")
        print(f"{'='*60}")

        out_path = os.path.join(OUTPUT_DIR, f"{name}.png")
        print(f"  Generating NB2...")
        t0 = time.time()
        try:
            generate_image_gemini(
                prompt, out_path,
                model="gemini-3.1-flash-image-preview",
                aspect_ratio="16:9"
            )
            gen_time = round(time.time() - t0, 1)
            print(f"  Done: {gen_time}s ✅")
        except Exception as e:
            gen_time = None
            print(f"  FAILED: {e}")

        results.append({
            "name": name,
            "style": style,
            "path": out_path,
            "time": gen_time,
        })

        # Send to Telegram
        if gen_time is not None:
            send_photo(out_path, f"🎨 NB2 Style: {style}\n⏱ {gen_time}s")
            time.sleep(1)

    # Summary
    print("\n" + "=" * 60)
    print("STYLE SHOWCASE COMPLETE")
    print("=" * 60)

    summary_lines = ["🎨 NB2 Style Showcase Complete!\n"]
    for r in results:
        t = f"{r['time']}s" if r['time'] else "FAIL"
        summary_lines.append(f"• {r['style']}: {t}")
        print(f"  {r['style']}: {t}")

    times = [r['time'] for r in results if r['time']]
    if times:
        summary_lines.append(f"\n⏱ Avg: {round(sum(times)/len(times), 1)}s per image")
        summary_lines.append(f"💰 Cost: ~$0.067/img x {len(times)} = ~${round(0.067 * len(times), 2)}")

    summary_lines.append("\nAll generated with gemini-3.1-flash-image-preview (Nano Banana 2) 🍌")
    summary_lines.append("Which styles are your favorites? 💜")

    send_telegram("\n".join(summary_lines), topic=22)
    print("\nDone!")


if __name__ == "__main__":
    main()
