---
title: "OpenClaw SEO Skill Suite"
description: "15 skills + 3 ClawFlow workflows for full-auto SEO pipeline"
status: completed
priority: P1
effort: 40h
tags: [seo, openclaw, skills, automation, clawflow]
created: 2026-03-25
completed: 2026-03-25
---

# OpenClaw SEO Skill Suite

## Overview
15 composable OpenClaw skills (3 utility + 9 core + 3 orchestration) and 3 ClawFlow workflows enabling full-auto SEO: keyword research through publishing, technical audits, competitor analysis, and AEO optimization. Supports WP/Shopify/Haravan, VI/EN multilingual.

## Architecture
- **Layer 1 (Utility):** seo-serp-scraper, seo-cms-adapter, seo-scorer
- **Layer 2 (Core):** 9 skills with defined I/O contracts (keyword_map.json -> outline.json -> article.md -> optimized_article.md -> URL)
- **Layer 3 (ClawFlows):** seo-content-flow, seo-audit-flow, seo-batch-flow

## Phase Summary

| Phase | Skills | Workflow | Effort | Status | Details |
|-------|--------|----------|--------|--------|---------|
| 1 - Core Pipeline | keyword-research, outline-generate, content-write, publish-cms | content-flow (basic) | 12h | completed | [phase-01](phase-01-core-pipeline.md) |
| 2 - Optimization | seo-scorer, optimize-score, image-generate | content-flow (full) | 10h | completed | [phase-02](phase-02-optimization.md) |
| 3 - Advanced Analysis | serp-scraper, technical-audit, competitor-analyze, aeo-optimize | audit-flow | 12h | completed | [phase-03](phase-03-advanced-analysis.md) |
| 4 - Scale & Polish | cms-adapter (refactor), batch-flow, Shopify/Haravan, multilingual | batch-flow | 6h | completed | [phase-04](phase-04-scale-and-polish.md) |

## Dependencies
```
Phase 1 (MVP) ──> Phase 2 (Optimization) ──> Phase 4 (Scale)
                                          \
Phase 1 ──────> Phase 3 (Analysis) ──────> Phase 4
```

## File Ownership Matrix (Parallel Execution)

| Owner | Files |
|-------|-------|
| Dev A | seo-keyword-research/, seo-outline-generate/, seo-content-write/ |
| Dev B | seo-publish-cms/, seo-cms-adapter/, seo-scorer/ |
| Dev C | seo-technical-audit/, seo-competitor-analyze/, seo-serp-scraper/ |
| Dev D | seo-image-generate/, seo-optimize-score/, seo-aeo-optimize/ |
| Integrator | seo-content-flow/, seo-audit-flow/, seo-batch-flow/ |

## Key Constraints
- Each SKILL.md < 500 lines; heavy logic in scripts/, schemas in references/
- All dependency versions pinned; no pipe-to-interpreter
- Credentials via env vars only; declare in metadata.openclaw.requires.env
- MIT-0 license for ClawHub publishing

## Implementation Notes

### Additional Artifacts Created
- **seo-cms-adapter/scripts/shopify-base-adapter.py** — Shared base class for Shopify API patterns, extended by both shopify-adapter and haravan-adapter

### Code Quality Metrics
- **Code review score**: 8/10 (all critical/high issues resolved)
- **Python compilation**: All 23 scripts compile without errors
- **Smoke tests**: All core pipelines functional
- **Architecture adherence**: Clean separation of concerns, proper abstraction layers

### Skill Distribution
- Layer 1 (Utility): seo-serp-scraper, seo-cms-adapter, seo-scorer
- Layer 2 (Core): seo-keyword-research, seo-outline-generate, seo-content-write, seo-publish-cms, seo-optimize-score, seo-image-generate, seo-technical-audit, seo-competitor-analyze, seo-aeo-optimize
- Layer 3 (Orchestration): seo-content-flow, seo-audit-flow, seo-batch-flow

## Research Reports
- [Brainstorm](../reports/brainstorm-260325-0344-openclaw-seo-skills.md)
- [Platform Research](../reports/researcher-260325-0344-openclaw-seo-research.md)
