# Shopify Admin REST API Reference

## Authentication

### Private App (deprecated, still functional)
Generate credentials in Shopify Admin > Apps > Develop apps > Create an app.
Use the Admin API access token directly as `X-Shopify-Access-Token` header.

### Custom App (recommended)
1. Go to Shopify Admin > Settings > Apps and sales channels > Develop apps
2. Create app, configure Admin API scopes: `write_content`, `read_content`, `write_themes`, `read_themes`
3. Install the app and copy the **Admin API access token** (shown once)

```
X-Shopify-Access-Token: shpat_xxxxxxxxxxxxxxxxxxxx
```

### Required Scopes
| Scope | Purpose |
|-------|---------|
| `write_content` | Create/update blog articles |
| `read_content`  | Read blogs and articles |
| `write_themes`  | Upload assets (images) to theme |
| `read_themes`   | List themes to find main theme ID |

---

## Blog Article Endpoints

Base URL: `https://{store}.myshopify.com/admin/api/2024-01`

### List Blogs
```
GET /blogs.json
```
Response: `{"blogs": [{"id": 123, "title": "News", "handle": "news"}, ...]}`

### List Articles in Blog
```
GET /blogs/{blog_id}/articles.json
```

### Create Article (Draft)
```
POST /blogs/{blog_id}/articles.json
Content-Type: application/json
X-Shopify-Access-Token: {token}

{
  "article": {
    "title":       "Article Title",
    "body_html":   "<p>Content HTML</p>",
    "handle":      "url-slug",
    "published":   false,
    "tags":        "seo, marketing",
    "title_tag":   "SEO Page Title | Brand",
    "metafields_global_description_tag": "150-160 char meta description"
  }
}
```

Response: `{"article": {"id": 456, "handle": "url-slug", "title": "...", ...}}`

### Update Article
```
PUT /blogs/{blog_id}/articles/{article_id}.json
Content-Type: application/json

{"article": {"tags": "new, tags"}}
```

### Delete Article
```
DELETE /blogs/{blog_id}/articles/{article_id}.json
```

---

## SEO Metadata Fields

| Field | Description | Max Length |
|-------|-------------|-----------|
| `title_tag` | HTML `<title>` for the article page | 70 chars |
| `metafields_global_description_tag` | Meta description | 320 chars |
| `handle` | URL slug — auto-generated from title if omitted | — |
| `body_html` | Article content (HTML) | unlimited |

**Note:** Shopify does not support custom meta robots or canonical URL overrides via API — these require theme-level customization.

---

## Asset Upload Endpoints

Used to host images in the Shopify CDN via theme assets.

### List Themes (to find main theme ID)
```
GET /themes.json
```
Response: `{"themes": [{"id": 789, "name": "Dawn", "role": "main"}, ...]}`
Use the theme where `"role": "main"`.

### Upload Asset
```
PUT /themes/{theme_id}/assets.json
Content-Type: application/json

{
  "asset": {
    "key":          "assets/my-image.jpg",
    "attachment":   "<base64-encoded file content>",
    "content_type": "image/jpeg"
  }
}
```

Response: `{"asset": {"key": "assets/my-image.jpg", "public_url": "https://cdn.shopify.com/..."}}`

### Supported Image Formats
`image/jpeg`, `image/png`, `image/gif`, `image/webp`, `image/svg+xml`

---

## Sitemap

```
GET https://{store}.myshopify.com/sitemap.xml
```

Returns XML with `<loc>` tags for all public URLs. Parse with regex:
```python
re.findall(r"<loc>\s*(https?://[^\s<]+)\s*</loc>", xml)
```

Blog article URLs follow pattern: `/blogs/{blog-handle}/{article-handle}`

---

## Rate Limits

- REST API: 2 requests/second (leaky bucket: 40 burst capacity)
- Response header `X-Shopify-Shop-Api-Call-Limit: 5/40` shows current usage
- On 429: wait 1 second and retry

---

## Common Error Codes

| Code | Meaning |
|------|---------|
| 401 | Invalid or missing access token |
| 403 | Insufficient scope — check app permissions |
| 404 | Resource not found (wrong blog_id or article_id) |
| 422 | Validation error — check required fields |
| 429 | Rate limit exceeded — back off and retry |
