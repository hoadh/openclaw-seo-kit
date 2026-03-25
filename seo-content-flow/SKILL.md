---
name: seo-content-flow
description: "Full-auto SEO content pipeline from keyword research through WordPress publishing - orchestrates keyword research, outline generation, content writing, image generation, score optimization, and CMS publishing"
metadata:
  openclaw:
    type: clawflow
    requires:
      env:
        - WORDPRESS_URL
        - WORDPRESS_TOKEN
        - GOOGLE_API_KEY
      optionalEnv:
        - SEMRUSH_API_KEY
        - CONTENT_LANG
        - CMS_TARGET
---

# seo-content-flow

## Overview

This is a ClawFlow orchestration skill. It chains six specialized SEO skills into a single end-to-end pipeline: keyword research → outline generation → article writing → image generation → score optimization → CMS publishing.

Each step receives the previous step's output as its input. The `images` and `optimize` steps run with a dependency relationship (optimize depends on both `write` and `images`). The publish step requires explicit user approval before executing.

**Quality gate:** If the `optimize` step produces a score below 70, the pipeline halts and notifies the user. Do not proceed to `publish` until the score reaches 70 or above.

Estimated total execution time: ~25 minutes end-to-end.

---

## ClawFlow Definition

```yaml
name: seo-content-flow
description: Full-auto SEO content from keyword to WordPress publish (6-step pipeline)
steps:
  - name: research
    skill: seo-keyword-research
    input: "${INPUT}"
    description: "Research keywords, discover LSI terms, analyze search intent"

  - name: outline
    skill: seo-outline-generate
    dependsOn: research
    input: "${research.output}"
    description: "Generate article outline with heading structure and meta tags"

  - name: write
    skill: seo-content-write
    dependsOn: outline
    input: "${outline.output}"
    env:
      CONTENT_LANG: "${CONTENT_LANG:-en}"
    description: "Write full SEO article from outline"

  - name: images
    skill: seo-image-generate
    dependsOn: write
    input: "${write.output}"
    description: "Generate featured and section images with alt text"

  - name: optimize
    skill: seo-optimize-score
    dependsOn:
      - write
      - images
    input: "${write.output}"
    env:
      IMAGES: "${images.output}"
    description: "Score and optimize article SEO quality; halt if score < 70"

  - name: publish
    skill: seo-publish-cms
    dependsOn: optimize
    approval: true
    input: "${optimize.output}"
    env:
      CMS_TARGET: "${CMS_TARGET:-wordpress}"
    description: "Publish optimized article to CMS as draft (requires approval)"
```

### Parallel Execution Note

The `images` step and the initial scoring phase of `optimize` can be run in parallel once `write` completes, since `seo-image-generate` only reads the article and `seo-optimize-score` begins with a read-only scoring pass. However, `optimize` must wait for `images` output before injecting image references. The `dependsOn: [write, images]` declaration in the flow definition enforces this — runners that support parallel execution will start `images` immediately after `write` while `optimize` waits for both.

### Quality Gate

After the `optimize` step completes, check the `overall_score` in the score report:

```
if optimize.score < 70:
  HALT pipeline
  notify user: "SEO score is {score}/100 — below the 70-point threshold.
                Review suggestions in score_report.json and re-run from the optimize step."
  exit (do not proceed to publish)
```

The pipeline only advances to `publish` when `overall_score >= 70`.

---

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `WORDPRESS_URL` | Yes | Base URL of WordPress site, e.g. `https://example.com` |
| `WORDPRESS_TOKEN` | Yes | WordPress credentials: `username:application_password` |
| `GOOGLE_API_KEY` | Yes | API key for AI image generation service (used by `seo-image-generate`) |
| `SEMRUSH_API_KEY` | No | SEMrush API key for keyword research data (used by `seo-keyword-research`) |
| `CONTENT_LANG` | No | Content language code — `en` (default) or `vi` |
| `CMS_TARGET` | No | CMS platform — `wordpress` (default) |

---

## How to Run

### Full pipeline from a keyword

```bash
# Set required env vars
export WORDPRESS_URL="https://your-site.com"
export WORDPRESS_TOKEN="username:your-app-password"
export GOOGLE_API_KEY="your-image-gen-api-key"

# Optional
export SEMRUSH_API_KEY="your-semrush-key"
export CONTENT_LANG="en"

# Run the flow with a seed keyword or topic
openclaw run seo-content-flow "best running shoes for beginners"
```

### Resume from a specific step

If an earlier step already produced output, you can start mid-flow:

```bash
# Start from outline step using existing research output
openclaw run seo-content-flow --from outline --input research-output.json

# Start from optimize step (skip image generation if images already exist)
openclaw run seo-content-flow --from optimize --input article.md

# Re-run just the publish step after manual score fixes
openclaw run seo-content-flow --from publish --input optimized_article.md
```

### Run with Vietnamese content

```bash
CONTENT_LANG=vi openclaw run seo-content-flow "giày chạy bộ tốt nhất cho người mới"
```

### Skip image generation (text-only publish)

If image generation is not needed, resume from optimize after write completes:

```bash
openclaw run seo-content-flow --from optimize --input article.md
# Note: image_map.json will be absent; seo-publish-cms will skip featured image attachment
```

---

## Step-by-Step Input/Output Contract

### Step 1: research (seo-keyword-research)

- **Input:** Seed keyword or topic string from user
- **Output:** JSON with primary keyword, LSI keywords, search volume estimates, search intent classification (informational/commercial/transactional), and competitor URLs
- **Key output fields:** `primary_keyword`, `lsi_keywords[]`, `search_intent`, `target_word_count`, `competitor_urls[]`

### Step 2: outline (seo-outline-generate)

- **Input:** Research output JSON from step 1
- **Output:** Structured article outline with: H1 title, H2/H3 heading tree, meta_title, meta_description, suggested word count per section, internal link opportunities
- **Key output fields:** `title`, `meta_title`, `meta_description`, `slug`, `headings[]`, `sections[]`

### Step 3: write (seo-content-write)

- **Input:** Outline JSON from step 2
- **Output:** Complete article as Markdown file (`article.md`) with YAML frontmatter containing all SEO fields from the outline
- **Key output fields:** Markdown file path or inline Markdown string with frontmatter block
- **Env used:** `CONTENT_LANG` — determines content language

### Step 4: images (seo-image-generate)

- **Input:** Article Markdown from step 3
- **Output:** `image_map.json` containing paths and alt text for featured image (1200×630) and one section image per H2 heading (800×450)
- **Key output fields:** `featured_image.path`, `featured_image.alt`, `section_images[].path`, `section_images[].alt`
- **Env used:** `GOOGLE_API_KEY` — authenticates calls to the AI image generation API
- **Parallel note:** This step starts immediately after `write` and runs concurrently with the initial scoring pass of the `optimize` step where supported by the runner

### Step 5: optimize (seo-optimize-score)

- **Input:** Article Markdown from step 3; image map from step 4 via `IMAGES` env var
- **Output:** `optimized_article.md` — the article with all SEO fixes applied, plus a `score_report.json`
- **Key output fields:** `overall_score`, `breakdown`, `suggestions`
- **Env used:** `IMAGES` — path to `image_map.json` from step 4; `WORDPRESS_URL` — used to fetch sitemap for internal link suggestions
- **Quality gate:** If `overall_score < 70`, the pipeline halts. The user must review suggestions and re-run from the `optimize` step after manual edits.
- **Depends on:** both `write` (article content) and `images` (image map for injection)

### Step 6: publish (seo-publish-cms) — APPROVAL REQUIRED

- **Input:** Optimized article Markdown (`optimized_article.md`) from step 5
- **Output:** Draft post URL and post ID from WordPress
- **Approval:** The pipeline pauses before this step and presents a summary to the user. The user must confirm to proceed.
- **What is published:** A WordPress draft (never published directly — status is always `draft`)
- **Env used:** `CMS_TARGET` (currently only `wordpress` is supported), `WORDPRESS_URL`, `WORDPRESS_TOKEN`

---

## Approval Step Detail

When the pipeline reaches the `publish` step (step 6), it will display:

```
--- Approval Required ---
Step: publish (seo-publish-cms)
Target: ${WORDPRESS_URL}
Article: "<title from outline>"
Slug: <slug>
Word count: ~<N> words
SEO Score: <score>/100
Images: <N> images ready (featured + <N-1> section images)

Proceed with publishing as draft? [y/N]
```

- Answering `y` / `yes` triggers the publish step
- Answering `n` / `no` or pressing Enter stops the pipeline; `optimized_article.md` and `image_map.json` are saved locally for manual publishing later

---

## Troubleshooting

**Pipeline stops at research step with no output:**
- If `SEMRUSH_API_KEY` is not set, `seo-keyword-research` falls back to organic analysis — this is slower but still works
- Check that the input keyword is not empty

**Outline step produces generic headings:**
- The research step output may lack depth; try a more specific seed keyword
- Add competitor URLs manually to the research output JSON before running outline

**Write step outputs wrong language:**
- Confirm `CONTENT_LANG` is set to a supported code (`en` or `vi`)
- The variable must be exported before running: `export CONTENT_LANG=vi`

**Images step fails with 401 or no images generated:**
- Verify `GOOGLE_API_KEY` is exported and has not expired
- Check API quota limits — some providers throttle burst requests for multiple images
- Resume from `images` step without re-running `write`: `openclaw run seo-content-flow --from images --input article.md`

**Images step produces wrong dimensions:**
- Some image APIs require specific parameter names (`width`/`height` vs `size`/`aspect_ratio`)
- Check your provider's API docs and adjust the `seo-image-generate` skill configuration

**Optimize step halts with score < 70:**
- Review `score_report.json` suggestions — the most impactful fixes are listed first
- Common quick wins: fix meta_title length, add internal links, adjust keyword density
- After editing `article.md`, resume: `openclaw run seo-content-flow --from optimize --input article.md`
- If score is 68–69, manual minor edits often push it over the threshold

**Optimize step cannot find sitemap for internal links:**
- Ensure `WORDPRESS_URL` is set and the site's sitemap is accessible at `${WORDPRESS_URL}/sitemap.xml`
- Alternatively, provide a local JSON sitemap file to `seo-optimize-score` directly

**Publish step fails with 401:**
- Regenerate the Application Password in WP Admin > Users > Profile
- Ensure `WORDPRESS_TOKEN` format is exactly `username:app_password` (spaces in password are fine)

**Publish step fails with 404 on REST API:**
- WordPress Permalinks must not be set to "Plain" — change to "Post name" in WP Admin > Settings > Permalinks
- Some security plugins block the REST API; whitelist your IP or temporarily disable the plugin

**Flow completes but post not visible in WordPress:**
- Posts are created as `draft` — go to WP Admin > Posts > Drafts to find it
- Check the Post ID in the publish output and navigate to `/?p=<id>` to preview

**Featured image not attached after publishing:**
- Confirm `image_map.json` exists in the same directory as the article
- The `seo-publish-cms` skill reads `image_map.json` to set the featured image; if absent, the post publishes without one

**Resuming after partial failure:**
- Each step saves its output to a local file before passing to the next step
- Use `--from <step-name> --input <file>` to resume without re-running earlier steps
- Step output files: `research-output.json`, `outline.json`, `article.md`, `image_map.json`, `optimized_article.md`, `score_report.json`
