---
name: seo-optimize-score
description: "Optimize article SEO score by fixing readability, injecting internal links, improving keyword placement, and adding schema markup when article scores below target"
metadata:
  openclaw:
    type: skill
    requires:
      anyBins:
        - python3
        - python
      optionalEnv:
        - WORDPRESS_URL
---

# seo-optimize-score

## Overview

Runs after `seo-scorer` to bring a low-scoring article up to the 80+ publishing threshold. Applies targeted fixes per dimension rather than rewriting the whole article.

**Optimization order (to avoid conflicts):**
1. Meta quality — frontmatter only
2. Heading structure — structural changes
3. Keyword density — after structure is stable
4. Internal links — after body text is finalized
5. Readability — last, since rewrites affect density
6. Schema markup — append-only

---

## Requirements

- Article must be a markdown file with valid YAML frontmatter
- `seo-scorer` skill must be available (run first to get baseline score)
- `WORDPRESS_URL` env var used to auto-fetch sitemap for link suggestions (optional)
- If `WORDPRESS_URL` is not set, provide a local JSON sitemap file path instead

---

## Steps

### Step 1 — Score the article

Run `seo-scorer` on the article to get the baseline score:

```bash
python3 seo-scorer/scripts/seo-score-calculator.py <article.md> > score_report.json
```

Read `score_report.json` and check `overall_score`.

### Step 2 — Skip if already optimized

If `overall_score >= 80`, output:

```
Article score is 83/100 — meets the 80-point target. No optimization needed.
```

Then stop. Do not modify the article.

### Step 3 — Apply fixes per low-scoring dimension

For each dimension with score below its threshold, apply the corresponding fix from `references/optimization-rules.md`.

Apply in this order:

#### 3a. Meta quality (threshold: < 15/20)

Edit the YAML frontmatter directly:
- Adjust `meta_title` to 50–60 chars containing `primary_keyword`
- Adjust `meta_description` to 120–160 chars containing `primary_keyword`

#### 3b. Heading structure (threshold: < 15/20)

- Ensure exactly one `# H1` heading that contains or references the primary keyword
- Ensure at least 2 `## H2` headings
- Ensure at least 1 `### H3` heading

#### 3c. Keyword density (threshold: < 14/20)

- If primary keyword density < 0.5%: insert keyword naturally in intro and conclusion
- If primary keyword density > 3%: replace some occurrences with pronouns or synonyms

#### 3d. Internal links (threshold: < 12/15)

Run the link suggester:

```bash
# With WordPress sitemap (auto-detected from WORDPRESS_URL env var)
python3 seo-optimize-score/scripts/internal-link-suggester.py \
  <article.md> \
  "${WORDPRESS_URL}/sitemap.xml"

# With local JSON sitemap file
python3 seo-optimize-score/scripts/internal-link-suggester.py \
  <article.md> \
  sitemap-pages.json
```

The JSON sitemap file format:
```json
[
  {"url": "/blog/related-post", "title": "Related Post Title"},
  {"url": "/guide/topic", "title": "Topic Guide"}
]
```

For each suggestion in the output, inject the link at the `context` location:
- Find the `anchor_text` in the sentence
- Replace with `[anchor_text](target_url)`
- Add only enough links to reach the recommended count

#### 3e. Readability (threshold: < 18/25)

Rewrite flagged paragraphs (avg sentence length > 22 words):
- Split long sentences at conjunctions: and, but, because, which, that, however
- Replace complex words with simpler equivalents
- Break paragraphs with > 5 sentences into two shorter ones
- **Do not rewrite:** code blocks, blockquotes, tables

### Step 4 — Agent rewrites low-readability sections

For each paragraph flagged in Step 3e, rewrite in place keeping:
- The same factual content and meaning
- The primary keyword present (check density after rewrite)
- Sentences under 20 words each

### Step 5 — Run internal-link-suggester.py

Already covered in Step 3d. Confirm links were injected and verify the count meets the target.

### Step 6 — Inject JSON-LD schema

Determine the appropriate schema type using `references/schema-injection-guide.md`:

| Article type | Schema |
|---|---|
| Has numbered steps or "How to" sections | `HowTo` |
| Has FAQ section with 3+ Q&A pairs | `FAQPage` |
| General informational article | `Article` |

Append the filled-in template at the end of the article as a fenced `json-ld` block:

````markdown
```json-ld
{
  "@context": "https://schema.org",
  "@type": "Article",
  ...
}
```
````

### Step 7 — Add schema markup

Already covered in Step 6. Only inject schema if the article does not already contain a `json-ld` fenced block.

### Step 8 — Re-score the article

Run `seo-scorer` again on the modified article:

```bash
python3 seo-scorer/scripts/seo-score-calculator.py <article.md>
```

Report the before/after scores:

```
Optimization complete.

Before: 62/100
After:  84/100

Breakdown improvement:
  Keyword Density:   12 → 18  (+6)
  Readability:       15 → 22  (+7)
  Heading Structure: 15 → 20  (+5)
  Internal Links:     8 → 12  (+4)
  Meta Quality:      12 → 12  (no change)
```

If the score is still below 80, identify the remaining low dimensions and explain what manual intervention is needed.

### Step 9 — Save optimized_article.md

Write the final optimized article to `optimized_article.md` in the same directory as the original.

If the score reached >= 80, the article is ready to pass to `seo-publish-cms`.

---

## Optimization Rules Reference

Full rules for each dimension: `references/optimization-rules.md`

Full JSON-LD templates: `references/schema-injection-guide.md`

---

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `WORDPRESS_URL` | No | Base URL for auto-fetching `sitemap.xml` for link suggestions |

---

## Troubleshooting

**Score did not improve after optimization:**
- Check if the article has enough body content (< 300 words makes scoring unreliable)
- Verify `primary_keyword` is set in frontmatter
- Some dimensions require manual rewrites — review suggestions from `seo-scorer`

**internal-link-suggester.py returns empty array:**
- Verify the sitemap URL is accessible and returns valid XML
- For local JSON, confirm format: `[{"url": "...", "title": "..."}]`
- Ensure article keywords match page titles/URLs in the sitemap

**Schema already exists warning:**
- If article already has a `json-ld` block, skip schema injection to avoid duplicates
- To update schema, remove the existing block first then re-run

**Re-score is lower than expected:**
- Readability rewrites may have changed keyword density — check density dimension
- If density dropped after rewriting, add keyword back in intro or conclusion
