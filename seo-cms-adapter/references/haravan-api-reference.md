# Haravan Admin REST API Reference

Haravan is a Vietnamese e-commerce platform with a Shopify-compatible REST API.
The adapter targets the blog/article publishing subset of the API.

---

## Authentication

### Access Token Setup
1. Log in to Haravan Partner dashboard at https://partners.haravan.com
2. Create a new app or use an existing private app
3. Configure scopes: `write_content`, `read_content`
4. Install the app on the target store
5. Copy the **access token** from the app credentials page

```
X-Haravan-Access-Token: {access_token}
```

### Key Difference from Shopify
- Header name: `X-Haravan-Access-Token` (not `X-Shopify-Access-Token`)
- No API version segment in URL path (Haravan uses `/admin/` directly)
- Base URL pattern: `https://{store}.haravan.com/admin/`

---

## API URL Structure

| Platform | Pattern |
|----------|---------|
| Shopify  | `https://{store}.myshopify.com/admin/api/2024-01/{resource}.json` |
| Haravan  | `https://{store}.haravan.com/admin/{resource}.json` |

---

## Blog Article Endpoints

Base URL: `https://{store}.haravan.com/admin`

### List Blogs
```
GET /blogs.json
X-Haravan-Access-Token: {token}
```
Response: `{"blogs": [{"id": 123, "title": "Tin tức", "handle": "tin-tuc"}, ...]}`

### Create Article (Draft)
```
POST /blogs/{blog_id}/articles.json
Content-Type: application/json
X-Haravan-Access-Token: {token}

{
  "article": {
    "title":       "Tiêu đề bài viết",
    "body_html":   "<p>Nội dung HTML</p>",
    "handle":      "tieu-de-bai-viet",
    "published":   false,
    "tags":        "seo, marketing",
    "title_tag":   "SEO Tiêu đề trang | Thương hiệu",
    "metafields_global_description_tag": "Mô tả meta 150-160 ký tự"
  }
}
```

Response: `{"article": {"id": 456, "handle": "tieu-de-bai-viet", ...}}`

### Update Article
```
PUT /blogs/{blog_id}/articles/{article_id}.json
Content-Type: application/json
X-Haravan-Access-Token: {token}

{"article": {"published": true}}
```

---

## SEO Metadata Fields

| Field | Description | Notes |
|-------|-------------|-------|
| `title_tag` | HTML `<title>` | 50-70 chars recommended |
| `metafields_global_description_tag` | Meta description | 120-160 chars recommended |
| `handle` | URL slug | Auto-lowercased, hyphens only |
| `body_html` | Article content (HTML) | Supports full HTML |
| `tags` | Comma-separated tag string | Not integer IDs like WordPress |

---

## Differences from Shopify API

| Feature | Shopify | Haravan |
|---------|---------|---------|
| Auth header | `X-Shopify-Access-Token` | `X-Haravan-Access-Token` |
| API versioning | `/admin/api/2024-01/` | `/admin/` (no version) |
| Theme asset upload | Supported via `/themes/{id}/assets.json` | Supported (same pattern) |
| GraphQL | Available | Not available |
| Webhooks | Full support | Partial support |
| Multi-location inventory | Yes | No |
| Blog categories | No (tags only) | No (tags only) |

---

## Asset Upload (Images)

Same pattern as Shopify — requires fetching the main theme ID first.

### Get Main Theme ID
```
GET /themes.json
X-Haravan-Access-Token: {token}
```
Find the theme where `"role": "main"`.

### Upload Image Asset
```
PUT /themes/{theme_id}/assets.json
Content-Type: application/json
X-Haravan-Access-Token: {token}

{
  "asset": {
    "key":          "assets/image.jpg",
    "attachment":   "<base64-encoded bytes>",
    "content_type": "image/jpeg"
  }
}
```

Response: `{"asset": {"public_url": "https://cdn.haravan.com/...", "key": "assets/image.jpg"}}`

---

## Sitemap

```
GET https://{store}.haravan.com/sitemap.xml
```

Parse `<loc>` elements. Blog article URLs: `/blogs/{blog-handle}/{article-handle}`

---

## Rate Limits

Haravan enforces rate limits similar to Shopify:
- Default: 2 requests/second
- On 429: wait 1-2 seconds and retry once

---

## Common Error Codes

| Code | Meaning |
|------|---------|
| 401 | Missing or invalid `X-Haravan-Access-Token` |
| 403 | Insufficient app permissions |
| 404 | Blog or article not found — verify `HARAVAN_BLOG_ID` |
| 422 | Validation error — check `body_html` and `title` are present |
| 429 | Rate limited — back off and retry |

---

## Vietnamese Content Notes

- `handle` field: Haravan auto-converts Vietnamese diacritics to ASCII slugs
  - "Tối ưu SEO" → `toi-uu-seo`
  - Pre-convert with a slug utility if you need exact control
- Tags support UTF-8 including Vietnamese characters
- `title_tag` and `metafields_global_description_tag` support full UTF-8
