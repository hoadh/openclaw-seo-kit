#!/usr/bin/env python3
"""shopify-base-adapter.py — Base class for Shopify-compatible REST API adapters.

Encapsulates shared logic used by both ShopifyAdapter and HaravanAdapter:
  - HTTP request helper (_request)
  - Article creation payload builder (_build_article_payload)
  - Tag update helper (_update_article_tags)
  - Sitemap fetcher (get_sitemap)
  - Article URL resolver (get_post_url)
  - Theme-based asset upload (upload_media_via_theme_asset)

Subclasses must implement:
  - _api(self, path: str) -> str      — constructs full API URL for a given path
  - _auth_headers(self) -> dict       — returns auth headers for this platform
  - authenticate(self) -> bool        — validates credentials
"""

import base64
import json
import mimetypes
import os
import re
import sys
import urllib.error
import urllib.request

_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _DIR)
from adapter_interface import CMSAdapter  # noqa: E402


class ShopifyBaseAdapter(CMSAdapter):
    """Shared base for Shopify-compatible REST API adapters (Shopify, Haravan)."""

    def __init__(self, store_url: str, access_token: str, blog_id: str):
        self.store_url = store_url.rstrip("/")
        self.access_token = access_token
        self.blog_id = blog_id

    # ------------------------------------------------------------------
    # Subclass contract
    # ------------------------------------------------------------------

    def _api(self, path: str) -> str:
        """Construct full API URL for the given resource path."""
        raise NotImplementedError

    def _auth_headers(self) -> dict:
        """Return platform-specific auth headers."""
        raise NotImplementedError

    def authenticate(self) -> bool:
        raise NotImplementedError

    # ------------------------------------------------------------------
    # Shared HTTP helper
    # ------------------------------------------------------------------

    def _request(self, url: str, data=None, headers=None, method=None) -> dict:
        req_headers = {"Accept": "application/json"}
        req_headers.update(self._auth_headers())
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
    # Shared article operations
    # ------------------------------------------------------------------

    def _build_article_payload(
        self, title: str, content: str, slug: str, meta: dict, status: str
    ) -> dict:
        """Build the article dict for POST/PUT body (platform-agnostic fields)."""
        published = status not in ("draft", "hidden")
        payload = {
            "title":      title,
            "body_html":  content,
            "handle":     slug,
            "published":  published,
            "title_tag":  meta.get("meta_title", title),
            "metafields_global_description_tag": meta.get("meta_description", ""),
        }
        if meta.get("tags"):
            payload["tags"] = ", ".join(str(t) for t in meta["tags"])
        return payload

    def create_post(
        self,
        title: str,
        content: str,
        slug: str,
        meta: dict,
        status: str = "draft",
    ) -> dict:
        if not self.blog_id:
            raise RuntimeError(
                f"{self.__class__.__name__}: blog_id env var is not set"
            )
        article_payload = self._build_article_payload(title, content, slug, meta, status)
        published = article_payload["published"]

        url = self._api(f"/blogs/{self.blog_id}/articles.json")
        body = json.dumps({"article": article_payload}).encode("utf-8")
        result = self._request(url, data=body, headers={"Content-Type": "application/json"})
        article = result.get("article", {})
        return {
            "post_id": article.get("id", 0),
            "url":     f"{self.store_url}/blogs/{self.blog_id}/{article.get('handle', slug)}",
            "status":  "draft" if not published else "published",
        }

    def set_categories(self, post_id: int, categories: list) -> bool:
        # Shopify-compatible blogs do not support hierarchical categories
        return True

    def set_tags(self, post_id: int, tags: list) -> bool:
        if not self.blog_id:
            return False
        tag_str = ", ".join(str(t) for t in tags)
        body = json.dumps({"article": {"tags": tag_str}}).encode("utf-8")
        try:
            self._request(
                self._api(f"/blogs/{self.blog_id}/articles/{post_id}.json"),
                data=body,
                headers={"Content-Type": "application/json"},
                method="PUT",
            )
            return True
        except RuntimeError:
            return False

    def get_sitemap(self) -> list:
        sitemap_url = f"{self.store_url}/sitemap.xml"
        try:
            req = urllib.request.Request(sitemap_url, headers={"Accept": "*/*"})
            with urllib.request.urlopen(req, timeout=15) as resp:
                xml = resp.read().decode("utf-8", errors="replace")
            return re.findall(r"<loc>\s*(https?://[^\s<]+)\s*</loc>", xml)
        except Exception:
            return []

    def get_post_url(self, post_id: int) -> str:
        if not self.blog_id:
            return ""
        try:
            result = self._request(
                self._api(f"/blogs/{self.blog_id}/articles/{post_id}.json")
            )
            handle = result.get("article", {}).get("handle", "")
            return f"{self.store_url}/blogs/{self.blog_id}/{handle}" if handle else ""
        except RuntimeError:
            return ""

    # ------------------------------------------------------------------
    # Shared theme-asset media upload
    # ------------------------------------------------------------------

    def upload_media_via_theme_asset(self, file_path: str) -> str:
        """Upload a file as a theme asset and return its CDN URL.

        Fetches the main theme ID, then PUTs the file as a base64 attachment.
        Returns empty string on any error.
        """
        if not os.path.isfile(file_path):
            return ""

        mime_type, _ = mimetypes.guess_type(file_path)
        mime_type = mime_type or "application/octet-stream"
        filename = os.path.basename(file_path)

        with open(file_path, "rb") as fh:
            encoded = base64.b64encode(fh.read()).decode("utf-8")

        asset_payload = {
            "asset": {
                "key":          f"assets/{filename}",
                "attachment":   encoded,
                "content_type": mime_type,
            }
        }

        try:
            themes = self._request(self._api("/themes.json"))
            main_theme = next(
                (t for t in themes.get("themes", []) if t.get("role") == "main"),
                None,
            )
            if not main_theme:
                return ""

            theme_id = main_theme["id"]
            url = self._api(f"/themes/{theme_id}/assets.json")
            body = json.dumps(asset_payload).encode("utf-8")
            result = self._request(
                url, data=body,
                headers={"Content-Type": "application/json"},
                method="PUT",
            )
            return result.get("asset", {}).get("public_url", "")
        except RuntimeError:
            return ""
