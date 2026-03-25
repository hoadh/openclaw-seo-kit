# SEO Skills Architecture

## Overview

The SEO skill suite consists of 16 interconnected components organized in 3 layers:
- **Layer 1 (Utility):** 4 shared services providing data fetching, CMS abstraction, scoring, and utilities
- **Layer 2 (Core):** 9 specialized skills for keyword research, content creation, optimization, and analysis
- **Layer 3 (Orchestration):** 3 ClawFlow workflows combining multiple skills into end-to-end pipelines

## Architecture Diagram

```
Input (Keyword/Topic)
        ↓
Layer 2 (Core Skills)
┌─────────────────────────────────────────────────────────────┐
│ [1] seo-keyword-research     → keyword_map.json             │
│     └─ requires: seo-serp-scraper                           │
│                                                              │
│ [2] seo-outline-generate     → outline.json                │
│     └─ input: keyword_map.json                             │
│                                                              │
│ [3] seo-content-write        → article.md                  │
│     └─ input: outline.json                                 │
│                                                              │
│ [4] seo-image-generate       → image_map.json              │
│     └─ input: article.md                                   │
│                                                              │
│ [5] seo-optimize-score       → optimized_article.md        │
│     └─ input: article.md + image_map.json                 │
│     └─ requires: seo-scorer                                │
│                                                              │
│ [6] seo-publish-cms          → published_url + post_id     │
│     └─ input: optimized_article.md                         │
│     └─ requires: seo-cms-adapter                           │
│                                                              │
│ [7] seo-technical-audit      → audit_report.json           │
│     └─ input: website_url                                  │
│     └─ requires: seo-serp-scraper, seo-scorer             │
│                                                              │
│ [8] seo-competitor-analyze   → competitor_report.json      │
│     └─ input: primary_keyword                             │
│     └─ requires: seo-serp-scraper                         │
│                                                              │
│ [9] seo-aeo-optimize         → optimized_content           │
│     └─ input: article.md                                   │
│     └─ AEO = AI-Enhanced Optimization                     │
└─────────────────────────────────────────────────────────────┘
        ↓ (via ClawFlow orchestration)
Layer 3 (Workflows)
┌─────────────────────────────────────────────────────────────┐
│ seo-content-flow      6-step automated pipeline             │
│ seo-audit-flow        Site audit + reporting               │
│ seo-batch-flow        Multi-article bulk processing        │
└─────────────────────────────────────────────────────────────┘

Layer 1 (Utility)
┌─────────────────────────────────────────────────────────────┐
│ seo-serp-scraper      Web search + SERP result extraction  │
│ seo-cms-adapter       Unified CMS interface (WP/Shopify)  │
│ seo-scorer            SEO scoring engine                    │
│ seo-shared-utils      Common utilities & validators        │
└─────────────────────────────────────────────────────────────┘
```

## Data Flow Chain

All processing follows a defined I/O contract:

1. **keyword_map.json** — Contains primary keyword, LSI terms, search intent, volume estimates, language
2. **outline.json** — H1 title, H2/H3 structure, meta_title, meta_description, internal link opportunities
3. **article.md** — Full Markdown with YAML frontmatter containing all SEO fields
4. **image_map.json** — Featured image (1200×630px) + section images (800×450px) with alt text
5. **optimized_article.md** — Article with SEO fixes applied + score_report.json with breakdown
6. **published_url** — CMS-specific post URL and post ID after publishing

## Layer 1: Utility Services

### seo-serp-scraper
- Performs web search queries and extracts SERP results
- Falls back gracefully when APIs unavailable
- Used by: seo-keyword-research, seo-technical-audit, seo-competitor-analyze

### seo-cms-adapter
- Abstracts CMS platforms: WordPress, Shopify, Haravan
- Unified interface for publishing, draft creation, metadata attachment
- Platform-specific authentication & API handling hidden behind adapter pattern
- Used by: seo-publish-cms

### seo-scorer
- Computes SEO scores (0-100) based on:
  - Keyword density and placement (10 points)
  - Heading structure (15 points)
  - Meta tag quality (15 points)
  - Content readability (15 points)
  - Internal link density (10 points)
  - Image optimization (10 points)
  - Structured data/schema (15 points)
  - Mobile-friendliness checks (10 points)
- Used by: seo-optimize-score, seo-technical-audit

### seo-shared-utils
- Common validators: keyword normalization, JSON schema validation
- Helpers: file I/O, error logging, multilingual utilities
- Used by: all skills

## Layer 2: Core Skills

### seo-keyword-research
- **Input:** Seed keyword or topic (string)
- **Output:** keyword_map.json
- **Process:**
  1. Normalize input keyword
  2. Perform web searches for variations (guide, tips, how-to, related)
  3. Optional: Enrich with SEMrush API (volume, difficulty)
  4. Run keyword-analyzer.py to extract LSI terms, long-tail questions, clusters
  5. Classify search intent (informational/commercial/transactional)
  6. Validate output schema
- **Language detection:** Automatic (Latin → English, Vietnamese diacritics → VI)

### seo-outline-generate
- **Input:** keyword_map.json from research
- **Output:** outline.json
- **Process:**
  1. Extract primary keyword and search intent
  2. Generate H1 title optimized for search intent
  3. Build heading structure (H2/H3) based on LSI keywords
  4. Create meta_title (60 chars), meta_description (155 chars)
  5. Calculate target word count per section
  6. Identify internal link anchor opportunities

### seo-content-write
- **Input:** outline.json
- **Output:** article.md (Markdown with YAML frontmatter)
- **Process:**
  1. Write introduction section with primary keyword natural placement
  2. Expand each H2 section based on word count targets
  3. Incorporate LSI keywords contextually
  4. Add conclusion with call-to-action
  5. Generate YAML frontmatter with all SEO fields
- **Multilingual:** Respects CONTENT_LANG env var (en/vi)

### seo-image-generate
- **Input:** article.md
- **Output:** image_map.json with local image paths
- **Process:**
  1. Generate featured image (1200×630px) based on article title
  2. Create one section image per H2 heading (800×450px)
  3. Provide descriptive alt text for each image
  4. Map images to article sections in JSON output

### seo-optimize-score
- **Input:** article.md, optional image_map.json
- **Output:** optimized_article.md, score_report.json
- **Process:**
  1. Run seo-scorer on article (baseline score)
  2. Fetch WordPress sitemap for internal linking suggestions
  3. Identify quick wins (add internal links, adjust keyword density)
  4. Inject optimizations into article
  5. Re-score and compare improvements
  6. Quality gate: halt if score < 70
- **Quality gate:** Pipeline stops if overall_score < 70/100

### seo-publish-cms
- **Input:** optimized_article.md
- **Output:** published_url, post_id
- **Process:**
  1. Load appropriate CMS adapter via seo-cms-adapter
  2. Authenticate to CMS (WP/Shopify/Haravan)
  3. Read article metadata from frontmatter
  4. Attach featured image from image_map.json (if available)
  5. Create post as draft (never auto-publish)
  6. Return post URL and ID
- **Requires approval:** Always requires user confirmation before publishing

### seo-technical-audit
- **Input:** website_url
- **Output:** audit_report.json
- **Process:**
  1. Crawl site structure (robots.txt, sitemap.xml)
  2. Check all pages for technical SEO issues
  3. Validate structured data, meta tags, performance
  4. Run seo-scorer on each page
  5. Generate issue report with severity and recommendations
- **Focus areas:**
  - Crawlability (robots.txt, sitemap, canonical tags)
  - Performance (Core Web Vitals, images optimization)
  - Mobile-friendliness (responsive design, viewport tags)
  - Schema markup (Article, BreadcrumbList, Organization)
  - Security (HTTPS, CSP headers)

### seo-competitor-analyze
- **Input:** primary_keyword
- **Output:** competitor_report.json
- **Process:**
  1. Search for SERP results for keyword
  2. Analyze top 10 ranking pages
  3. Extract: domain, page title, content length, heading structure, keyword density
  4. Score each competitor page using seo-scorer
  5. Identify common patterns in top-ranking content
  6. Recommend content gaps and opportunities

### seo-aeo-optimize
- **Input:** article.md
- **Output:** optimized_content (enhanced article)
- **Process:**
  1. AI-enhanced analysis of article quality
  2. Suggest deeper content sections (expand thin sections)
  3. Add more specific examples and case studies
  4. Enhance readability with better transitions
  5. Improve engagement through better storytelling
  6. Output enhanced version with suggestions tracked

## Layer 3: ClawFlow Workflows

### seo-content-flow
**6-step automated SEO content pipeline**

```
Step 1: research    (keyword research)
    ↓
Step 2: outline     (generate structure)
    ↓
Step 3: write       (create content)
    ↓
Step 4: images      (parallel with step 5 initial phase)
    ↓
Step 5: optimize    (score & improve, depends on 3 & 4)
    ↓ [Quality gate: score >= 70]
Step 6: publish     (CMS publishing, approval required)
```

**Execution time:** ~25 minutes end-to-end
**Quality gate:** Halts if overall_score < 70; user must review and re-run from optimize step

### seo-audit-flow
**Site audit + reporting workflow**

```
Input: website_url
    ↓
Step 1: technical-audit (crawl site, check issues)
    ↓
Step 2: generate-report (format findings, prioritize issues)
    ↓
Output: audit_report.json (issues, recommendations, priorities)
```

### seo-batch-flow
**Multi-article bulk processing**

```
Input: keywords.json (array of keywords)
    ↓
For each keyword:
  └─ Run seo-content-flow (6-step pipeline)
    ↓
Output: Array of published URLs
```

## Environment Variables

### Required (Global)
- `WORDPRESS_URL` — WordPress site URL
- `WORDPRESS_TOKEN` — `username:app_password` format
- `IMAGE_GEN_API_KEY` — AI image generation API key

### Optional (Global)
- `SEMRUSH_API_KEY` — For enhanced keyword research volume/difficulty data
- `CONTENT_LANG` — Content language code (`en` or `vi`, default: `en`)
- `CMS_TARGET` — CMS platform (`wordpress`, `shopify`, `haravan`, default: `wordpress`)

### CMS-Specific (if using Shopify or Haravan)
- `SHOPIFY_STORE_URL` — Shopify store URL
- `SHOPIFY_ACCESS_TOKEN` — Admin API token
- `SHOPIFY_BLOG_ID` — Blog ID for articles
- `HARAVAN_STORE_URL` — Haravan store URL
- `HARAVAN_ACCESS_TOKEN` — Admin API token
- `HARAVAN_BLOG_ID` — Blog ID for articles

## File Structure

Each skill directory contains:
```
seo-{skill-name}/
├── SKILL.md           # Skill documentation & specifications
├── scripts/           # Python execution scripts (stdlib-only)
│   ├── main.py        # Entry point
│   └── ...
└── references/        # Reference files (schemas, guides)
    ├── {schema}.json  # JSON schema files
    └── ...
```

Example: seo-keyword-research/
```
seo-keyword-research/
├── SKILL.md
├── scripts/
│   ├── main.py
│   └── keyword-analyzer.py
└── references/
    ├── keyword-map-schema.json
    └── search-intent-guide.md
```

## Language Support

All skills support English (en) and Vietnamese (vi):
- Language detection in keyword research (automatic)
- Content generation respects CONTENT_LANG environment variable
- Output files include language metadata in JSON/YAML
- Multilingual validators in seo-shared-utils

## Error Handling Strategy

All skills implement consistent error handling:
1. **Graceful degradation:** Optional services (SEMrush, image API) fail without halting pipeline
2. **Clear error messages:** Exit with descriptive error + suggested action
3. **Schema validation:** Mandatory JSON output validation before passing to next step
4. **Retry logic:** Single automatic retry on transient failures (network timeouts)
5. **Quality gates:** Critical steps (optimize) halt if quality thresholds not met

## Integration Points

### Adding New Skills
1. Create skill directory: `/workspace/seo-{skill-name}/`
2. Write SKILL.md with clear I/O contract
3. Implement scripts/ with stdlib-only Python
4. Add references/ with schemas or guides
5. Update this architecture document

### Adding New Workflows
1. Create ClawFlow definition in SKILL.md
2. Define step names, dependencies, and approval gates
3. Reference existing skills by name
4. Document input/output contracts between steps

### Adding CMS Support
1. Implement adapter in seo-cms-adapter/scripts/{platform}-adapter.py
2. Follow WordPressAdapter interface pattern
3. Register in adapter-interface.py factory
4. Document env vars and authentication requirements
