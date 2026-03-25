---
name: seo-technical-audit
description: Run comprehensive technical SEO audit checking crawlability, structured data, content structure, and site architecture with scored report when given a website URL
version: 1.0.0
metadata:
  openclaw:
    requires:
      env:
        - name: GOOGLE_SEARCH_CONSOLE_TOKEN
          required: false
          description: GSC API token for impression/click data. Skill works without it.
      anyBins:
        - python3
        - python
---

# SEO Technical Audit Skill

## Context

You are a technical SEO auditor. Your goal is to crawl a target website, evaluate it across 7 scoring modules, and produce a comprehensive `audit_report.md` with actionable recommendations.

Score each module per `references/audit-scoring-rubric.md`. Use `references/cwv-proxy-signals.md` for performance signals without Lighthouse.

## References

- `references/audit-scoring-rubric.md` — 7 modules, 100-point scoring system
- `references/cwv-proxy-signals.md` — Core Web Vitals proxy signals from HTML analysis

## Steps

### 1. Accept Target URL

- Confirm a URL was provided (e.g., `https://example.com`).
- Normalize: ensure `https://` prefix, strip trailing slash.
- If missing, exit with: `"Error: target URL is required"`.

### 2. Fetch robots.txt and sitemap.xml

```
web_fetch https://example.com/robots.txt
web_fetch https://example.com/sitemap.xml
```

Pipe both to `robots-sitemap-checker.py`:

```bash
echo '{"robots_txt": "<content>", "sitemap_xml": "<content>"}' \
  | python3 scripts/robots-sitemap-checker.py
```

Record the module 2 score and issues from the output.

### 3. Crawl Site Pages

Use `web_fetch` to retrieve up to 20 pages starting from the homepage.
Collect URLs from the sitemap (up to 20) or follow internal links.

Build the pages input array:
```json
{"pages": [{"url": "https://...", "html": "<html>...", "status": 200}], "max_pages": 20}
```

Run `site-crawler.py`:
```bash
echo '<pages_json>' | python3 scripts/site-crawler.py
```

Collect per-page data: title, meta description, headings, word count, internal links, image alt coverage.

### 4. Check Structured Data Per Page

For each page with JSON-LD present, pipe HTML to `structured-data-checker.py`:

```bash
echo '<html_content>' | python3 scripts/structured-data-checker.py
```

Aggregate findings: types found, missing required fields, overall structured data score.

### 5. Score Each Module

Using data collected in steps 2–4, score each module per `audit-scoring-rubric.md`:

| Module | Max | Data Source |
|--------|-----|-------------|
| Technical Foundation | 20 | site-crawler.py (status, canonical, title uniqueness) |
| Search Accessibility | 15 | robots-sitemap-checker.py |
| Structured Data | 15 | structured-data-checker.py |
| Content Structure | 15 | site-crawler.py (H1, meta, headings) |
| Multimedia | 10 | site-crawler.py (alt text, image counts) |
| Content Quality | 15 | site-crawler.py (word count, freshness) |
| Site Architecture | 10 | site-crawler.py (internal links, depth) |

Also apply CWV proxy checks from `cwv-proxy-signals.md` to each page HTML.

### 6. Compile audit_report.md

Write `audit_report.md` with the following structure:

```markdown
# Technical SEO Audit: [domain]
**Date:** [today]  **Overall Score:** [X/100] ([Grade])

## Executive Summary
[2-3 sentence summary of major findings]

## Module Scores
| Module | Score | Grade |
|--------|-------|-------|
...

## Critical Issues
[List of blockers requiring immediate action]

## High Priority Recommendations
[Top 5 recommendations with expected impact]

## Module Details
[Per-module findings with specific URLs and data]

## CWV Proxy Assessment
[Performance signals from HTML analysis]

## Next Steps
[Prioritized action plan]
```

## Error Handling

- If `web_fetch` returns non-200, record the status and continue with remaining pages
- If `robots.txt` returns 404, note it as a missing file (deduct points from module 2)
- If `sitemap.xml` returns 404, note it and check robots.txt for alternate sitemap URL
- If a page has no HTML content, skip it and note in report
