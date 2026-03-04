#!/usr/bin/env python3
"""Generate or edit images using Gemini/Imagen API.

Usage:
    python3 generate_image.py --prompt "description" --filename "output.png" [--resolution 1K|2K|4K] [--input-image path] [--api-key KEY]
"""
import argparse
import base64
import json
import os
import sys
import urllib.request


RESOLUTION_MAP = {
    "1K": "1:1",
    "2K": "1:1",
    "4K": "1:1",
}


def get_api_key(cli_key=None):
    if cli_key:
        return cli_key
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


def generate(prompt, output_path, api_key, resolution="1K", input_image=None):
    from google import genai
    from google.genai import types

    client = genai.Client(api_key=api_key)

    if input_image:
        with open(input_image, "rb") as f:
            img_data = f.read()
        img_b64 = base64.b64encode(img_data).decode()
        response = client.models.generate_content(
            model="gemini-3-pro-image-preview",
            contents=[
                types.Content(parts=[
                    types.Part(text=prompt),
                    types.Part(inline_data=types.Blob(mime_type="image/png", data=img_data)),
                ])
            ],
            config=types.GenerateContentConfig(
                response_modalities=["IMAGE", "TEXT"],
            ),
        )
        for part in response.candidates[0].content.parts:
            if part.inline_data and part.inline_data.mime_type.startswith("image/"):
                with open(output_path, "wb") as f:
                    f.write(part.inline_data.data)
                return output_path
        raise RuntimeError("No image in response")
    else:
        model = "gemini-3-pro-image-preview"
        response = client.models.generate_content(
            model=model,
            contents=prompt + " Generate only an image, no text response.",
            config=types.GenerateContentConfig(
                response_modalities=["IMAGE", "TEXT"],
            ),
        )
        for part in response.candidates[0].content.parts:
            if part.inline_data and part.inline_data.mime_type.startswith("image/"):
                with open(output_path, "wb") as f:
                    f.write(part.inline_data.data)
                return output_path
        raise RuntimeError("No image in response")


def main():
    parser = argparse.ArgumentParser(description="Generate/edit images with Gemini")
    parser.add_argument("--prompt", required=True, help="Image prompt or editing instructions")
    parser.add_argument("--filename", required=True, help="Output filename")
    parser.add_argument("--resolution", default="1K", choices=["1K", "2K", "4K"])
    parser.add_argument("--input-image", help="Path to input image for editing")
    parser.add_argument("--api-key", help="Gemini API key (overrides env)")
    args = parser.parse_args()

    api_key = get_api_key(args.api_key)
    if not api_key:
        print("Error: No API key provided. Set GEMINI_API_KEY or pass --api-key", file=sys.stderr)
        sys.exit(1)

    if args.input_image and not os.path.isfile(args.input_image):
        print(f"Error loading input image: {args.input_image} not found", file=sys.stderr)
        sys.exit(1)

    output_path = os.path.abspath(args.filename)
    result = generate(args.prompt, output_path, api_key, args.resolution, args.input_image)
    print(f"Saved: {result}")


if __name__ == "__main__":
    main()
