#!/usr/bin/env python3
"""haravan-adapter.py — Haravan CMS adapter implementing CMSAdapter interface.

Haravan is a Vietnamese e-commerce platform with a Shopify-compatible REST API
subset. Key differences from Shopify: different base URL pattern (no version
segment in path), X-Haravan-Access-Token auth header.
Inherits shared logic from ShopifyBaseAdapter.

Required env vars:
    HARAVAN_STORE_URL     — Store URL, e.g. https://mystore.haravan.com
    HARAVAN_ACCESS_TOKEN  — Haravan app access token
    HARAVAN_BLOG_ID       — Numeric ID of the target blog
"""

import importlib.util
import os
import sys

_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _DIR)

# Load base adapter (kebab-case filename requires importlib)
def _load_module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

_base = _load_module(os.path.join(_DIR, "shopify-base-adapter.py"), "shopify_base_adapter")
ShopifyBaseAdapter = _base.ShopifyBaseAdapter


class HaravanAdapter(ShopifyBaseAdapter):
    """Haravan adapter using Admin REST API (Shopify-compatible subset)."""

    def __init__(self):
        super().__init__(
            store_url=os.environ.get("HARAVAN_STORE_URL", ""),
            access_token=os.environ.get("HARAVAN_ACCESS_TOKEN", ""),
            blog_id=os.environ.get("HARAVAN_BLOG_ID", ""),
        )

    def _api(self, path: str) -> str:
        # Haravan admin API: /admin/<resource>.json (no version segment)
        return f"{self.store_url}/admin{path}"

    def _auth_headers(self) -> dict:
        return {"X-Haravan-Access-Token": self.access_token}

    def authenticate(self) -> bool:
        if not self.store_url or not self.access_token:
            return False
        try:
            self._request(self._api("/shop.json"))
            return True
        except RuntimeError:
            return False

    def upload_media(self, file_path: str, alt_text: str) -> str:
        """Upload image via Haravan theme asset API and return CDN URL."""
        return self.upload_media_via_theme_asset(file_path)


def create_adapter() -> HaravanAdapter:
    """Factory function called by get_adapter()."""
    return HaravanAdapter()
