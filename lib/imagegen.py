"""Image generation library. Gemini/Imagen (primary), OpenAI DALL-E (fallback).

Usage:
    from lib.imagegen import generate_image_gemini, generate_image

    # Imagen 4 Ultra (default)
    generate_image_gemini("a cat in space", "/tmp/cat.png", model="imagen-4.0-ultra-generate-001", aspect_ratio="16:9")

    # OpenAI fallback
    generate_image("a cat in space", "/tmp/cat.png")
"""

import base64
import json
import os
import urllib.request


def _get_openai_key():
    key = os.environ.get("OPENAI_API_KEY", "")
    if not key:
        env_path = "/root/.openclaw/.env"
        if os.path.exists(env_path):
            with open(env_path) as f:
                for line in f:
                    if line.startswith("OPENAI_API_KEY="):
                        key = line.strip().split("=", 1)[1]
                        break
    return key


def _get_gemini_key():
    key = os.environ.get("GEMINI_API_KEY", "")
    if not key:
        env_path = "/root/.openclaw/.env"
        if os.path.exists(env_path):
            with open(env_path) as f:
                for line in f:
                    if line.startswith("GEMINI_API_KEY="):
                        key = line.strip().split("=", 1)[1]
                        break
    return key


def generate_image_gemini(prompt, output_path, model="gemini-3.1-flash-image-preview",
                          size="1024x1536", aspect_ratio=None):
    """Generate an image using Gemini's image generation models.

    Supported models:
        - gemini-3.1-flash-image-preview (Nano Banana 2, default - best quality/price)
        - gemini-3-pro-image-preview (Nano Banana Pro - premium tier)
        - gemini-2.5-flash-image (Nano Banana - cheapest)
        - imagen-4.0-ultra-generate-001 (Imagen 4 Ultra)
        - imagen-4.0-generate-001 (Imagen 4)
        - imagen-4.0-fast-generate-001 (Imagen 4 Fast)

    Aspect ratios for Imagen models: "1:1", "3:4", "4:3", "9:16", "16:9"
    """
    from google import genai

    key = _get_gemini_key()
    if not key:
        raise RuntimeError("GEMINI_API_KEY not found")

    client = genai.Client(api_key=key)

    if model.startswith("imagen"):
        from google.genai import types
        ar = aspect_ratio or "16:9"
        result = client.models.generate_images(
            model=model,
            prompt=prompt,
            config=types.GenerateImagesConfig(
                number_of_images=1,
                aspect_ratio=ar,
            ),
        )
        if result.generated_images:
            img_bytes = result.generated_images[0].image.image_bytes
            with open(output_path, "wb") as f:
                f.write(img_bytes)
        else:
            raise RuntimeError("Imagen returned no images")
    else:
        from google.genai import types
        response = client.models.generate_content(
            model=model,
            contents=prompt + " Generate only an image, no text response.",
            config=types.GenerateContentConfig(
                response_modalities=["IMAGE", "TEXT"],
            ),
        )
        found = False
        for part in response.candidates[0].content.parts:
            if part.inline_data and part.inline_data.mime_type.startswith("image/"):
                with open(output_path, "wb") as f:
                    f.write(part.inline_data.data)
                found = True
                break
        if not found:
            raise RuntimeError(f"Gemini returned no image. Response: {response.text[:200] if response.text else 'empty'}")

    return output_path


def generate_image(prompt, output_path, model="gpt-image-1.5", size="1024x1536",
                   quality="high"):
    """Generate a single image using OpenAI's image API (fallback).

    Args:
        prompt: Image generation prompt
        output_path: Path to save the PNG
        model: OpenAI image model
        size: Image dimensions
        quality: "low", "medium", or "high"

    Returns:
        output_path on success
    """
    key = _get_openai_key()
    if not key:
        raise RuntimeError("OPENAI_API_KEY not found")

    data = json.dumps({
        "model": model,
        "prompt": prompt,
        "n": 1,
        "size": size,
        "quality": quality,
    }).encode()

    req = urllib.request.Request(
        "https://api.openai.com/v1/images/generations",
        data=data,
        headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
        },
    )

    resp = urllib.request.urlopen(req, timeout=120)
    result = json.loads(resp.read())

    img_data = result["data"][0]
    if "b64_json" in img_data:
        img_bytes = base64.b64decode(img_data["b64_json"])
        with open(output_path, "wb") as f:
            f.write(img_bytes)
    elif "url" in img_data:
        urllib.request.urlretrieve(img_data["url"], output_path)
    else:
        raise RuntimeError(f"Unexpected response format: {list(img_data.keys())}")

    return output_path
