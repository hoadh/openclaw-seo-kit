#!/usr/bin/env python3
"""
wp-publisher.py — Publish article to CMS as draft via seo-cms-adapter.

Reads JSON from stdin, creates a draft post using the unified CMSAdapter
interface. Supports WordPress (default), Shopify, and Haravan via CMS_TARGET.

Required env vars:
  CMS_TARGET      — "wordpress" | "shopify" | "haravan" (default: wordpress)
  WORDPRESS_URL   — Base URL (if CMS_TARGET=wordpress)
  WORDPRESS_TOKEN — "username:application_password" (if CMS_TARGET=wordpress)
  SHOPIFY_STORE_URL / SHOPIFY_ACCESS_TOKEN / SHOPIFY_BLOG_ID (if shopify)
  HARAVAN_STORE_URL / HARAVAN_ACCESS_TOKEN / HARAVAN_BLOG_ID (if haravan)

Input JSON fields:
  title, content (HTML), slug, meta_title, meta_description,
  categories (list[int]), tags (list[int]), featured_media (optional int)

Output JSON:
  {"post_id": int, "url": str, "status": "draft"}
"""

import importlib.util
import json
import os
import sys


def _load_adapter_interface():
    """Load get_adapter() from seo-cms-adapter skill via importlib."""
    # Resolve path relative to this script: ../../seo-cms-adapter/scripts/
    this_dir = os.path.dirname(os.path.abspath(__file__))
    adapter_path = os.path.join(
        this_dir, "..", "..", "seo-cms-adapter", "scripts", "adapter-interface.py"
    )
    adapter_path = os.path.normpath(adapter_path)

    if not os.path.isfile(adapter_path):
        sys.exit(
            f"Error: seo-cms-adapter not found at {adapter_path}. "
            "Ensure seo-cms-adapter skill is installed alongside seo-publish-cms."
        )

    spec = importlib.util.spec_from_file_location("adapter_interface", adapter_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main():
    try:
        raw = sys.stdin.read()
        article = json.loads(raw)
    except json.JSONDecodeError as exc:
        sys.exit(f"Error: Invalid JSON input — {exc}")

    cms_target = os.environ.get("CMS_TARGET", "wordpress").strip().lower()

    # Load adapter
    ai_mod = _load_adapter_interface()
    try:
        adapter = ai_mod.get_adapter(cms_target)
    except (ValueError, FileNotFoundError) as exc:
        sys.exit(f"Error loading CMS adapter: {exc}")

    # Authenticate
    if not adapter.authenticate():
        _print_auth_error(cms_target)
        sys.exit(1)

    # Build meta dict from input
    meta = {
        "meta_title":       article.get("meta_title", ""),
        "meta_description": article.get("meta_description", ""),
        "categories":       article.get("categories", []),
        "tags":             article.get("tags", []),
    }
    if article.get("featured_media"):
        meta["featured_media"] = article["featured_media"]

    # Create post as draft
    try:
        result = adapter.create_post(
            title=article.get("title", ""),
            content=article.get("content", ""),
            slug=article.get("slug", ""),
            meta=meta,
            status="draft",
        )
    except RuntimeError as exc:
        _handle_api_error(str(exc), cms_target)
        sys.exit(1)

    print(json.dumps(result, ensure_ascii=False, indent=2))


def _print_auth_error(cms_target: str) -> None:
    messages = {
        "wordpress": (
            "Auth failure: Check WORDPRESS_TOKEN format — must be "
            "'username:application_password'. Generate one at "
            "WP Admin > Users > Profile > Application Passwords."
        ),
        "shopify": (
            "Auth failure: Check SHOPIFY_ACCESS_TOKEN. Generate a Custom App "
            "token at Shopify Admin > Settings > Apps and sales channels > Develop apps."
        ),
        "haravan": (
            "Auth failure: Check HARAVAN_ACCESS_TOKEN. Generate a token from "
            "your Haravan Partner app credentials."
        ),
    }
    print(messages.get(cms_target, f"Auth failure for CMS target: {cms_target}"),
          file=sys.stderr)


def _handle_api_error(error_msg: str, cms_target: str) -> None:
    if "401" in error_msg:
        _print_auth_error(cms_target)
    elif "403" in error_msg:
        print(
            f"Permission denied (403): The {cms_target} app/user lacks create permissions. "
            "Check API scopes.",
            file=sys.stderr,
        )
    else:
        print(f"API error ({cms_target}): {error_msg}", file=sys.stderr)


if __name__ == "__main__":
    main()
