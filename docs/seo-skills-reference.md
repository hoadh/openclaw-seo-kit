# SEO Skills Reference Guide

Quick reference for all 16 SEO components with input/output contracts and dependencies.

## Layer 1: Utility Services

| Skill | Purpose | Input | Output | Dependencies |
|-------|---------|-------|--------|--------------|
| **seo-serp-scraper** | Web search & SERP extraction | Query string | JSON array of results | None (stdlib only) |
| **seo-cms-adapter** | Unified CMS interface | CMS_TARGET env var | Adapter instance | None (stdlib only) |
| **seo-scorer** | SEO scoring engine (0-100) | article.md | JSON score report | None (stdlib only) |
| **seo-shared-utils** | Common validators & helpers | Varies | Varies | None (stdlib only) |

## Layer 2: Core Skills

### 1. seo-keyword-research
**Discover primary keyword, LSI terms, search intent, and volume estimates**

```yaml
Input:
  - seed_keyword: string (e.g., "running shoes for beginners")
  - optional: language hint from keyword diacritics

Output: keyword_map.json
  - primary_keyword: string
  - search_intent: "informational" | "commercial" | "transactional" | "navigational"
  - lsi_keywords: [string] (10-20 related terms)
  - long_tail: [string] (5-15 long-tail questions)
  - clusters: [{ name, keywords: [string] }] (keyword groups)
  - volume_estimate: "low" | "medium" | "high"
  - language: "en" | "vi"
  - competitor_urls: [string] (top 5 SERP links)

Environment:
  - SEMRUSH_API_KEY: optional (enhances volume/difficulty data)

Dependencies:
  - seo-serp-scraper (for web search)

Execution: ~2-3 minutes
```

**When to use:** Start of any SEO workflow; before content creation
**Key output:** keyword_map.json drives all downstream skills

---

### 2. seo-outline-generate
**Create content structure from keyword research**

```yaml
Input: keyword_map.json
  - primary_keyword
  - search_intent
  - lsi_keywords
  - long_tail questions

Output: outline.json
  - h1_title: string (optimized for search intent)
  - meta_title: string (max 60 chars)
  - meta_description: string (max 155 chars)
  - slug: string (URL-friendly)
  - headings: [{ level, text, keyword_focus }]
  - sections: [{ h2, h3_list, word_count_target, link_opportunities }]
  - schema_type: "Article" | "NewsArticle" | "HowTo"

Execution: ~1 minute
```

**Depends on:** seo-keyword-research
**Key output:** outline.json used by seo-content-write

---

### 3. seo-content-write
**Generate full article from outline**

```yaml
Input: outline.json
  - h1_title, meta fields, sections with word count targets

Output: article.md (Markdown with YAML frontmatter)
---
title: <h1>
meta_title: <60 chars>
meta_description: <155 chars>
slug: <url-friendly>
language: en | vi
schema_type: Article
word_count: <N>
---
<Full article in Markdown with H2/H3 structure>

Environment:
  - CONTENT_LANG: "en" (default) | "vi"

Execution: ~3-4 minutes
```

**Depends on:** seo-outline-generate
**Language support:** English (en), Vietnamese (vi)
**Key output:** article.md consumed by seo-image-generate and seo-optimize-score

---

### 4. seo-image-generate
**Create featured and section images**

```yaml
Input: article.md
  - h1 title (for featured image)
  - each H2 heading (for section images)

Output: image_map.json
{
  "featured_image": {
    "path": "images/featured-123.jpg",
    "alt": "Featured image alt text",
    "size": "1200x630"
  },
  "section_images": [
    {
      "h2_heading": "Section title",
      "path": "images/section-1-123.jpg",
      "alt": "Section image alt text",
      "size": "800x450"
    }
  ]
}

Environment:
  - GOOGLE_API_KEY: required (AI image generation API key)

Execution: ~5-8 minutes (concurrent with optimize initial phase)
```

**Depends on:** seo-content-write
**Runs in parallel with:** seo-optimize-score (can start immediately after write)
**Key output:** image_map.json injected by seo-optimize-score

---

### 5. seo-optimize-score
**Score article and apply SEO improvements**

```yaml
Input:
  - article.md (from seo-content-write)
  - optional: IMAGES env var pointing to image_map.json

Output:
  - optimized_article.md (improved version)
  - score_report.json
    {
      "overall_score": 0-100,
      "breakdown": {
        "keyword_optimization": 0-10,
        "heading_structure": 0-15,
        "meta_tags": 0-15,
        "readability": 0-15,
        "internal_links": 0-10,
        "images": 0-10,
        "structured_data": 0-15,
        "mobile_friendly": 0-10
      },
      "suggestions": [
        { "issue": "...", "impact": "high|medium|low", "fix": "..." }
      ]
    }

Environment:
  - WORDPRESS_URL: optional (fetches sitemap for internal link suggestions)

Dependencies:
  - seo-scorer (for scoring engine)

Execution: ~2-3 minutes
Quality Gate: HALTS if overall_score < 70
```

**Critical:** Depends on both seo-content-write and seo-image-generate (if images used)
**Quality gate:** If score < 70, user must review score_report.json suggestions and re-run from this step
**Key output:** optimized_article.md (ready for publishing)

---

### 6. seo-publish-cms
**Publish optimized article to CMS**

```yaml
Input: optimized_article.md
  - YAML frontmatter with title, meta fields, slug
  - optional: image_map.json (same directory)

Output:
  - post_url: string (e.g., "https://site.com/?p=123")
  - post_id: integer
  - status: "draft" (never auto-published)

Environment:
  - CMS_TARGET: "wordpress" (default) | "shopify" | "haravan"
  - WORDPRESS_URL: required if CMS_TARGET=wordpress
  - WORDPRESS_TOKEN: required if CMS_TARGET=wordpress
  - (Shopify/Haravan env vars if using those platforms)

Dependencies:
  - seo-cms-adapter (for CMS platform abstraction)

Execution: ~1-2 minutes
Approval: REQUIRED (user confirms before publishing)
```

**Always creates as draft:** Never directly publishes; post must be reviewed and published manually
**Image handling:** Automatically attaches featured image from image_map.json (if present)
**Multi-CMS:** Supports WordPress, Shopify, Haravan via adapter pattern

---

### 7. seo-technical-audit
**Analyze website for technical SEO issues**

```yaml
Input:
  - website_url: string (e.g., "https://example.com")

Output: audit_report.json
  {
    "site_url": "...",
    "crawl_date": "2026-03-25T...",
    "pages_crawled": 42,
    "issues": [
      {
        "page_url": "...",
        "severity": "critical" | "high" | "medium" | "low",
        "issue_type": "broken_link" | "missing_meta" | "poor_performance" | ...,
        "description": "...",
        "recommendation": "..."
      }
    ],
    "score_by_page": { "page_url": 0-100, ... }
  }

Dependencies:
  - seo-serp-scraper (for crawling)
  - seo-scorer (for page scoring)

Execution: ~5-10 minutes (depends on site size)
```

**Focus areas:**
- Crawlability (robots.txt, sitemap, canonical tags)
- Performance (Core Web Vitals, image optimization)
- Mobile-friendliness (responsive, viewport tags)
- Schema markup (Article, BreadcrumbList, Organization)
- Security (HTTPS, CSP headers)

---

### 8. seo-competitor-analyze
**Analyze top-ranking competitors for keyword**

```yaml
Input:
  - primary_keyword: string

Output: competitor_report.json
  {
    "keyword": "...",
    "serp_results": [
      {
        "rank": 1-10,
        "domain": "...",
        "page_title": "...",
        "url": "...",
        "content_length": 2500,
        "heading_structure": { "h1": 1, "h2": 5, "h3": 12 },
        "keyword_density": 2.4,
        "seo_score": 82,
        "common_lsi_keywords": ["...", "..."]
      }
    ],
    "gap_analysis": {
      "top_competitor_strengths": ["..."],
      "content_gaps": ["..."],
      "opportunities": ["..."]
    }
  }

Dependencies:
  - seo-serp-scraper (for SERP analysis)
  - seo-scorer (for page scoring)

Execution: ~3-4 minutes
```

**Analyzes:** Top 10 ranking pages for the keyword
**Gap analysis:** Identifies opportunities and missing content topics

---

### 9. seo-aeo-optimize
**AI-Enhanced article optimization (beyond traditional SEO)**

```yaml
Input: article.md

Output:
  - enhanced_content: string (improved article Markdown)
  - enhancement_report: JSON
    {
      "original_score": 75,
      "enhanced_score": 88,
      "improvements": [
        { "type": "expanded_section", "h2": "...", "added_paragraphs": 3 },
        { "type": "added_examples", "count": 2 },
        { "type": "improved_readability", "flesch_kincaid": "7.2 → 6.8" }
      ]
    }

Execution: ~2-3 minutes
```

**Focus:** Content depth, storytelling, engagement, specificity
**Output:** Enhanced article with suggestions tracked (non-destructive)

---

## Layer 3: ClawFlow Workflows

### seo-content-flow
**Full 6-step automated SEO content pipeline**

```yaml
Input:
  - seed_keyword: string (or existing keyword_map.json)

Steps:
  1. research       → keyword_map.json
  2. outline        → outline.json
  3. write          → article.md
  4. images         → image_map.json
  5. optimize       → optimized_article.md + score_report.json
  6. publish        → post_url + post_id

Environment:
  - WORDPRESS_URL: required
  - WORDPRESS_TOKEN: required
  - GOOGLE_API_KEY: required
  - SEMRUSH_API_KEY: optional
  - CONTENT_LANG: optional ("en" default | "vi")
  - CMS_TARGET: optional ("wordpress" default)

Execution: ~25 minutes total
Quality Gate: Halts at step 5 if score < 70

Resume Examples:
  openclaw run seo-content-flow --from outline --input research-output.json
  openclaw run seo-content-flow --from optimize --input article.md
```

---

### seo-audit-flow
**Site audit workflow**

```yaml
Input:
  - website_url: string

Steps:
  1. technical-audit    → raw audit findings
  2. generate-report    → formatted audit_report.json

Output: audit_report.json (prioritized issues + recommendations)

Execution: ~8-12 minutes
```

---

### seo-batch-flow
**Process multiple keywords in sequence**

```yaml
Input:
  - keywords.json: [{ keyword: "...", lang: "en"|"vi" }, ...]

Process:
  For each keyword:
    - Run seo-content-flow (6-step pipeline)
    - Collect published URLs

Output: batch_results.json
  {
    "total_keywords": 10,
    "successful": 9,
    "failed": 1,
    "results": [
      { "keyword": "...", "post_url": "...", "post_id": 123, "status": "published" }
    ]
  }

Execution: 25 minutes × number_of_keywords
```

---

## Quick Start Scenarios

### Generate single article from keyword
```bash
openclaw run seo-content-flow "best laptop for video editing"
```

### Audit existing website
```bash
openclaw run seo-audit-flow "https://mysite.com"
```

### Analyze competitors for keyword
```bash
openclaw run seo-competitor-analyze "fitness tracker watch"
```

### Publish to Shopify instead of WordPress
```bash
export CMS_TARGET=shopify
export SHOPIFY_STORE_URL="https://mystore.myshopify.com"
export SHOPIFY_ACCESS_TOKEN="shpat_..."
export SHOPIFY_BLOG_ID=123456

openclaw run seo-content-flow "eco-friendly water bottle"
```

### Generate Vietnamese content
```bash
export CONTENT_LANG=vi
openclaw run seo-content-flow "máy tính xách tay tốt nhất 2026"
```

### Resume pipeline after failed step
```bash
# Resume from optimize if write succeeded but images failed
openclaw run seo-content-flow --from optimize --input article.md

# After manual fixes to article, re-score
openclaw run seo-content-flow --from optimize --input article-fixed.md
```

---

## Output File Locations

After running seo-content-flow, outputs appear in current working directory:

```
./
├── keyword_map.json          (step 1)
├── outline.json              (step 2)
├── article.md                (step 3)
├── image_map.json            (step 4)
├── optimized_article.md      (step 5)
├── score_report.json         (step 5)
└── publish_result.json       (step 6)
```

Resume from any point using existing output files as inputs.

---

## Error Recovery

| Error | Solution |
|-------|----------|
| Research: 0 search results | Try broader keyword; remove modifiers (remove "guide", "tips") |
| Outline: Generic headings | Try more specific seed keyword; add competitor URLs manually |
| Write: Wrong language | Set `CONTENT_LANG=vi` or `en` before running |
| Images: 401 API error | Regenerate GOOGLE_API_KEY; check quota limits |
| Optimize: Score < 70 | Review score_report.json suggestions; edit article; re-run from optimize |
| Publish: 401 on WordPress | Regenerate Application Password in WP Admin > Users |
| Publish: 404 REST API | Change Permalinks to "Post name" in WP Admin > Settings |

---

## Dependency Graph

```
seo-shared-utils (used by all)
    ↓
seo-serp-scraper ←─── seo-keyword-research ──→ seo-outline-generate
                       seo-technical-audit
                       seo-competitor-analyze

seo-cms-adapter ←───────── seo-publish-cms

seo-scorer ←─── seo-optimize-score
                seo-technical-audit

seo-keyword-research → seo-outline-generate → seo-content-write → seo-image-generate
                                                ↓                      ↓
                                            seo-optimize-score ←──────┘
                                                ↓
                                            seo-publish-cms
```

---

## Multilingual Support Matrix

All skills support English (en) and Vietnamese (vi):

| Skill | en | vi | Auto-detect |
|-------|----|----|-------------|
| seo-keyword-research | ✓ | ✓ | ✓ (diacritics) |
| seo-outline-generate | ✓ | ✓ | From keyword_map |
| seo-content-write | ✓ | ✓ | CONTENT_LANG env |
| seo-image-generate | ✓ | ✓ | From article.md |
| seo-optimize-score | ✓ | ✓ | From article.md |
| seo-publish-cms | ✓ | ✓ | From frontmatter |
| seo-technical-audit | ✓ | ✓ | Report only (en) |
| seo-competitor-analyze | ✓ | ✓ | Report only (en) |

---

## Integration Checklist

Before deploying SEO skill suite:

- [ ] All env vars configured (WORDPRESS_URL, TOKEN, GOOGLE_API_KEY)
- [ ] SEMrush API key set (optional, gracefully skipped if absent)
- [ ] WordPress site has REST API enabled (check Settings > Permalinks)
- [ ] Image generation API quota verified
- [ ] Python 3.7+ available on system (all scripts use stdlib only)
- [ ] Test seo-content-flow on one keyword end-to-end
- [ ] Verify published post appears in WordPress Drafts
- [ ] Configure CMS_TARGET if using Shopify/Haravan
