#!/usr/bin/env python3
"""adapter-interface.py — Abstract base class for CMS adapters.

Defines the CMSAdapter interface and a factory function to instantiate
the correct adapter based on the CMS_TARGET environment variable or
the cms_target parameter.

Factory usage:
    adapter = get_adapter("wordpress")
    adapter = get_adapter("shopify")
    adapter = get_adapter("haravan")
"""

import os
import importlib.util
from abc import ABC, abstractmethod


class CMSAdapter(ABC):
    """Abstract base class defining the unified CMS publishing interface."""

    @abstractmethod
    def authenticate(self) -> bool:
        """Verify credentials and connectivity to the CMS.

        Returns:
            True if authentication succeeded, False otherwise.
        """
        ...

    @abstractmethod
    def create_post(
        self,
        title: str,
        content: str,
        slug: str,
        meta: dict,
        status: str = "draft",
    ) -> dict:
        """Create a new post/article in the CMS.

        Args:
            title:   Post title (plain text).
            content: Post body (HTML).
            slug:    URL-friendly identifier.
            meta:    Dict with keys: meta_title, meta_description,
                     categories (list[int]), tags (list[int]),
                     featured_media (int, optional).
            status:  Publication status — default "draft".

        Returns:
            {"post_id": int, "url": str, "status": str}
        """
        ...

    @abstractmethod
    def upload_media(self, file_path: str, alt_text: str) -> str:
        """Upload a media file to the CMS media library.

        Args:
            file_path: Absolute or relative path to the local file.
            alt_text:  Accessibility alt text for the image.

        Returns:
            Public URL of the uploaded media, or empty string on failure.
        """
        ...

    @abstractmethod
    def set_categories(self, post_id: int, categories: list) -> bool:
        """Assign categories to an existing post.

        Args:
            post_id:    CMS post identifier.
            categories: List of category IDs (int).

        Returns:
            True on success.
        """
        ...

    @abstractmethod
    def set_tags(self, post_id: int, tags: list) -> bool:
        """Assign tags to an existing post.

        Args:
            post_id: CMS post identifier.
            tags:    List of tag IDs (int).

        Returns:
            True on success.
        """
        ...

    @abstractmethod
    def get_sitemap(self) -> list:
        """Retrieve all URLs from the CMS sitemap.

        Returns:
            List of URL strings found in sitemap.xml.
        """
        ...

    @abstractmethod
    def get_post_url(self, post_id: int) -> str:
        """Get the public URL for a post by its ID.

        Args:
            post_id: CMS post identifier.

        Returns:
            Full public URL string.
        """
        ...


def _load_adapter_module(adapter_name: str):
    """Load a sibling adapter script by name using importlib."""
    scripts_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(scripts_dir, f"{adapter_name}.py")

    if not os.path.isfile(file_path):
        raise FileNotFoundError(
            f"Adapter script not found: {file_path}"
        )

    module_name = adapter_name.replace("-", "_")
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def get_adapter(cms_target: str) -> CMSAdapter:
    """Return the correct CMSAdapter instance for the given CMS target.

    Args:
        cms_target: One of "wordpress", "shopify", or "haravan".
                    Falls back to CMS_TARGET env var if empty.

    Returns:
        An instantiated CMSAdapter subclass.

    Raises:
        ValueError: If cms_target is not supported.
        FileNotFoundError: If adapter script is missing.
    """
    if not cms_target:
        cms_target = os.environ.get("CMS_TARGET", "wordpress")

    cms_target = cms_target.strip().lower()

    _SUPPORTED = {
        "wordpress": "wp-adapter",
        "shopify":   "shopify-adapter",
        "haravan":   "haravan-adapter",
    }

    if cms_target not in _SUPPORTED:
        raise ValueError(
            f"Unsupported CMS target: '{cms_target}'. "
            f"Choose from: {', '.join(_SUPPORTED.keys())}"
        )

    mod = _load_adapter_module(_SUPPORTED[cms_target])
    return mod.create_adapter()
