---
name: seo-image-generate
description: "Generate SEO-optimized thumbnail and section images with alt text for articles using AI image generation when preparing content for publishing"
metadata:
  openclaw:
    type: skill
    requires:
      anyBins:
        - python3
        - python
      env:
        - IMAGE_GEN_API_KEY
    primaryEnv: IMAGE_GEN_API_KEY
---

# seo-image-generate

## Overview

Generates a featured (OG) image and one section image per H2 heading in an article. Produces SEO-friendly alt text for each image and saves an `image_map.json` for consumption by `seo-publish-cms`.

**Outputs per article:**
- `images/featured-{slug}.webp` — 1200×630 px hero/OG image
- `images/{section-heading}.webp` — 800×450 px per H2 section
- `image_map.json` — structured map of all images with paths and alt text

---

## Requirements

- `IMAGE_GEN_API_KEY` — API key for the image generation service (required)
- Article must be a markdown file with YAML frontmatter containing `primary_keyword`
- `images/` output directory will be created if it does not exist

---

## Steps

### Step 1 — Read article.md

Read the target article markdown file. Confirm it has:
- YAML frontmatter with `primary_keyword` and `meta_title`
- At least one `## H2` heading (for section images)

If frontmatter is missing, warn the user — the featured image prompt will fall back to the H1 title.

### Step 2 — Run image-prompt-builder.py

Generate image prompts for the featured image and all H2 sections:

```bash
python3 seo-image-generate/scripts/image-prompt-builder.py <article.md>
```

Or from stdin:

```bash
cat article.md | python3 seo-image-generate/scripts/image-prompt-builder.py
```

Output is a JSON array:

```json
[
  {
    "type": "featured",
    "heading": "Best Running Shoes for Beginners",
    "prompt": "running shoes for beginners, hero banner...",
    "filename": "featured-best-running-shoes-for-beginners.webp"
  },
  {
    "type": "section",
    "heading": "How to Choose Running Shoes",
    "prompt": "Visual illustration of 'How to Choose Running Shoes'...",
    "filename": "how-to-choose-running-shoes.webp"
  }
]
```

### Step 3 — Call image generation API for each prompt

For each item in the prompts array, call the image generation API using `IMAGE_GEN_API_KEY`.

Use these dimensions per image type:

| Type | Width | Height |
|---|---|---|
| `featured` | 1200 | 630 |
| `section` | 800 | 450 |

**Example API call pattern (adapt to your provider):**

```bash
curl -X POST "https://api.imagegen.example.com/v1/generate" \
  -H "Authorization: Bearer ${IMAGE_GEN_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "<prompt from step 2>",
    "width": 1200,
    "height": 630,
    "format": "webp"
  }' \
  --output "images/featured-article-slug.webp"
```

Request WebP format where supported. If the API returns PNG or JPEG, save as-is and note the actual format in `image_map.json`.

### Step 4 — Save images

Create the `images/` directory relative to the article location if it does not exist.

Save each generated image to `images/{filename}` using the filename from the prompts array.

### Step 5 — Generate alt text for each image

For each saved image, generate SEO-friendly alt text using `alt-text-generator.py`:

```bash
echo '{
  "heading": "How to Choose Running Shoes",
  "keywords": ["running shoes for beginners", "beginner running gear"],
  "context": "First sentence or excerpt from this section"
}' | python3 seo-image-generate/scripts/alt-text-generator.py
```

Output:
```json
{"alt_text": "How to choose running shoes — person comparing pairs in a sports store for running shoes for beginners"}
```

Provide context from the first sentence of the corresponding section body for richer alt text.

### Step 6 — Save image_map.json

Compile all image metadata into `image_map.json` following the schema in `references/image-map-schema.json`:

```json
{
  "featured_image": {
    "path": "images/featured-best-running-shoes-for-beginners.webp",
    "alt": "Best running shoes for beginners displayed on a wooden surface",
    "width": 1200,
    "height": 630,
    "format": "webp",
    "prompt": "running shoes for beginners, hero banner..."
  },
  "section_images": [
    {
      "section_heading": "How to Choose Running Shoes",
      "path": "images/how-to-choose-running-shoes.webp",
      "alt": "How to choose running shoes for beginners — comparing pairs in store",
      "width": 800,
      "height": 450,
      "format": "webp",
      "prompt": "Visual illustration of 'How to Choose Running Shoes'..."
    }
  ]
}
```

Save `image_map.json` in the same directory as the article.

---

## Image Specifications

See `references/image-specs.md` for:
- Full dimension and format requirements
- Alt text rules and examples
- File naming conventions
- WebP conversion notes

---

## Output Schema

See `references/image-map-schema.json` for the full JSON Schema definition of `image_map.json`.

---

## Integration with seo-content-flow

In the `seo-content-flow` pipeline, this skill runs after `seo-content-write` and its `image_map.json` output is passed to `seo-optimize-score` via the `IMAGES` env var. The `seo-publish-cms` skill reads `image_map.json` to attach the featured image and inline section images during WordPress publishing.

---

## Troubleshooting

**image-prompt-builder.py produces no section images:**
- Confirm the article has `## H2` headings (not just H3 or H1)
- H2 headings must start at column 0 with exactly `## `

**API call fails with 401:**
- Verify `IMAGE_GEN_API_KEY` is exported in the shell environment
- Check the API key has not expired or exceeded its quota

**Generated images are wrong dimensions:**
- Some APIs require separate width/height params; others use aspect ratio codes
- Check your provider's API docs and adjust the curl command accordingly

**Alt text exceeds 125 characters:**
- Shorten the `context` input passed to `alt-text-generator.py`
- Or pass a shorter heading with less detail

**image_map.json not found by seo-publish-cms:**
- Ensure `image_map.json` is saved in the same directory as `article.md`
- Pass the image map path explicitly if your CMS skill supports it
