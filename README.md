# OpenClaw SEO Skill Suite

Full-auto SEO pipeline for OpenClaw: keyword research through publishing, technical audits, competitor analysis, and AEO optimization. Supports WordPress/Shopify/Haravan, Vietnamese/English multilingual.

## Skills

### Core Pipeline

| Skill | Description |
|-------|-------------|
| `seo-keyword-research` | Research keywords with intent analysis, LSI discovery, clustering |
| `seo-outline-generate` | Generate article outline with heading hierarchy, meta tags, schema markup |
| `seo-content-write` | Write full SEO article from outline with multilingual support (VI/EN) |
| `seo-publish-cms` | Publish article to CMS with media upload, categories, tags |

### Optimization

| Skill | Description |
|-------|-------------|
| `seo-scorer` | Score article SEO quality (keyword density, readability, headings, links, meta) 0-100 |
| `seo-optimize-score` | Auto-fix SEO issues: readability, internal links, schema markup injection |
| `seo-image-generate` | Generate SEO-optimized images with alt text using AI image generation |

### Advanced Analysis

| Skill | Description |
|-------|-------------|
| `seo-serp-scraper` | Parse SERPs: organic results, PAA, featured snippets, related searches |
| `seo-technical-audit` | Technical SEO audit: crawlability, structured data, site architecture (0-100) |
| `seo-competitor-analyze` | Content gaps, keyword gaps, backlink opportunities vs competitors |
| `seo-aeo-optimize` | Optimize for AI search engines (Google AI Overview, ChatGPT, Perplexity) |

### Utility

| Skill | Description |
|-------|-------------|
| `seo-cms-adapter` | Unified CMS API for WordPress, Shopify, Haravan |
| `seo-shared-utils` | Shared frontmatter parser used across skills |

### Workflows (ClawFlow)

| Workflow | Description |
|----------|-------------|
| `seo-content-flow` | Full 6-step pipeline: research -> outline -> write -> images -> optimize -> publish |
| `seo-audit-flow` | Technical audit + competitor analysis + AEO check |
| `seo-batch-flow` | Batch process keyword list through content pipeline |

## Requirements

- Python 3.7+
- OpenClaw framework (`openclaw` command)

No pip dependencies — all scripts use Python stdlib only.

## Install

```bash
git clone <this-repo> && cd <this-repo>
./install.sh
```

This symlinks all 16 components to `~/.openclaw/skills/`. Updates to the repo flow through automatically.

### Options

```bash
./install.sh --copy       # Copy files instead of symlink (portable)
./install.sh --dry-run    # Preview without changes
./install.sh --target DIR # Custom skills directory
```

### Environment Variables

Set these before running skills that need them:

| Variable | Required By | Description |
|----------|-------------|-------------|
| `WORDPRESS_URL` | seo-publish-cms | WordPress site URL |
| `WORDPRESS_TOKEN` | seo-publish-cms | WordPress Application Password |
| `SHOPIFY_STORE_URL` | seo-cms-adapter | Shopify store URL |
| `SHOPIFY_ACCESS_TOKEN` | seo-cms-adapter | Shopify Admin API token |
| `SHOPIFY_BLOG_ID` | seo-cms-adapter | Shopify blog ID |
| `HARAVAN_STORE_URL` | seo-cms-adapter | Haravan store URL |
| `HARAVAN_ACCESS_TOKEN` | seo-cms-adapter | Haravan API token |
| `HARAVAN_BLOG_ID` | seo-cms-adapter | Haravan blog ID |
| `SEMRUSH_API_KEY` | seo-keyword-research, seo-competitor-analyze | Optional: enriches keyword data |
| `AHREFS_API_KEY` | seo-competitor-analyze | Optional: backlink analysis |
| `IMAGE_GEN_API_KEY` | seo-image-generate | AI image generation API key |
| `GOOGLE_SEARCH_CONSOLE_TOKEN` | seo-technical-audit | Optional: GSC data |
| `CMS_TARGET` | seo-publish-cms | `wordpress` (default), `shopify`, or `haravan` |
| `CONTENT_LANG` | seo-content-write | `en` (default) or `vi` |

## Uninstall

```bash
./uninstall.sh
```

Only removes symlinks pointing to this repo (safe).

```bash
./uninstall.sh --force    # Also remove copied installs
./uninstall.sh --dry-run  # Preview without changes
```

## Quick Start

```bash
# Publish an SEO article from keyword to WordPress draft
openclaw run seo-content-flow "best laptop for video editing"

# Run technical audit on a site
openclaw run seo-audit-flow "https://mysite.com"

# Batch process keywords
openclaw run seo-batch-flow keywords.txt

# Score an existing article
openclaw run seo-scorer article.md
```

## Architecture

```
Layer 3 (Orchestration)     seo-content-flow | seo-audit-flow | seo-batch-flow
                                    |                |                |
Layer 2 (Core Skills)       keyword-research    technical-audit    batch-runner
                            outline-generate    competitor-analyze
                            content-write       aeo-optimize
                            image-generate
                            optimize-score
                            publish-cms
                                    |                |
Layer 1 (Utility)           seo-scorer | seo-cms-adapter | seo-serp-scraper | seo-shared-utils
```

## Data Flow (Content Pipeline)

```
keyword (string)
  -> seo-keyword-research -> keyword_map.json
    -> seo-outline-generate -> outline.json
      -> seo-content-write -> article.md
        +-> seo-image-generate -> image_map.json
        +-> seo-optimize-score -> optimized_article.md (quality gate: score >= 70)
          -> seo-publish-cms -> published URL (draft)
```

## Documentation

Detailed docs in [`docs/`](docs/):

- [Getting Started](docs/seo-getting-started.md)
- [Skills Reference](docs/seo-skills-reference.md) (all I/O contracts)
- [Architecture](docs/seo-architecture.md)
- [Troubleshooting](docs/seo-troubleshooting.md)

## License

MIT-0
