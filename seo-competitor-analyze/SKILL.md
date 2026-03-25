---
name: seo-competitor-analyze
description: Analyze competitors to find content gaps, keyword gaps, and backlink opportunities for SEO strategy when given target domain and competitor domains
version: 1.0.0
metadata:
  openclaw:
    requires:
      env:
        - name: SEMRUSH_API_KEY
          required: false
          description: SEMrush API key for keyword volume and backlink data
        - name: AHREFS_API_KEY
          required: false
          description: Ahrefs API key for backlink analysis
      anyBins:
        - python3
        - python
---

# SEO Competitor Analyze Skill

## Context

You are an SEO competitive intelligence analyst. Your goal is to identify content and keyword gaps between a target domain and its competitors, producing actionable gap reports.

Use `seo-serp-scraper` to enrich gap analysis with real SERP data. Prioritize gaps with evidence of search demand.

## References

- `references/gap-analysis-methodology.md` — Full methodology for content, keyword, and backlink gap analysis
- `references/backlink-analysis-guide.md` — Backlink analysis with and without paid APIs

## Steps

### 1. Accept Target and Competitor Domains

- Confirm target domain and at least 1 competitor domain were provided.
- Normalize all domains: strip `https://`, `www.`, trailing slashes.
- If no competitors provided, suggest finding them via: `web_search "[target topic] top sites"`

### 2. Fetch Sitemaps

For target and each competitor, fetch sitemap:
```
web_fetch https://domain.com/sitemap.xml
web_fetch https://domain.com/robots.txt  (to find alternate sitemap URL)
```

Parse each sitemap to extract page URLs (up to 100 per domain).
For each URL, `web_fetch` the page to extract title, meta description, and H1.

Build the input structure:
```json
{
  "target": {"pages": [{"url":"","title":"","meta":""}]},
  "competitors": [{"domain":"competitor.com", "pages": [...]}]
}
```

### 3. Run Content Gap Analysis

```bash
echo '<pages_json>' | python3 scripts/content-gap-finder.py
```

This identifies topic clusters present in competitor sitemaps but absent from target.
Review the output and flag `high` priority gaps for SERP enrichment.

### 4. Enrich Top Gaps with SERP Data

For each `high` priority content gap topic, run `seo-serp-scraper`:
- Check if a featured snippet exists (strong demand signal)
- Note PAA questions (content angle opportunities)
- Note competing domains already ranking

Limit to top 10 gaps to stay within rate limits.

### 5. Run Keyword Gap Analysis

Collect keyword signals from page titles and headings:
- Target keywords: from target domain pages
- Competitor keywords: from all competitor pages

```bash
echo '{"target_keywords": [...], "competitor_keywords": [...]}' \
  | python3 scripts/keyword-gap-analyzer.py
```

If `SEMRUSH_API_KEY` is set, enrich with volume data:
```
GET https://api.semrush.com/?type=phrase_this&phrase={keyword}&key={SEMRUSH_API_KEY}
```

### 6. Backlink Gap Analysis

If `SEMRUSH_API_KEY` or `AHREFS_API_KEY` is set, run full backlink comparison
per `references/backlink-analysis-guide.md`.

Without paid APIs, use proxy methods:
- `web_search 'link:competitor.com'` for each competitor
- Search `intitle:resources "[topic]"` to find link-worthy resource pages

### 7. Compile gap_report.md

Write `gap_report.md` with the following structure:

```markdown
# Competitor Gap Analysis: [target domain]
**Date:** [today]  **Competitors Analyzed:** [n]

## Executive Summary
[Top 3 findings in bullet points]

## Content Gaps (Priority Order)
| Topic | Competitors | Priority | Action |
|-------|-------------|----------|--------|
...

## Keyword Gaps (Top 20)
| Keyword | Competitor Count | Priority | Suggested Page |
|---------|-----------------|----------|----------------|
...

## Backlink Opportunities
[From paid API data or proxy analysis]

## Quick Wins (Implement This Week)
[3-5 specific actions with highest ROI]

## Long-Term Opportunities
[Strategic content plays for next quarter]
```

## Error Handling

- If a sitemap returns 404, try `/sitemap_index.xml` and `/news-sitemap.xml`
- If a competitor page fetch fails, skip it and continue with remaining pages
- If no keyword gaps found, check that target keyword list was properly extracted
- If SERP enrichment hits rate limits, reduce to top 5 gaps only
