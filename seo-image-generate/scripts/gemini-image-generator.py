#!/usr/bin/env python3
"""Generate images via Google Gemini API (Imagen 4).

Reads a JSON prompt object from stdin and generates an image,
saving it to the specified output path.

Usage:
    echo '{"prompt": "...", "width": 1200, "height": 630}' | \
        python3 gemini-image-generator.py --output images/featured.webp

    python3 gemini-image-generator.py --input prompts.json --output-dir images/

Environment:
    GOOGLE_API_KEY — required, Gemini API key

Exit codes:
    0 — success
    1 — API error or generation failure
    2 — input/config error
"""

import base64
import json
import os
import sys
import urllib.error
import urllib.request


# Gemini API endpoint for image generation
API_BASE = "https://generativelanguage.googleapis.com/v1beta"
MODEL = "imagen-3.0-generate-002"


def get_api_key():
    """Read GOOGLE_API_KEY from environment."""
    key = os.environ.get("GOOGLE_API_KEY", "")
    if not key:
        print("Error: GOOGLE_API_KEY not set", file=sys.stderr)
        sys.exit(2)
    return key


def generate_image(prompt, width, height, api_key):
    """Call Gemini Imagen API to generate an image.

    Returns raw image bytes (PNG) or None on failure.
    """
    url = f"{API_BASE}/models/{MODEL}:predict?key={api_key}"

    payload = {
        "instances": [{"prompt": prompt}],
        "parameters": {
            "sampleCount": 1,
            "aspectRatio": _aspect_ratio(width, height),
            "outputOptions": {"mimeType": "image/png"}
        }
    }

    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            result = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        print(f"Error: Gemini API {e.code}: {body}", file=sys.stderr)
        return None
    except urllib.error.URLError as e:
        print(f"Error: network failure: {e.reason}", file=sys.stderr)
        return None

    # Extract base64 image from response
    predictions = result.get("predictions", [])
    if not predictions:
        print("Error: no predictions in API response", file=sys.stderr)
        return None

    b64_data = predictions[0].get("bytesBase64Encoded", "")
    if not b64_data:
        print("Error: no image data in prediction", file=sys.stderr)
        return None

    return base64.b64decode(b64_data)


def _aspect_ratio(width, height):
    """Map pixel dimensions to Imagen aspect ratio string."""
    ratio = width / height if height else 1.0
    # Imagen supported ratios: 1:1, 3:4, 4:3, 9:16, 16:9
    if ratio >= 1.7:    # 1200x630 ≈ 1.9:1 -> closest is 16:9
        return "16:9"
    elif ratio >= 1.2:  # wider than tall
        return "4:3"
    elif ratio <= 0.6:  # tall
        return "9:16"
    elif ratio <= 0.8:
        return "3:4"
    else:
        return "1:1"


def save_image(image_bytes, output_path):
    """Save image bytes to file, creating directories as needed."""
    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    with open(output_path, "wb") as f:
        f.write(image_bytes)

    print(f"Saved: {output_path} ({len(image_bytes)} bytes)",
          file=sys.stderr)


def process_single(prompt_obj, output_path, api_key):
    """Generate one image from a prompt object."""
    prompt = prompt_obj.get("prompt", "")
    width = prompt_obj.get("width", 1200)
    height = prompt_obj.get("height", 630)

    if not prompt:
        print("Error: empty prompt", file=sys.stderr)
        return False

    image_bytes = generate_image(prompt, width, height, api_key)
    if not image_bytes:
        return False

    save_image(image_bytes, output_path)
    return True


def process_batch(prompts, output_dir, api_key):
    """Generate images for a batch of prompts (from image-prompt-builder)."""
    results = []
    for item in prompts:
        filename = item.get("filename", "image.png")
        output_path = os.path.join(output_dir, filename)

        # Set dimensions based on type
        if item.get("type") == "featured":
            item.setdefault("width", 1200)
            item.setdefault("height", 630)
        else:
            item.setdefault("width", 800)
            item.setdefault("height", 450)

        success = process_single(item, output_path, api_key)
        results.append({
            "filename": filename,
            "path": output_path,
            "success": success
        })

    return results


def main():
    api_key = get_api_key()

    # Parse args
    output_path = None
    output_dir = None
    input_file = None

    args = sys.argv[1:]
    i = 0
    while i < len(args):
        if args[i] == "--output" and i + 1 < len(args):
            output_path = args[i + 1]
            i += 2
        elif args[i] == "--output-dir" and i + 1 < len(args):
            output_dir = args[i + 1]
            i += 2
        elif args[i] == "--input" and i + 1 < len(args):
            input_file = args[i + 1]
            i += 2
        else:
            print(f"Unknown arg: {args[i]}", file=sys.stderr)
            sys.exit(2)

    # Read input
    if input_file:
        with open(input_file, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        raw = sys.stdin.read().strip()
        if not raw:
            print("Error: no input (stdin or --input)", file=sys.stderr)
            sys.exit(2)
        data = json.loads(raw)

    # Batch mode (array from image-prompt-builder) or single mode (object)
    if isinstance(data, list):
        if not output_dir:
            output_dir = "images"
        results = process_batch(data, output_dir, api_key)
        success_count = sum(1 for r in results if r["success"])
        print(json.dumps({
            "total": len(results),
            "success": success_count,
            "failed": len(results) - success_count,
            "images": results
        }, indent=2))
    else:
        if not output_path:
            output_path = "images/generated.png"
        ok = process_single(data, output_path, api_key)
        print(json.dumps({
            "path": output_path,
            "success": ok
        }))
        if not ok:
            sys.exit(1)


if __name__ == "__main__":
    main()
