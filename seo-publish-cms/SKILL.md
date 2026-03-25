---
name: seo-publish-cms
description: "Publish SEO article to WordPress, Shopify, or Haravan via REST API with media upload, categories, tags, and featured image when content is ready for CMS"
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

# seo-publish-cms

## Context

You are a CMS publishing specialist. Your job is to take a finalized SEO article file and publish it to WordPress as a draft post, handling image uploads, category/tag assignment, and SEO meta fields. You never publish directly — always create as `draft` so the user can review before going live.

## Input

An article file (typically `article.md`) with YAML frontmatter containing SEO metadata, followed by the article body in Markdown.

**Expected frontmatter fields:**
```yaml
---
title: "Article Title"
slug: "url-slug-here"
meta_title: "SEO Page Title | Brand"
meta_description: "150-160 char meta description"
categories: [5, 12]          # WordPress category IDs
tags: [3, 7, 9]              # WordPress tag IDs
featured_image: "./hero.jpg" # optional, relative path
---
```

## Environment Variables

| Variable | Description |
|---|---|
| `CMS_TARGET` | Target CMS: `wordpress` (default), `shopify`, or `haravan` |
| `WORDPRESS_URL` | Base URL of WordPress site, e.g. `https://example.com` |
| `WORDPRESS_TOKEN` | WordPress credentials as `username:application_password` |
| `SHOPIFY_STORE_URL` | Shopify store URL, e.g. `https://mystore.myshopify.com` |
| `SHOPIFY_ACCESS_TOKEN` | Shopify Admin API access token |
| `SHOPIFY_BLOG_ID` | Numeric Shopify blog ID for article creation |
| `HARAVAN_STORE_URL` | Haravan store URL, e.g. `https://mystore.haravan.com` |
| `HARAVAN_ACCESS_TOKEN` | Haravan Admin API access token |
| `HARAVAN_BLOG_ID` | Numeric Haravan blog ID for article creation |

**Backward compatibility:** If `CMS_TARGET` is not set, defaults to `wordpress`. Existing `WORDPRESS_URL` / `WORDPRESS_TOKEN` setups continue to work unchanged.

**WordPress setup:** Generate an Application Password in WP Admin > Users > Profile > Application Passwords.

## Steps

1. **Read article file**
   - Read `article.md` (or the file specified by the user)
   - Parse YAML frontmatter block (between `---` delimiters) for: `title`, `slug`, `meta_title`, `meta_description`, `categories`, `tags`, `featured_image`
   - Separate the frontmatter from the Markdown body

2. **Convert Markdown body to HTML**
   - Apply basic Markdown-to-HTML conversion for the article body:
     - `# Heading` → `<h1>`, `## Heading` → `<h2>`, etc.
     - `**bold**` → `<strong>`, `*italic*` → `<em>`
     - `` `code` `` → `<code>`, fenced code blocks → `<pre><code>`
     - `[text](url)` → `<a href="url">text</a>`
     - `![alt](path)` → `<img src="path" alt="alt">` (paths will be replaced in step 5)
     - Blank-line-separated paragraphs → `<p>` tags
     - `- item` / `* item` → `<ul><li>` lists
     - `1. item` → `<ol><li>` lists

3. **Extract image paths**
   - Find all image references in the article: frontmatter `featured_image` + all `![alt](path)` in body
   - Collect unique local paths (skip URLs that start with `http://` or `https://`)
   - Note the alt text associated with each image path

4. **Upload images to WordPress**
   - For each local image path, run:
     ```bash
     python3 scripts/media-uploader.py "<image_path>" "<alt_text>"
     ```
   - Collect the returned `{"media_id": int, "url": str}` for each image
   - If an image upload fails: log a warning, continue publishing without that image, do NOT abort

5. **Replace local image paths with WordPress URLs**
   - In the converted HTML content, replace each `src="<local_path>"` with the corresponding `src="<wp_media_url>"` from step 4
   - Images that failed to upload remain as their original local path with a warning comment

6. **Set featured image**
   - If `featured_image` is specified in frontmatter and was successfully uploaded, use its `media_id` as `featured_media`
   - If no `featured_image` is specified but images were uploaded, use the first uploaded image's `media_id`
   - If no images were uploaded, omit `featured_media`

7. **Create CMS draft post via adapter**
   - Build the JSON payload and pipe to `wp-publisher.py`:
     ```bash
     echo '<json_payload>' | python3 scripts/wp-publisher.py
     ```
   - The script loads `seo-cms-adapter` and routes to the correct platform via `CMS_TARGET`
   - JSON payload structure:
     ```json
     {
       "title": "<from frontmatter>",
       "content": "<converted HTML>",
       "slug": "<from frontmatter>",
       "meta_title": "<from frontmatter>",
       "meta_description": "<from frontmatter>",
       "categories": [<ids>],
       "tags": [<ids>],
       "featured_media": <media_id or omit>
     }
     ```
   - **WordPress:** categories/tags are integer IDs; featured_media is WP media ID
   - **Shopify/Haravan:** categories are ignored; tags are joined as comma-separated strings

8. **Return result to user**
   - Report the outcome clearly:
     ```
     Draft created successfully.
     Post ID: 42
     Preview URL: https://example.com/?p=42
     Status: draft (not yet published)

     Images uploaded: 3/3
     Featured image: set (media ID 123)

     Next step: Review the draft at the URL above, then publish when ready.
     ```

## Error Handling

| Error | Response |
|---|---|
| Auth failure (401) | Stop immediately. Print: "Authentication failed. Check WORDPRESS_TOKEN — format must be 'username:application_password'. Generate one at WP Admin > Users > Profile > Application Passwords." |
| Permission denied (403) | Stop. Print: "WordPress user lacks permission to create posts. Ensure the user role has 'edit_posts' capability." |
| Image upload failure | Warn user, continue publishing without that image. List failed images at end. |
| API timeout | Retry the failed request once after 5 seconds. If retry fails, report the error with full details. |
| Invalid JSON from scripts | Print the raw output and exit with a clear message about what went wrong. |

## Notes

- Always publish as `draft` — never use `status: publish` directly
- Category and tag values in frontmatter must be **integer IDs**, not names. To find IDs, check `GET /wp-json/wp/v2/categories` (see `references/wp-api-reference.md`)
- Yoast SEO and RankMath meta fields are both set simultaneously — whichever plugin is active will use its fields
- The `WORDPRESS_TOKEN` should never be logged or printed in output
