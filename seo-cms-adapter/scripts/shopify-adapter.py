#!/usr/bin/env python3
"""shopify-adapter.py — Shopify CMS adapter implementing CMSAdapter interface.

Uses Shopify Admin REST API 2024-01 (not GraphQL).
Inherits shared logic from ShopifyBaseAdapter.

Required env vars:
    SHOPIFY_STORE_URL     — Store URL, e.g. https://mystore.myshopify.com
    SHOPIFY_ACCESS_TOKEN  — Private/Custom App access token
    SHOPIFY_BLOG_ID       — Numeric ID of the target blog
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

_API_VERSION = "2024-01"


class ShopifyAdapter(ShopifyBaseAdapter):
    """Shopify adapter using Admin REST API 2024-01."""

    def __init__(self):
        super().__init__(
            store_url=os.environ.get("SHOPIFY_STORE_URL", ""),
            access_token=os.environ.get("SHOPIFY_ACCESS_TOKEN", ""),
            blog_id=os.environ.get("SHOPIFY_BLOG_ID", ""),
        )

    def _api(self, path: str) -> str:
        return f"{self.store_url}/admin/api/{_API_VERSION}{path}"

    def _auth_headers(self) -> dict:
        return {"X-Shopify-Access-Token": self.access_token}

    def authenticate(self) -> bool:
        if not self.store_url or not self.access_token:
            return False
        try:
            self._request(self._api("/shop.json"))
            return True
        except RuntimeError:
            return False

    def upload_media(self, file_path: str, alt_text: str) -> str:
        """Upload image as a Shopify theme asset and return CDN URL."""
        return self.upload_media_via_theme_asset(file_path)


def create_adapter() -> ShopifyAdapter:
    """Factory function called by get_adapter()."""
    return ShopifyAdapter()
