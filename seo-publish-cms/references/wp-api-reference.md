# WordPress REST API Quick Reference

## Authentication

### Application Passwords (Recommended)

WordPress 5.6+ supports Application Passwords natively.

**Setup:**
1. Go to WP Admin > Users > Profile
2. Scroll to "Application Passwords"
3. Enter a name (e.g. "SEO Publisher") and click "Add New Application Password"
4. Copy the generated password immediately — it is shown only once

**Token format for WORDPRESS_TOKEN:**
```
username:xxxx xxxx xxxx xxxx xxxx xxxx
```
The spaces in the application password are fine — include them as-is.

**Header format (Basic Auth, base64-encoded):**
```
Authorization: Basic base64("username:app_password")
```

**Example:**
```python
import base64
token = "admin:abcd efgh ijkl mnop qrst uvwx"
encoded = base64.b64encode(token.encode()).decode()
# Authorization: Basic YWRtaW46YWJjZCBlZmdo...
```

---

## POST /wp-json/wp/v2/posts

Create a new post.

**Request body (JSON):**

| Field | Type | Description |
|---|---|---|
| `title` | string | Post title (plain text or rendered object) |
| `content` | string | Post body HTML |
| `slug` | string | URL slug (auto-generated if omitted) |
| `status` | string | `draft`, `publish`, `pending`, `private` |
| `categories` | int[] | Array of category IDs |
| `tags` | int[] | Array of tag IDs |
| `featured_media` | int | Media ID for featured image |
| `meta` | object | Custom meta fields (see SEO section below) |

**SEO meta fields:**

Yoast SEO:
```json
{
  "meta": {
    "_yoast_wpseo_title": "Custom SEO Title",
    "_yoast_wpseo_metadesc": "Custom meta description"
  }
}
```

RankMath SEO:
```json
{
  "meta": {
    "rank_math_title": "Custom SEO Title",
    "rank_math_description": "Custom meta description"
  }
}
```

**Response (201 Created):**
```json
{
  "id": 42,
  "link": "https://example.com/my-post-slug/",
  "status": "draft",
  "slug": "my-post-slug",
  "title": { "rendered": "Post Title" }
}
```

---

## POST /wp-json/wp/v2/media

Upload a file to the media library.

**Request:** `multipart/form-data`

| Field | Type | Description |
|---|---|---|
| `file` | binary | Image file (jpg, png, webp) |
| `alt_text` | string | Alt text for accessibility/SEO |
| `title` | string | (optional) Media title |
| `caption` | string | (optional) Caption text |

**Example curl:**
```bash
curl -X POST \
  -H "Authorization: Basic <token>" \
  -F "file=@/path/to/image.jpg" \
  -F "alt_text=Hero image description" \
  https://example.com/wp-json/wp/v2/media
```

**Response (201 Created):**
```json
{
  "id": 123,
  "source_url": "https://example.com/wp-content/uploads/2024/01/image.jpg",
  "alt_text": "Hero image description",
  "mime_type": "image/jpeg"
}
```

---

## GET /wp-json/wp/v2/categories

List available categories.

**Query params:** `per_page` (default 10, max 100), `search`, `page`

```bash
curl -H "Authorization: Basic <token>" \
  "https://example.com/wp-json/wp/v2/categories?per_page=100"
```

**Response item:**
```json
{ "id": 5, "name": "SEO Tips", "slug": "seo-tips", "count": 12 }
```

---

## GET /wp-json/wp/v2/tags

List available tags.

```bash
curl -H "Authorization: Basic <token>" \
  "https://example.com/wp-json/wp/v2/tags?per_page=100&search=keyword"
```

---

## Common Error Codes

| Code | Meaning | Fix |
|---|---|---|
| 401 | Unauthorized | Check WORDPRESS_TOKEN format: `username:app_password` |
| 403 | Forbidden | User lacks `edit_posts` capability; check role |
| 404 | Not Found | Wrong WORDPRESS_URL or REST API disabled |
| 413 | Payload Too Large | Image too big; resize or increase `upload_max_filesize` in php.ini |
| 422 | Unprocessable Entity | Invalid field value (e.g. bad category ID) |
| 500 | Server Error | Check WP error logs at `wp-content/debug.log` |

---

## Troubleshooting

**REST API returns 404 for all endpoints:**
- Ensure Permalinks are not set to "Plain" (WP Admin > Settings > Permalinks)
- Some security plugins block REST API; whitelist your IP or disable temporarily

**Application Password not working:**
- Confirm the user has the Application Passwords feature enabled (some security plugins disable it)
- Try regenerating the password; spaces in the password are normal

**Meta fields not saving:**
- Yoast/RankMath must be active and the meta key must be registered
- Some fields require the post to be published first; create as draft then update

**Upload fails with 403:**
- Check that `Allow file uploads` is enabled for the user role
- Confirm `upload_max_filesize` and `post_max_size` in php.ini are large enough
