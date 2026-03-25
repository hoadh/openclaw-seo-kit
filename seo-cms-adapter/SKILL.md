---
name: seo-cms-adapter
description: "Abstract CMS adapter providing unified API for publishing to WordPress, Shopify, and Haravan when any SEO skill needs CMS interaction"
metadata:
  openclaw:
    requires:
      env:
        - CMS_TARGET
      primaryEnv: CMS_TARGET
      anyBins:
        - python3
        - python
---

# seo-cms-adapter

## Context

You are a CMS integration specialist. Your job is to provide a unified publishing interface across WordPress, Shopify, and Haravan so that any SEO skill can publish content without knowing platform-specific API details. You act as the translation layer — callers use the same interface regardless of which CMS is configured.

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `CMS_TARGET` | Yes | Target CMS: `wordpress`, `shopify`, or `haravan` |
| `WORDPRESS_URL` | If wordpress | Base URL, e.g. `https://example.com` |
| `WORDPRESS_TOKEN` | If wordpress | `username:application_password` |
| `SHOPIFY_STORE_URL` | If shopify | Store URL, e.g. `https://mystore.myshopify.com` |
| `SHOPIFY_ACCESS_TOKEN` | If shopify | Admin API access token |
| `SHOPIFY_BLOG_ID` | If shopify | Numeric blog ID for article creation |
| `HARAVAN_STORE_URL` | If haravan | Store URL, e.g. `https://mystore.haravan.com` |
| `HARAVAN_ACCESS_TOKEN` | If haravan | Admin API access token |
| `HARAVAN_BLOG_ID` | If haravan | Numeric blog ID for article creation |

## Steps

1. **Read CMS_TARGET**
   - Read `CMS_TARGET` environment variable
   - Accepted values: `wordpress`, `shopify`, `haravan`
   - If unset or empty, default to `wordpress`
   - If unsupported value: exit with clear error listing valid options

2. **Load adapter**
   - Call the factory: `get_adapter(cms_target)` from `scripts/adapter-interface.py`
   - The factory loads the correct adapter script via importlib:
     - `wordpress` → `scripts/wp-adapter.py` → `WordPressAdapter`
     - `shopify`   → `scripts/shopify-adapter.py` → `ShopifyAdapter`
     - `haravan`   → `scripts/haravan-adapter.py` → `HaravanAdapter`

3. **Authenticate**
   - Call `adapter.authenticate()` — returns `True`/`False`
   - On failure: print platform-specific auth error and exit
   - Never log the token/password value itself

4. **Expose unified methods**
   The adapter provides these methods for callers:

   | Method | Signature | Returns |
   |--------|-----------|---------|
   | `create_post` | `(title, content, slug, meta, status="draft")` | `{"post_id", "url", "status"}` |
   | `upload_media` | `(file_path, alt_text)` | `str` URL or `""` on failure |
   | `set_categories` | `(post_id, categories)` | `bool` |
   | `set_tags` | `(post_id, tags)` | `bool` |
   | `get_sitemap` | `()` | `list[str]` of URLs |
   | `get_post_url` | `(post_id)` | `str` URL |

   - `create_post` always creates as `draft` unless `status` is explicitly overridden
   - `upload_media` failure is non-fatal — callers should log a warning and continue
   - `set_categories` is a no-op on Shopify/Haravan (they use tags only) — returns `True`

## Adapter Usage Pattern

```python
import os, sys, importlib.util

def load_adapter_interface():
    skill_dir = "/path/to/seo-cms-adapter/scripts"
    spec = importlib.util.spec_from_file_location(
        "adapter_interface",
        os.path.join(skill_dir, "adapter-interface.py")
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

ai = load_adapter_interface()
adapter = ai.get_adapter(os.environ.get("CMS_TARGET", "wordpress"))

if not adapter.authenticate():
    sys.exit("CMS authentication failed")

result = adapter.create_post(
    title="Article Title",
    content="<p>HTML content</p>",
    slug="article-slug",
    meta={
        "meta_title":       "SEO Title | Brand",
        "meta_description": "150-160 char description",
        "categories":       [5, 12],   # WordPress IDs; ignored on Shopify/Haravan
        "tags":             [3, 7],    # WordPress IDs; converted to strings on others
        "featured_media":   123,       # WordPress media ID; ignored on others
    },
    status="draft",
)
print(result)  # {"post_id": 42, "url": "https://...", "status": "draft"}
```

## Platform Differences Summary

| Feature | WordPress | Shopify | Haravan |
|---------|-----------|---------|---------|
| Auth | Basic (base64 token) | `X-Shopify-Access-Token` | `X-Haravan-Access-Token` |
| API version in URL | `/wp-json/wp/v2/` | `/admin/api/2024-01/` | `/admin/` |
| Categories | Integer IDs | Not supported | Not supported |
| Tags | Integer IDs | Comma-separated strings | Comma-separated strings |
| Draft status | `"status": "draft"` | `"published": false` | `"published": false` |
| SEO fields | Yoast + RankMath meta | `title_tag` + `metafields_global_description_tag` | Same as Shopify |
| Media upload | `/wp-json/wp/v2/media` (multipart) | Theme assets (base64) | Theme assets (base64) |

## Error Handling

| Error | Response |
|---|---|
| `CMS_TARGET` unsupported | Exit with list of valid values |
| Auth failure | Exit with platform-specific setup instructions |
| `create_post` HTTP error | Raise `RuntimeError` with HTTP status and body |
| `upload_media` failure | Return `""` — callers should warn and continue |
| Missing `BLOG_ID` (Shopify/Haravan) | Raise `RuntimeError` before API call |

## References

- `references/shopify-api-reference.md` — Shopify Admin REST API details
- `references/haravan-api-reference.md` — Haravan API differences and notes
- WordPress: see `seo-publish-cms/references/wp-api-reference.md`
