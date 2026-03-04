"""FINAL comparison: Imagen Ultra vs NB2 - explicitly specifying models (no defaults)"""

import os
import sys
import time
import subprocess

sys.path.insert(0, "/root/.openclaw/workspace")
from lib.imagegen import generate_image_gemini

OUTPUT_DIR = "/root/.openclaw/workspace/output/nb2-vs-imagen-final"

# 5 diverse prompts across styles
PROMPTS = [
    {
        "name": "pixar_robot",
        "style": "Pixar 3D",
        "prompt": "A adorable Pixar-style 3D rendered robot sitting on a park bench reading a tiny book, big expressive glossy eyes, soft ambient occlusion, subsurface scattering, warm sunset lighting, Pixar movie quality rendering, cute and heartwarming scene"
    },
    {
        "name": "cyberpunk_street",
        "style": "Cyberpunk",
        "prompt": "A rain-soaked cyberpunk street at night, towering neon signs in Japanese and English reflecting off wet pavement, a lone figure with an umbrella walking past steaming food stalls, holographic advertisements, dense urban atmosphere, Blade Runner aesthetic, electric pink and cyan color palette"
    },
    {
        "name": "stoic_cinematic",
        "style": "Cinematic",
        "prompt": "Marcus Aurelius standing alone on a Roman balcony overlooking a vast empire at golden hour, dramatic volumetric light through storm clouds, toga billowing in wind, epic scale, cinematic composition like a Ridley Scott film, photorealistic, anamorphic lens flare"
    },
    {
        "name": "watercolor_venice",
        "style": "Watercolor",
        "prompt": "A loose impressionist watercolor painting of Venice canals at golden hour, gondolas on shimmering water, warm ochre and terracotta buildings, wet-on-wet technique with paint bleeding naturally, visible paper texture, artistic and painterly, gallery quality watercolor"
    },
    {
        "name": "food_sushi",
        "style": "Food Photo",
        "prompt": "A gourmet sushi platter on a minimalist ceramic plate, fresh salmon and tuna nigiri with glistening fish, wasabi and pickled ginger garnish, natural light from a window, shallow depth of field, food magazine cover quality, appetizing warm tones"
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
    result = subprocess.run(cmd, capture_output=True, text=True)
    if '"ok":false' in result.stdout:
        print(f"  [WARN] Telegram send failed: {result.stdout[:200]}")


def main():
    load_env()
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    send_telegram("🔬 REAL comparison this time! Explicitly passing model names.\n\n5 prompts x 2 models. For each prompt you'll see:\n🅰️ = Imagen 4.0 Ultra ($0.06)\n🅱️ = Nano Banana 2 ($0.067)\n\nIncoming! 🔥", topic=22)

    results = []
    total = len(PROMPTS)

    for i, p in enumerate(PROMPTS):
        name = p["name"]
        prompt = p["prompt"]
        style = p["style"]
        print(f"\n{'='*60}")
        print(f"[{i+1}/{total}] {style}: {name}")
        print(f"{'='*60}")

        # --- IMAGEN 4.0 ULTRA (explicit model) ---
        imagen_path = os.path.join(OUTPUT_DIR, f"{name}_IMAGEN.png")
        print(f"  Generating Imagen 4.0 Ultra...")
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

        # --- NANO BANANA 2 (explicit model) ---
        nb2_path = os.path.join(OUTPUT_DIR, f"{name}_NB2.png")
        print(f"  Generating Nano Banana 2...")
        t0 = time.time()
        try:
            generate_image_gemini(
                prompt, nb2_path,
                model="gemini-3.1-flash-image-preview",
                aspect_ratio="16:9"
            )
            nb2_time = round(time.time() - t0, 1)
            print(f"  NB2: {nb2_time}s ✅")
        except Exception as e:
            nb2_time = None
            print(f"  NB2 FAILED: {e}")

        results.append({
            "name": name,
            "style": style,
            "imagen_time": imagen_time,
            "nb2_time": nb2_time,
        })

        # Send pair to Telegram - labeled clearly
        if imagen_time is not None:
            send_photo(imagen_path, f"🅰️ IMAGEN ULTRA - {style}\n⏱ {imagen_time}s | $0.06/img")
            time.sleep(1)
        if nb2_time is not None:
            send_photo(nb2_path, f"🅱️ NANO BANANA 2 - {style}\n⏱ {nb2_time}s | $0.067/img")
            time.sleep(1)

        # Separator between pairs
        if i < total - 1:
            send_telegram(f"{'─' * 20}\nNext style: {PROMPTS[i+1]['style']}...", topic=22)
            time.sleep(0.5)

    # Summary
    print("\n" + "=" * 60)
    print("FINAL RESULTS")
    print("=" * 60)

    lines = ["📊 Side-by-Side Complete! (models explicitly specified this time)\n"]
    for r in results:
        it = f"{r['imagen_time']}s" if r['imagen_time'] else "FAIL"
        nt = f"{r['nb2_time']}s" if r['nb2_time'] else "FAIL"
        lines.append(f"• {r['style']}: Imagen {it} vs NB2 {nt}")

    itimes = [r['imagen_time'] for r in results if r['imagen_time']]
    ntimes = [r['nb2_time'] for r in results if r['nb2_time']]
    if itimes:
        lines.append(f"\n⏱ Imagen avg: {round(sum(itimes)/len(itimes), 1)}s")
    if ntimes:
        lines.append(f"⏱ NB2 avg: {round(sum(ntimes)/len(ntimes), 1)}s")

    lines.append("\n🅰️ = Imagen 4.0 Ultra ($0.06/img)")
    lines.append("🅱️ = Nano Banana 2 ($0.067/img)")
    lines.append("\nNow you can ACTUALLY compare them side by side! Which wins? 💜")

    send_telegram("\n".join(lines), topic=22)
    print("\nDone!")


if __name__ == "__main__":
    main()
