# SEO Workflow Documentation

## Overview

The SEO skill suite provides automated content creation from keyword research through CMS publishing. This document describes the main workflows and their execution.

## 6-Step Content Pipeline (seo-content-flow)

Automated end-to-end SEO content generation:

| Step | Skill | Input | Output | Time |
|------|-------|-------|--------|------|
| 1 | seo-keyword-research | Seed keyword | keyword_map.json | 2-3 min |
| 2 | seo-outline-generate | keyword_map.json | outline.json | 1 min |
| 3 | seo-content-write | outline.json | article.md | 3-4 min |
| 4 | seo-image-generate | article.md | image_map.json | 5-8 min |
| 5 | seo-optimize-score | article.md + images | optimized_article.md | 2-3 min |
| 6 | seo-publish-cms | optimized_article.md | post_url + post_id | 1-2 min |

**Total execution time:** ~25 minutes
**Quality gate:** Step 5 halts if SEO score < 70/100

### How to Run

```bash
# Basic usage
export WORDPRESS_URL="https://your-site.com"
export WORDPRESS_TOKEN="username:app_password"
export GOOGLE_API_KEY="your-api-key"

openclaw run seo-content-flow "best running shoes for beginners"
```

### Resume from Any Step

```bash
# Start from outline if research already done
openclaw run seo-content-flow --from outline --input keyword_map.json

# Start from optimize if content written but needs re-scoring
openclaw run seo-content-flow --from optimize --input article.md

# Just publish after manual review
openclaw run seo-content-flow --from publish --input optimized_article.md
```

## Additional Workflows

### Site Audit (seo-audit-flow)
```bash
openclaw run seo-audit-flow "https://your-site.com"
# Output: audit_report.json with technical SEO issues and recommendations
```

### Batch Processing (seo-batch-flow)
```bash
# Process multiple keywords from file
openclaw run seo-batch-flow keywords.json
# Keywords.json format: [{ keyword: "...", lang: "en"|"vi" }, ...]
```

## Multilingual Support

### English (en)
```bash
export CONTENT_LANG=en
openclaw run seo-content-flow "best laptop for video editing"
```

### Vietnamese (vi)
```bash
export CONTENT_LANG=vi
openclaw run seo-content-flow "máy tính xách tay tốt nhất"
# Language auto-detected from diacritics
```

## Multi-CMS Support

### WordPress (default)
```bash
export CMS_TARGET=wordpress
export WORDPRESS_URL="https://example.com"
export WORDPRESS_TOKEN="user:password"
openclaw run seo-content-flow "keyword"
```

### Shopify
```bash
export CMS_TARGET=shopify
export SHOPIFY_STORE_URL="https://mystore.myshopify.com"
export SHOPIFY_ACCESS_TOKEN="shpat_..."
export SHOPIFY_BLOG_ID=123456
openclaw run seo-content-flow "keyword"
```

### Haravan (Vietnam e-commerce)
```bash
export CMS_TARGET=haravan
export HARAVAN_STORE_URL="https://mystore.haravan.com"
export HARAVAN_ACCESS_TOKEN="token..."
export HARAVAN_BLOG_ID=123456
openclaw run seo-content-flow "keyword"
```

## Data Flow Diagram

```
Input Keyword
    ↓
[1] Keyword Research
    ↓ keyword_map.json
[2] Outline Generation
    ↓ outline.json
[3] Content Writing
    ↓ article.md
    ├─→ [4] Image Generation
    │       ↓ image_map.json
    │       ↓
    └─→ [5] Score Optimization
            ↓ optimized_article.md + score_report.json
            ↓ [Quality gate: score >= 70]
        [6] CMS Publishing
            ↓
        Published URL (Draft)
```

## Key Features

- **Automatic keyword research** with LSI term discovery
- **Search intent classification** (informational, commercial, transactional)
- **AI content generation** with natural keyword placement
- **Image generation** (featured + section images)
- **SEO scoring** (0-100 scale with actionable suggestions)
- **Internal link optimization** using site sitemap
- **Multi-CMS publishing** (WordPress, Shopify, Haravan)
- **Multilingual content** (English, Vietnamese, auto-detected)
- **Quality gates** (halts if score < 70)
- **Approval-based publishing** (always creates draft, never auto-publishes)

## Environment Variables

### Required
- `WORDPRESS_URL` — Your WordPress site URL
- `WORDPRESS_TOKEN` — `username:app_password` format
- `GOOGLE_API_KEY` — AI image generation API key

### Optional
- `SEMRUSH_API_KEY` — For keyword volume/difficulty (gracefully skipped if absent)
- `CONTENT_LANG` — `en` (default) or `vi`
- `CMS_TARGET` — `wordpress` (default), `shopify`, or `haravan`

## Troubleshooting

| Issue | Solution |
|-------|----------|
| No keyword research results | Try broader keyword; check internet connection |
| Article scored < 70 | Review score_report.json suggestions; edit; re-run optimize |
| Images failed to generate | Check GOOGLE_API_KEY validity and quota |
| Can't publish to WordPress | Verify WORDPRESS_TOKEN and REST API enabled (Settings > Permalinks) |
| Content in wrong language | Set CONTENT_LANG before running |
| Resume doesn't work | Ensure output files (keyword_map.json, article.md, etc.) exist locally |

## Output Files

After running seo-content-flow:

```
./
├── keyword_map.json        # Step 1 output
├── outline.json            # Step 2 output
├── article.md              # Step 3 output
├── image_map.json          # Step 4 output
├── optimized_article.md    # Step 5 output
├── score_report.json       # Step 5 quality metrics
└── publish_result.json     # Step 6 result
```

All intermediate outputs are saved to current directory for inspection and resuming.

## Next Steps

- **Learn architecture:** See [seo-architecture.md](./seo-architecture.md)
- **Skill details:** See [seo-skills-reference.md](./seo-skills-reference.md)
- **Individual skill docs:** See SKILL.md in each skill directory