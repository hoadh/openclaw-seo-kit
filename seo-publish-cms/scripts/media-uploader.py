#!/usr/bin/env python3
"""
media-uploader.py — Upload image to WordPress media library via REST API.

Usage:
  python3 media-uploader.py <file_path> <alt_text>

Required env vars:
  WORDPRESS_URL   — Base URL of WordPress site (e.g. https://example.com)
  WORDPRESS_TOKEN — "username:application_password" string

Output JSON:
  {"media_id": int, "url": str}

Supported formats: jpg, jpeg, png, webp
"""

import json
import sys
import os
import base64
import mimetypes
import urllib.request
import urllib.error


SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}


def get_auth_header(token: str) -> str:
    encoded = base64.b64encode(token.encode("utf-8")).decode("utf-8")
    return f"Basic {encoded}"


def detect_mime_type(file_path: str) -> str:
    ext = os.path.splitext(file_path)[1].lower()
    mime_map = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".webp": "image/webp",
    }
    mime = mime_map.get(ext)
    if mime is None:
        guessed, _ = mimetypes.guess_type(file_path)
        mime = guessed or "application/octet-stream"
    return mime


def build_multipart_body(
    file_path: str, mime_type: str, alt_text: str
) -> tuple[bytes, str]:
    """Build a multipart/form-data body for the media upload request."""
    boundary = "----WPMediaUploadBoundary7f3a9b2c"
    filename = os.path.basename(file_path)

    with open(file_path, "rb") as f:
        file_data = f.read()

    parts = []

    # File field
    parts.append(
        f'--{boundary}\r\n'
        f'Content-Disposition: form-data; name="file"; filename="{filename}"\r\n'
        f'Content-Type: {mime_type}\r\n\r\n'
    )
    body = "".join(parts).encode("utf-8") + file_data + b"\r\n"

    # alt_text field
    alt_part = (
        f'--{boundary}\r\n'
        f'Content-Disposition: form-data; name="alt_text"\r\n\r\n'
        f'{alt_text}\r\n'
    )
    body += alt_part.encode("utf-8")
    body += f"--{boundary}--\r\n".encode("utf-8")

    content_type = f"multipart/form-data; boundary={boundary}"
    return body, content_type


def upload_media(
    base_url: str, auth_header: str, file_path: str, alt_text: str
) -> dict:
    mime_type = detect_mime_type(file_path)
    body, content_type = build_multipart_body(file_path, mime_type, alt_text)

    url = f"{base_url.rstrip('/')}/wp-json/wp/v2/media"
    req = urllib.request.Request(
        url,
        data=body,
        headers={
            "Authorization": auth_header,
            "Content-Type": content_type,
            "Accept": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            source_url = (
                result.get("source_url")
                or result.get("guid", {}).get("rendered", "")
            )
            return {"media_id": result["id"], "url": source_url}

    except urllib.error.HTTPError as e:
        body_text = e.read().decode("utf-8", errors="replace")
        if e.code == 401:
            sys.exit(
                "Auth failure (401): Check WORDPRESS_TOKEN — must be "
                "'username:application_password'. Generate in WP Admin > Users > "
                "Profile > Application Passwords."
            )
        if e.code == 413:
            sys.exit(
                "Upload failed (413): File too large. Increase upload_max_filesize "
                "in php.ini or use a smaller image."
            )
        sys.exit(f"API error ({e.code}): {body_text}")

    except urllib.error.URLError as e:
        sys.exit(f"Connection error: {e.reason}. Check WORDPRESS_URL is reachable.")


def main():
    if len(sys.argv) < 3:
        sys.exit(
            "Usage: python3 media-uploader.py <file_path> <alt_text>\n"
            "Example: python3 media-uploader.py ./hero.jpg 'Hero image'"
        )

    file_path = sys.argv[1]
    alt_text = sys.argv[2]

    if not os.path.isfile(file_path):
        sys.exit(f"Error: File not found — {file_path}")

    ext = os.path.splitext(file_path)[1].lower()
    if ext not in SUPPORTED_EXTENSIONS:
        sys.exit(
            f"Error: Unsupported file format '{ext}'. "
            f"Supported: {', '.join(sorted(SUPPORTED_EXTENSIONS))}"
        )

    wp_url = os.environ.get("WORDPRESS_URL", "").strip()
    wp_token = os.environ.get("WORDPRESS_TOKEN", "").strip()

    if not wp_url:
        sys.exit("Error: WORDPRESS_URL environment variable is not set.")
    if not wp_token:
        sys.exit("Error: WORDPRESS_TOKEN environment variable is not set.")

    auth_header = get_auth_header(wp_token)
    result = upload_media(wp_url, auth_header, file_path, alt_text)

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
