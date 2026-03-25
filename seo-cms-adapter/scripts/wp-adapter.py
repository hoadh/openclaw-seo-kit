#!/usr/bin/env python3
"""wp-adapter.py — WordPress CMS adapter implementing CMSAdapter interface.

Uses WordPress REST API v2 with Basic Auth (Application Passwords).

Required env vars:
    WORDPRESS_URL   — Base URL, e.g. https://example.com
    WORDPRESS_TOKEN — "username:application_password"
"""

import base64
import json
import mimetypes
import os
import re
import sys
import urllib.error
import urllib.request

# Allow running standalone and as imported module
_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _DIR)
from adapter_interface import CMSAdapter  # noqa: E402


class WordPressAdapter(CMSAdapter):
    """WordPress adapter using REST API v2."""

    def __init__(self):
        self.base_url = os.environ.get("WORDPRESS_URL", "").rstrip("/")
        self.token = os.environ.get("WORDPRESS_TOKEN", "")
        self._auth_header = ""

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _auth(self) -> str:
        if not self._auth_header:
            encoded = base64.b64encode(self.token.encode()).decode()
            self._auth_header = f"Basic {encoded}"
        return self._auth_header

    def _api(self, path: str) -> str:
        return f"{self.base_url}/wp-json/wp/v2{path}"

    def _request(self, url: str, data=None, headers=None, method=None) -> dict:
        """Send HTTP request and return parsed JSON response."""
        req_headers = {"Accept": "application/json", "Authorization": self._auth()}
        if headers:
            req_headers.update(headers)

        if data and not method:
            method = "POST"

        req = urllib.request.Request(
            url, data=data, headers=req_headers, method=method or "GET"
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"HTTP {exc.code} from {url}: {body}") from exc
        except urllib.error.URLError as exc:
            raise RuntimeError(f"Connection error: {exc.reason}") from exc

    # ------------------------------------------------------------------
    # Interface implementation
    # ------------------------------------------------------------------

    def authenticate(self) -> bool:
        if not self.base_url or not self.token:
            return False
        try:
            self._request(self._api("/users/me"))
            return True
        except RuntimeError:
            return False

    def create_post(
        self,
        title: str,
        content: str,
        slug: str,
        meta: dict,
        status: str = "draft",
    ) -> dict:
        payload: dict = {
            "title":   title,
            "content": content,
            "slug":    slug,
            "status":  status,
        }

        if meta.get("categories"):
            payload["categories"] = meta["categories"]
        if meta.get("tags"):
            payload["tags"] = meta["tags"]
        if meta.get("featured_media"):
            payload["featured_media"] = meta["featured_media"]

        # Yoast SEO + RankMath fields
        seo_meta = {}
        if meta.get("meta_title"):
            seo_meta["_yoast_wpseo_title"] = meta["meta_title"]
            seo_meta["rank_math_title"] = meta["meta_title"]
        if meta.get("meta_description"):
            seo_meta["_yoast_wpseo_metadesc"] = meta["meta_description"]
            seo_meta["rank_math_description"] = meta["meta_description"]
        if seo_meta:
            payload["meta"] = seo_meta

        body = json.dumps(payload).encode("utf-8")
        result = self._request(
            self._api("/posts"),
            data=body,
            headers={"Content-Type": "application/json"},
        )
        return {
            "post_id": result["id"],
            "url":     result.get("link", ""),
            "status":  result.get("status", status),
        }

    def upload_media(self, file_path: str, alt_text: str) -> str:
        if not os.path.isfile(file_path):
            return ""

        mime_type, _ = mimetypes.guess_type(file_path)
        mime_type = mime_type or "application/octet-stream"
        filename = os.path.basename(file_path)

        with open(file_path, "rb") as fh:
            file_data = fh.read()

        result = self._request(
            self._api("/media"),
            data=file_data,
            headers={
                "Content-Type":        mime_type,
                "Content-Disposition": f'attachment; filename="{filename}"',
            },
        )
        # Update alt text
        if result.get("id") and alt_text:
            update_url = self._api(f"/media/{result['id']}")
            body = json.dumps({"alt_text": alt_text}).encode("utf-8")
            try:
                self._request(
                    update_url,
                    data=body,
                    headers={"Content-Type": "application/json"},
                    method="POST",
                )
            except RuntimeError:
                pass  # non-fatal

        return result.get("source_url", "")

    def set_categories(self, post_id: int, categories: list) -> bool:
        body = json.dumps({"categories": categories}).encode("utf-8")
        try:
            self._request(
                self._api(f"/posts/{post_id}"),
                data=body,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            return True
        except RuntimeError:
            return False

    def set_tags(self, post_id: int, tags: list) -> bool:
        body = json.dumps({"tags": tags}).encode("utf-8")
        try:
            self._request(
                self._api(f"/posts/{post_id}"),
                data=body,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            return True
        except RuntimeError:
            return False

    def get_sitemap(self) -> list:
        sitemap_url = f"{self.base_url}/sitemap.xml"
        try:
            req = urllib.request.Request(sitemap_url, headers={"Accept": "*/*"})
            with urllib.request.urlopen(req, timeout=15) as resp:
                xml = resp.read().decode("utf-8", errors="replace")
            return re.findall(r"<loc>\s*(https?://[^\s<]+)\s*</loc>", xml)
        except Exception:
            return []

    def get_post_url(self, post_id: int) -> str:
        try:
            result = self._request(self._api(f"/posts/{post_id}"))
            return result.get("link", "")
        except RuntimeError:
            return ""


def create_adapter() -> WordPressAdapter:
    """Factory function called by get_adapter()."""
    return WordPressAdapter()
