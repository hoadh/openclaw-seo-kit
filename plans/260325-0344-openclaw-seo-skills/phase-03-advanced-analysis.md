---
phase: 3
title: "Advanced Analysis"
status: completed
priority: P2
effort: 12h
depends_on: [phase-01]
---

# Phase 3: Advanced Analysis

## Context Links
- [Plan Overview](plan.md)
- [Phase 1: Core Pipeline](phase-01-core-pipeline.md)
- [Phase 2: Optimization](phase-02-optimization.md)
- [Community SEO/AEO Skills](../reports/researcher-260325-0344-openclaw-seo-research.md) (section: OpenClaw SEO/AEO Ecosystem)

## Overview
Build SERP scraper utility, technical audit, competitor analysis, and AEO optimization skills. Creates seo-audit-flow combining all three analysis skills. Enables proactive SEO strategy beyond content creation.

## Key Insights
- Community `seo-aeo-diagnostics` uses 7-module 100-point scale — adopt compatible scoring for interop
- `aeo-content-strategy` mines Reddit/Quora without API keys — useful pattern for seo-competitor-analyze
- Google Search Console + Analytics tokens needed for real data; skills must work without them (degraded mode)
- AEO is distinct from SEO: citation patterns, answer formatting, topical authority > keyword density

## Requirements

### Functional
- SERP scraper: extract top-10 results, PAA boxes, related searches, featured snippets for any query
- Technical audit: crawl site for Core Web Vitals signals, structured data, sitemap, robots.txt issues
- Competitor analysis: content gaps, keyword gaps, backlink profile comparison
- AEO optimization: rewrite content for AI search citation (concise answers, structured data, authority signals)

### Non-Functional
- SERP scraper respects rate limits (1 req/sec default)
- Technical audit handles sites up to 100 pages
- All skills functional without paid APIs (SEMrush/Ahrefs); paid APIs enhance data quality
- AEO optimization preserves original SEO optimization

## Architecture

### Audit Flow
```
TARGET_URL
  -> seo-technical-audit -> audit_report.md
       |                        |
       v                        v
  seo-competitor-analyze   seo-aeo-optimize
  (uses seo-serp-scraper)     |
       |                       |
  gap_report.md            aeo_article.md
```

### I/O Contracts

**serp_results.json** (seo-serp-scraper output)
```json
{
  "query": "string",
  "results": [
    {"position": 1, "url": "string", "title": "string", "snippet": "string", "type": "organic|featured|video"}
  ],
  "paa": [{"question": "string", "snippet": "string"}],
  "related_searches": ["string"],
  "featured_snippet": {"text": "string", "url": "string"} | null
}
```

**audit_report.md** — structured markdown with scored sections:
- Technical Foundation (crawlability, indexability)
- Structured Data (schema completeness)
- Content Structure (headings, readability)
- Site Architecture (internal linking, navigation)
- Mobile/Performance (Core Web Vitals proxy signals)
- Overall score: 0-100

**gap_report.md** — markdown with:
- Content gaps (topics competitors cover, you don't)
- Keyword gaps (keywords competitors rank for, you don't)
- Backlink opportunities (sites linking to competitors)
- Priority-ranked action items

**aeo_article.md** — optimized article with:
- Concise answer blocks (2-3 sentences per question)
- FAQ schema markup enhanced
- Citation-friendly formatting
- Source attribution patterns

## Related Code Files

### Files to Create

#### seo-serp-scraper/
```
seo-serp-scraper/
├── SKILL.md
├── scripts/
│   ├── serp-parser.py               # Parse web_search/web_fetch results into structured JSON
│   └── rate-limiter.py              # Simple rate limiter for sequential requests
├── references/
│   ├── serp-results-schema.json
│   └── serp-feature-types.md        # Types of SERP features to extract
```

#### seo-technical-audit/
```
seo-technical-audit/
├── SKILL.md
├── scripts/
│   ├── site-crawler.py              # Crawl pages, check status codes, redirects
│   ├── structured-data-checker.py   # Validate JSON-LD / microdata
│   └── robots-sitemap-checker.py    # Parse robots.txt + validate sitemap
├── references/
│   ├── audit-scoring-rubric.md      # 100-point scoring breakdown
│   └── cwv-proxy-signals.md         # What to check without Lighthouse
```

#### seo-competitor-analyze/
```
seo-competitor-analyze/
├── SKILL.md
├── scripts/
│   ├── content-gap-finder.py        # Compare topic coverage between sites
│   └── keyword-gap-analyzer.py      # Find keyword ranking differences
├── references/
│   ├── gap-analysis-methodology.md
│   └── backlink-analysis-guide.md
```

#### seo-aeo-optimize/
```
seo-aeo-optimize/
├── SKILL.md
├── scripts/
│   └── aeo-formatter.py             # Format content for AI citation patterns
├── references/
│   ├── aeo-optimization-guide.md    # AI search ranking factors
│   ├── citation-patterns.md         # How AI assistants cite sources
│   └── answer-block-templates.md    # Templates for concise answer formatting
```

#### seo-audit-flow/
```
seo-audit-flow/
├── SKILL.md
```

## Implementation Steps

### 1. seo-serp-scraper (2h)
1. Create directory structure
2. Write `references/serp-feature-types.md`:
   - Organic results, featured snippets, PAA, knowledge panel, video carousel, local pack, image pack
   - Extraction rules per type
3. Write `scripts/serp-parser.py`:
   - Accept raw HTML or web_search JSON output
   - Extract structured data per feature type
   - Handle missing/partial results gracefully
   - Output serp_results.json
4. Write `scripts/rate-limiter.py`:
   - Simple token bucket: configurable requests/sec (default 1)
   - Used by other scripts that call web_search/web_fetch in loops
5. Write `references/serp-results-schema.json`
6. Write SKILL.md:
   - Description: "Scrape and parse search engine results pages extracting organic results, PAA boxes, featured snippets, and related searches for SEO analysis"
   - Tools: web_search, web_fetch
   - Steps: (1) accept query string, (2) web_search query, (3) web_fetch top results for snippet extraction, (4) parse with serp-parser.py, (5) rate limit between fetches, (6) output serp_results.json

### 2. seo-technical-audit (4h)
1. Create directory structure
2. Write `references/audit-scoring-rubric.md` (7 modules, 100 points total):
   - Technical foundation: 20 pts (status codes, redirects, canonical tags)
   - Search accessibility: 15 pts (robots.txt, sitemap, meta robots)
   - Structured data: 15 pts (JSON-LD presence, validity, completeness)
   - Content structure: 15 pts (heading hierarchy, readability, keyword signals)
   - Multimedia: 10 pts (alt text, image optimization signals)
   - Content quality: 15 pts (freshness, word count, uniqueness signals)
   - Site architecture: 10 pts (internal linking, navigation depth)
3. Write `references/cwv-proxy-signals.md`:
   - Without Lighthouse: check image sizes, render-blocking resources, lazy loading attrs
   - HTML size, external script count as proxy metrics
4. Write `scripts/site-crawler.py`:
   - Accept root URL + max pages (default 20)
   - Crawl via web_fetch, collect status codes, titles, meta, headings
   - Respect robots.txt
   - Output structured page data JSON
5. Write `scripts/structured-data-checker.py`:
   - Extract JSON-LD blocks from HTML
   - Validate against Schema.org requirements
   - Score completeness
6. Write `scripts/robots-sitemap-checker.py`:
   - Fetch /robots.txt, parse rules
   - Fetch /sitemap.xml, validate format, check for broken URLs (sample)
7. Write SKILL.md:
   - Description: "Run comprehensive technical SEO audit checking crawlability, structured data, content structure, and site architecture with scored report when given a website URL"
   - Requires env: [GOOGLE_SEARCH_CONSOLE_TOKEN] (optional), anyBins: [python3, python]
   - Tools: web_fetch, exec
   - Steps: (1) accept target URL, (2) run robots-sitemap-checker.py, (3) crawl site with site-crawler.py (max 20 pages), (4) check structured data per page, (5) score each module per rubric, (6) compile audit_report.md with scores + actionable fixes
   - Error handling: blocked by robots.txt -> report as finding, GSC unavailable -> skip GSC data

### 3. seo-competitor-analyze (3h)
1. Create directory structure
2. Write `references/gap-analysis-methodology.md`:
   - Content gap: compare topic clusters between target and competitors via SERP overlap
   - Keyword gap: compare ranking keywords (SEMrush if available, else SERP-based estimation)
   - Backlink: compare linking domains (Ahrefs if available, else skip)
3. Write `references/backlink-analysis-guide.md`
4. Write `scripts/content-gap-finder.py`:
   - Accept two sitemaps or URL lists
   - Categorize pages by topic (from titles/meta)
   - Find topics in competitor not in target
   - Output gap list with priority scores
5. Write `scripts/keyword-gap-analyzer.py`:
   - Use serp-scraper results for target keywords
   - Identify keywords where competitor ranks but target doesn't
   - Prioritize by estimated volume
6. Write SKILL.md:
   - Description: "Analyze competitors to find content gaps, keyword gaps, and backlink opportunities for SEO strategy when given target domain and competitor domains"
   - Requires env: [SEMRUSH_API_KEY] (optional), [AHREFS_API_KEY] (optional)
   - Steps: (1) accept target domain + competitor list, (2) fetch sitemaps for all domains, (3) run content-gap-finder.py, (4) for top gap keywords run seo-serp-scraper, (5) run keyword-gap-analyzer.py, (6) if SEMrush/Ahrefs available enrich with volume/backlink data, (7) compile gap_report.md with prioritized actions

### 4. seo-aeo-optimize (2h)
1. Create directory structure
2. Write `references/aeo-optimization-guide.md`:
   - AI search ranking factors: topical authority, citation-friendly formatting, structured answers
   - Differences from traditional SEO
   - Google AI Overview, ChatGPT, Perplexity citation patterns
3. Write `references/citation-patterns.md`:
   - How AI assistants select and cite sources
   - Optimal answer length (2-3 sentences for featured answers)
   - Authority signals AI models look for
4. Write `references/answer-block-templates.md`:
   - Template for concise answer blocks
   - FAQ enhancement patterns
   - "What is X" / "How to X" answer formats
5. Write `scripts/aeo-formatter.py`:
   - Parse article sections
   - Insert concise answer blocks after each H2
   - Enhance FAQ schema with direct answers
   - Add "TL;DR" summary at top
   - Output aeo_article.md
6. Write SKILL.md:
   - Description: "Optimize article for AI search engines (Google AI Overview, ChatGPT, Perplexity) by adding citation-friendly formatting and answer blocks when preparing content for AEO"
   - No env vars required (pure LLM + formatter)
   - Steps: (1) read article.md, (2) analyze current AEO readiness, (3) add concise answer blocks per section, (4) enhance FAQ with direct answers, (5) add TL;DR summary, (6) run aeo-formatter.py for structural changes, (7) verify SEO score not degraded (run seo-scorer), (8) save aeo_article.md

### 5. seo-audit-flow (1h)
1. Write SKILL.md with ClawFlow definition:
   ```yaml
   name: seo-audit-flow
   description: Comprehensive site audit with technical, competitor, and AEO analysis
   workflows:
     - name: tech-audit
       skill: seo-technical-audit
       env: { TARGET_URL: "${INPUT}" }
     - name: competitor
       skill: seo-competitor-analyze
       dependsOn: tech-audit
       env: { TARGET_DOMAIN: "${INPUT}", AUDIT_DATA: "${tech-audit.output}" }
     - name: aeo-check
       skill: seo-aeo-optimize
       dependsOn: tech-audit
       env: { SITE_DATA: "${tech-audit.output}" }
   ```
2. Document that competitor and aeo-check run in parallel after tech-audit

## Todo List
- [x] Create seo-serp-scraper/ directory structure
- [x] Write serp-parser.py + rate-limiter.py
- [x] Write serp-feature-types.md + serp-results-schema.json
- [x] Write seo-serp-scraper/SKILL.md
- [x] Test SERP scraper against 5 sample queries
- [x] Create seo-technical-audit/ directory structure
- [x] Write audit-scoring-rubric.md + cwv-proxy-signals.md
- [x] Write site-crawler.py + structured-data-checker.py + robots-sitemap-checker.py
- [x] Write seo-technical-audit/SKILL.md
- [x] Test audit against 3 sample sites
- [x] Create seo-competitor-analyze/ directory structure
- [x] Write gap-analysis-methodology.md + backlink-analysis-guide.md
- [x] Write content-gap-finder.py + keyword-gap-analyzer.py
- [x] Write seo-competitor-analyze/SKILL.md
- [x] Test competitor analysis with known domain pair
- [x] Create seo-aeo-optimize/ directory structure
- [x] Write aeo-optimization-guide.md + citation-patterns.md + answer-block-templates.md
- [x] Write aeo-formatter.py
- [x] Write seo-aeo-optimize/SKILL.md
- [x] Test AEO optimization preserves SEO score
- [x] Create seo-audit-flow/SKILL.md
- [x] Integration test: full audit-flow on sample domain
- [x] Validate all SKILL.md files against ClawHub checklist

## Success Criteria
- SERP scraper extracts all feature types for 90%+ of queries
- Technical audit produces actionable report with scored modules (0-100)
- Competitor analysis identifies at least 10 content gaps for typical domain pair
- AEO optimization does not reduce SEO score (seo-scorer delta >= 0)
- Audit-flow completes in < 30 min for site with 20 pages

## Risk Assessment

| Risk | Impact | Mitigation |
|------|--------|------------|
| SERP scraping blocked/rate-limited | High | Use web_search tool (not raw scraping); rate-limiter.py; fallback to cached results |
| Technical audit misses JS-rendered content | Medium | Document limitation; note that web_fetch may not execute JS |
| Competitor data sparse without paid APIs | Medium | SERP-based estimation as baseline; SEMrush/Ahrefs as enhancement |
| AEO best practices evolving rapidly | Medium | Keep references/ docs updatable; version aeo-optimization-guide.md |
| Site crawler overwhelms target server | Low | Max 20 pages default; 1 req/sec rate limit; respect robots.txt |

## Security Considerations
- GOOGLE_SEARCH_CONSOLE_TOKEN, SEMRUSH_API_KEY, AHREFS_API_KEY in env only
- Site crawler respects robots.txt disallow rules
- No data exfiltration: all analysis results stay local
- Rate limiting prevents accidental DoS on target sites

## Next Steps
- Phase 4 integrates audit findings into batch-flow for agency reporting
- Consider: audit_report.md format should be stable — used as input by batch-flow reports
- AEO guide needs quarterly review as AI search landscape evolves
