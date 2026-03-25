---
name: seo-audit-flow
description: Comprehensive site audit combining technical SEO audit, competitor analysis, and AEO optimization in a single automated workflow
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
        - name: GOOGLE_SEARCH_CONSOLE_TOKEN
          required: false
          description: GSC API token for impression and click data
      anyBins:
        - python3
        - python
    clawflow:
      name: seo-audit-flow
      description: Comprehensive site audit with technical, competitor, and AEO analysis
      estimatedDuration: 30m
      steps:
        - name: tech-audit
          skill: seo-technical-audit
          input: "${INPUT}"
          description: "Run technical SEO audit on target site"
        - name: competitor
          skill: seo-competitor-analyze
          dependsOn: tech-audit
          input: "${INPUT}"
          env:
            AUDIT_DATA: "${tech-audit.output}"
          description: "Analyze competitors for content and keyword gaps"
        - name: aeo-check
          skill: seo-aeo-optimize
          dependsOn: tech-audit
          input: "${INPUT}"
          env:
            AUDIT_CONTEXT: "${tech-audit.output}"
          description: "Check and optimize existing site pages for AI search engine visibility"
---

# SEO Audit Flow Skill

## Context

This ClawFlow orchestration skill runs a comprehensive three-phase SEO audit
combining technical crawl analysis, competitive gap analysis, and AI engine
optimization — all from a single target URL input.

The `competitor` and `aeo-check` steps run **in parallel** after `tech-audit`
completes, cutting total execution time roughly in half.

## Flow Diagram

```
INPUT (target URL + competitor domains)
        │
        ▼
┌───────────────────┐
│   tech-audit      │  ~10 min
│ seo-technical-    │  Crawls site, scores 7 modules,
│ audit             │  outputs audit_report.md
└────────┬──────────┘
         │
    ┌────┴────┐  (parallel)
    │         │
    ▼         ▼
┌───────┐  ┌──────────┐
│compet-│  │aeo-check │  ~10 min each
│itor   │  │seo-aeo-  │
│seo-   │  │optimize  │
│compet-│  │          │
│itor-  │  │Formats   │
│analyze│  │top pages │
│       │  │for AI    │
│Finds  │  │citation  │
│gaps   │  └──────────┘
└───────┘
    │         │
    └────┬────┘
         ▼
   Final Report
   (merged outputs)
```

## Input Format

```json
{
  "target_url": "https://example.com",
  "competitor_domains": ["competitor1.com", "competitor2.com"],
  "max_pages": 20,
  "focus_keyword": "optional primary keyword for context"
}
```

Or pass as plain URL string — the flow will use default settings.

## Steps

### Phase 1: Technical Audit (Sequential, ~10 min)

Runs `seo-technical-audit` on the target URL:
- Fetches robots.txt and sitemap.xml
- Crawls up to 20 pages
- Checks structured data, content structure, and CWV proxy signals
- Produces `audit_report.md` and structured JSON output

Output is stored as `tech-audit.output` and passed to both Phase 2 steps.

### Phase 2a: Competitor Analysis (Parallel, ~10 min)

Runs `seo-competitor-analyze` using:
- Target URL from `${INPUT}`
- Technical audit data from `${tech-audit.output}` (provides crawled page list)
- Competitor domains from `${INPUT}`

Produces `gap_report.md` with content gaps, keyword gaps, and backlink opportunities.

### Phase 2b: AEO Check and Optimization (Parallel, ~10 min)

Runs `seo-aeo-optimize` using:
- Target URL from `${INPUT}` — the skill fetches existing site pages directly
- Technical audit findings from `AUDIT_CONTEXT` env var (provides crawled page list and scores as reference context)
- Checks each live page against AEO readiness criteria
- Applies `aeo-formatter.py` to pages needing optimization
- Produces `aeo_report.md` with per-page AEO scores and formatted versions

### Phase 3: Merge Final Report

After both Phase 2 steps complete, compile `full_audit_report.md`:

```markdown
# Comprehensive SEO Audit: [domain]
**Date:** [today]  **Duration:** ~30 minutes

## Executive Summary
[Top 5 findings across all three audits]

## Technical SEO Score: [X/100]
[Summary from audit_report.md — link to full report]

## Competitor Gap Summary
[Top 5 gaps from gap_report.md — link to full report]

## AEO Readiness Summary
[AEO score and top optimizations from aeo_report.md]

## Prioritized Action Plan

### This Week (High Impact, Low Effort)
1. [Action from technical audit]
2. [Action from competitor gaps]
3. [AEO quick win]

### This Month (High Impact, Medium Effort)
[3-5 actions across all three areas]

### This Quarter (Strategic)
[Long-term plays from competitor and AEO analysis]

## Output Files
- `audit_report.md` — Full technical audit
- `gap_report.md` — Full competitor gap analysis
- `aeo_report.md` — Full AEO optimization report
```

## Environment Variables

| Variable | Required | Used By | Purpose |
|----------|----------|---------|---------|
| `SEMRUSH_API_KEY` | No | competitor step | Keyword volume, backlink data |
| `AHREFS_API_KEY` | No | competitor step | Backlink analysis |
| `GOOGLE_SEARCH_CONSOLE_TOKEN` | No | tech-audit step | GSC impression/click data |

All steps work without API keys using web_search and web_fetch as fallbacks.

## Estimated Execution Time

| Step | Duration | Notes |
|------|----------|-------|
| tech-audit | 8–12 min | Depends on site size and page count |
| competitor (parallel) | 8–12 min | Depends on competitor count |
| aeo-check (parallel) | 5–10 min | Depends on article count |
| Report merge | 2–3 min | |
| **Total** | **~25–35 min** | Parallel execution saves ~10 min |

## Troubleshooting

**tech-audit fails to crawl:**
- Check if site blocks bots (User-agent restrictions in robots.txt)
- Reduce `max_pages` to 5 for initial test
- Verify target URL is accessible (not behind login or paywall)

**competitor step finds no gaps:**
- Ensure competitor domains are provided in input
- Check that competitor sitemaps are publicly accessible
- Try adding more competitors (3–5 recommended)

**aeo-check produces no changes:**
- Article may already be well-optimized for AEO
- Check that input pages are markdown or have extractable text
- Verify `aeo-formatter.py` is executable: `python3 -c "import py_compile; py_compile.compile('scripts/aeo-formatter.py')"`

**Rate limiting during web_fetch:**
- Use `seo-serp-scraper`'s `rate-limiter.py` with `--rate 0.5` for aggressive sites
- Add `"crawl_delay": 2` to input JSON to slow down crawling

## Output Files

All output files are written to the current working directory:

```
./audit_report.md       — Technical SEO audit (from seo-technical-audit)
./gap_report.md         — Competitor gap analysis (from seo-competitor-analyze)
./aeo_report.md         — AEO optimization report (from seo-aeo-optimize)
./full_audit_report.md  — Merged executive summary (this flow)
```
