# Brainstorm Report: OpenClaw SEO Skill Suite
**Date:** 2026-03-25
**Status:** Agreed — Ready for Implementation Plan

---

## Problem Statement
Build comprehensive SEO skill suite for OpenClaw platform covering:
- All SEO roles: writer, specialist, agency, ecommerce
- All platforms: WordPress, Shopify, Haravan (multi-platform)
- Multilingual: Vietnamese + English + extensible
- Integrations: Google Tools, Ahrefs/SEMrush, AI-only analysis
- Full automation: keyword input → auto-publish
- Extended: Technical audit, competitor analysis, AEO optimization

## Current State
- SEO workflow doc exists (6-step concept) — no implementation yet
- OpenClaw platform supports Skills (SKILL.md) + ClawFlows (YAML pipelines)
- Community has AEO/SEO skills available for reference

---

## Agreed Architecture: 3-Layer Modular Design

### Layer 1: Utility Skills (Shared Helpers)

| Skill | Purpose | OpenClaw Tools |
|-------|---------|----------------|
| **seo-serp-scraper** | Scrape SERP, PAA, Related Searches | `web_search`, `web_fetch` |
| **seo-cms-adapter** | Abstract CMS API (WP/Shopify/Haravan) | `exec`, `web_fetch` |
| **seo-scorer** | Score SEO quality (keyword density, readability, headings, links) | `read`, `exec` |

### Layer 2: Core Skills (9 Composable Units)

| # | Skill | Function | I/O Contract |
|---|-------|----------|--------------|
| 1 | **seo-keyword-research** | Search intent, LSI/long-tail, clustering, volume estimate | keyword/URL → keyword_map.json |
| 2 | **seo-outline-generate** | H2/H3 outline, meta title/desc, schema markup suggestion | keyword_map → outline.json |
| 3 | **seo-content-write** | Write article per outline, natural keyword placement, multilang | outline → article.md |
| 4 | **seo-image-generate** | Thumbnail + section images, SEO alt text | article → images/ + image_map.json |
| 5 | **seo-optimize-score** | Score, internal link suggest, readability fix, schema inject | article → optimized_article.md |
| 6 | **seo-publish-cms** | Publish to WP/Shopify/Haravan with media, tags, categories | article + images → published URL |
| 7 | **seo-technical-audit** | Core Web Vitals, structured data, sitemap, robots.txt, mobile | URL → audit_report.md |
| 8 | **seo-competitor-analyze** | Content gap, keyword gap, backlink profile, SERP tracking | domain list → gap_report.md |
| 9 | **seo-aeo-optimize** | Optimize for AI search (Google AI Overview, ChatGPT, Perplexity) | article → aeo_article.md |

### Layer 3: ClawFlows (Full-Auto Workflows)

#### 1. seo-content-flow (Main 6-step pipeline)
```yaml
name: seo-content-flow
description: Full-auto SEO content from keyword to publish
workflows:
  - name: research
    skill: seo-keyword-research
    env: { KEYWORD: "${INPUT}" }
  - name: outline
    skill: seo-outline-generate
    dependsOn: research
    env: { KEYWORD_MAP: "${research.output}" }
  - name: write
    skill: seo-content-write
    dependsOn: outline
    env: { OUTLINE: "${outline.output}", LANG: "${LANG}" }
  - name: images
    skill: seo-image-generate
    dependsOn: write
    env: { ARTICLE: "${write.output}" }
  - name: optimize
    skill: seo-optimize-score
    dependsOn: [write, images]
    env: { ARTICLE: "${write.output}", IMAGES: "${images.output}" }
  - name: publish
    skill: seo-publish-cms
    dependsOn: optimize
    approval: true
    env: { CONTENT: "${optimize.output}", CMS: "${CMS_TARGET}" }
```

#### 2. seo-audit-flow (Technical + Content audit)
```yaml
name: seo-audit-flow
description: Comprehensive site audit with tech, competitor, and AEO analysis
workflows:
  - name: tech-audit
    skill: seo-technical-audit
    env: { TARGET_URL: "${INPUT}" }
  - name: competitor
    skill: seo-competitor-analyze
    dependsOn: tech-audit
    env: { AUDIT_DATA: "${tech-audit.output}" }
  - name: aeo-check
    skill: seo-aeo-optimize
    dependsOn: tech-audit
    env: { SITE_DATA: "${tech-audit.output}" }
```

#### 3. seo-batch-flow (Agency bulk processing)
```yaml
name: seo-batch-flow
description: Batch process keyword list through content pipeline
# Iterates keyword list, runs seo-content-flow per keyword
# Supports parallel execution for agency scale
```

---

## Environment Variables

| Variable | Purpose | Required By |
|----------|---------|-------------|
| `GOOGLE_SEARCH_CONSOLE_TOKEN` | GSC API access | technical-audit, competitor-analyze |
| `GOOGLE_ANALYTICS_TOKEN` | GA4 traffic data | competitor-analyze |
| `SEMRUSH_API_KEY` | Keyword/backlink data | keyword-research, competitor-analyze |
| `AHREFS_API_KEY` | Alternative to SEMrush | keyword-research, competitor-analyze |
| `WORDPRESS_URL` + `WORDPRESS_TOKEN` | WP REST API | publish-cms |
| `SHOPIFY_STORE` + `SHOPIFY_TOKEN` | Shopify Admin API | publish-cms |
| `HARAVAN_STORE` + `HARAVAN_TOKEN` | Haravan API | publish-cms |
| `GOOGLE_API_KEY` | Image generation service | image-generate |

## OpenClaw Tools Required
- **Low-risk**: `read`, `list`, `search`, `web_search`, `web_fetch`, `memory`
- **Medium-risk**: `write` (save outputs)
- **High-risk**: `exec` (run Python/Node scripts)

---

## Implementation Phases

### Phase 1: Core Pipeline (MVP)
- seo-keyword-research
- seo-outline-generate
- seo-content-write
- seo-publish-cms (WordPress first)
- seo-content-flow (basic chain)

### Phase 2: Optimization
- seo-scorer (utility)
- seo-optimize-score
- seo-image-generate
- seo-content-flow (complete 6-step)

### Phase 3: Advanced Analysis
- seo-serp-scraper (utility)
- seo-technical-audit
- seo-competitor-analyze
- seo-aeo-optimize
- seo-audit-flow

### Phase 4: Scale & Polish
- seo-cms-adapter (multi-platform)
- seo-batch-flow (agency bulk)
- Shopify + Haravan adapter scripts
- Multilingual support hardening
- Monitoring & reporting dashboard

---

## Risk Assessment

| Risk | Impact | Mitigation |
|------|--------|------------|
| API rate limits (GSC, SEMrush) | Medium | Backoff + caching in scripts |
| Content quality inconsistency | High | seo-scorer as quality gate, threshold-based rejection |
| Multi-CMS API divergence | Medium | seo-cms-adapter abstract layer |
| Multilingual complexity | Medium | Language param via env, locale-aware prompts |
| SKILL.md 500-line limit | Low | Heavy logic in scripts/, domain knowledge in references/ |
| OpenClaw version changes | Low | Pin tool versions, follow ClawHub practices |

## Success Metrics
- Full pipeline runs keyword → published article in < 10 minutes
- SEO score > 80/100 on generated articles
- Support 3 CMS platforms without skill changes (only adapter swap)
- Batch flow handles 50+ keywords per run for agency use
- AEO optimization improves AI citation rate by measurable %

## References
- [OpenClaw Docs](https://docs.openclaw.ai/)
- [Community Skills](https://github.com/VoltAgent/awesome-openclaw-skills)
- [SEO Workflow Doc](/workspace/docs/seo-workflow.md)
- [Research Report](/workspace/plans/reports/researcher-260325-0344-openclaw-seo-research.md)
