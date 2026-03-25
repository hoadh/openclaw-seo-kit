---
phase: 4
title: "Scale & Polish"
status: completed
priority: P2
effort: 6h
depends_on: [phase-02, phase-03]
---

# Phase 4: Scale & Polish

## Context Links
- [Plan Overview](plan.md)
- [Phase 1: Core Pipeline](phase-01-core-pipeline.md)
- [Phase 2: Optimization](phase-02-optimization.md)
- [Phase 3: Advanced Analysis](phase-03-advanced-analysis.md)

## Overview
Refactor CMS publishing into abstract adapter pattern supporting WP/Shopify/Haravan. Build batch-flow for agency-scale keyword processing. Harden multilingual support. This phase upgrades existing skills — minimal new skills created.

## Key Insights
- seo-publish-cms (Phase 1) already handles WP — refactor to use seo-cms-adapter as abstraction layer
- Shopify uses Admin API (GraphQL), Haravan uses REST API similar to Shopify — adapter pattern critical
- Batch-flow iterates seo-content-flow per keyword — needs parallel execution + progress tracking
- Multilingual hardening: VI tone rules, EN style guide already in references; need locale-aware scoring in seo-scorer

## Requirements

### Functional
- CMS adapter abstracts: create_post, upload_media, set_categories, set_tags, get_sitemap across 3 platforms
- Batch-flow processes keyword list file, runs content-flow per keyword, reports progress
- Vietnamese content passes seo-scorer with locale-appropriate rules
- Shopify/Haravan publish creates blog posts with SEO metadata

### Non-Functional
- Adapter swap requires only env var change (CMS_TARGET=shopify)
- Batch-flow handles 50+ keywords without memory issues
- Language switching requires no code changes (env var LANG=vi|en)

## Architecture

### CMS Adapter Pattern
```
seo-publish-cms (SKILL.md)
  -> reads CMS_TARGET env var
  -> delegates to seo-cms-adapter
     -> seo-cms-adapter/scripts/
        ├── adapter-interface.py     # Abstract base
        ├── wp-adapter.py            # WordPress REST API
        ├── shopify-adapter.py       # Shopify Admin GraphQL API
        └── haravan-adapter.py       # Haravan REST API
```

### Batch Flow
```
keyword_list.txt (one keyword per line)
  -> seo-batch-flow
     -> for each keyword:
        -> seo-content-flow (full 6-step)
     -> aggregate results
     -> batch_report.md
```

### I/O Contracts

**CMS Adapter Interface** (all adapters implement):
```python
class CMSAdapter:
    def create_post(title, content, slug, meta, status="draft") -> post_id
    def upload_media(file_path, alt_text) -> media_url
    def set_categories(post_id, categories) -> bool
    def set_tags(post_id, tags) -> bool
    def get_sitemap() -> list[str]  # URLs
    def get_post_url(post_id) -> str
```

**batch_report.md**:
- Summary: X keywords processed, Y published, Z failed
- Per-keyword: keyword, SEO score, status, published URL or error
- Execution time per keyword + total

## Related Code Files

### Files to Create

#### seo-cms-adapter/
```
seo-cms-adapter/
├── SKILL.md
├── scripts/
│   ├── adapter-interface.py         # ABC with required methods
│   ├── wp-adapter.py                # WordPress REST API implementation
│   ├── shopify-adapter.py           # Shopify Admin API (GraphQL)
│   └── haravan-adapter.py           # Haravan REST API implementation
├── references/
│   ├── shopify-api-reference.md     # Key endpoints, auth, blog post creation
│   └── haravan-api-reference.md     # Key endpoints, auth, blog post creation
```

#### seo-batch-flow/
```
seo-batch-flow/
├── SKILL.md
├── scripts/
│   └── batch-runner.py              # Iterate keywords, invoke content-flow, aggregate report
├── references/
│   └── batch-report-template.md     # Report format template
```

### Files to Modify
- `seo-publish-cms/SKILL.md` — update to use seo-cms-adapter instead of direct WP calls
- `seo-publish-cms/scripts/wp-publisher.py` — replace with adapter delegation
- `seo-scorer/scripts/seo-score-calculator.py` — add locale-aware scoring (VI readability)
- `seo-scorer/references/scoring-rubric.md` — add VI-specific scoring criteria
- `seo-content-write/references/multilingual-rules.md` — expand VI/EN rules

## Implementation Steps

### 1. seo-cms-adapter (3h)
1. Create directory structure
2. Write `scripts/adapter-interface.py`:
   ```python
   from abc import ABC, abstractmethod

   class CMSAdapter(ABC):
       @abstractmethod
       def authenticate(self) -> bool: ...
       @abstractmethod
       def create_post(self, title, content, slug, meta, status="draft") -> dict: ...
       @abstractmethod
       def upload_media(self, file_path, alt_text) -> str: ...
       @abstractmethod
       def set_categories(self, post_id, categories) -> bool: ...
       @abstractmethod
       def set_tags(self, post_id, tags) -> bool: ...
       @abstractmethod
       def get_sitemap(self) -> list: ...
       @abstractmethod
       def get_post_url(self, post_id) -> str: ...
   ```
3. Write `scripts/wp-adapter.py` — migrate logic from Phase 1 wp-publisher.py
4. Write `scripts/shopify-adapter.py`:
   - Shopify Admin API (GraphQL): `POST /admin/api/2024-01/graphql.json`
   - Create blog article: `blogArticleCreate` mutation
   - Upload media: staged upload -> file create
   - Handle Shopify SEO fields (title, description)
5. Write `scripts/haravan-adapter.py`:
   - Haravan REST API (Shopify-compatible subset)
   - `POST /admin/blogs/{id}/articles.json`
   - Media upload via asset API
6. Write `references/shopify-api-reference.md` + `references/haravan-api-reference.md`
7. Write SKILL.md:
   - Description: "Abstract CMS adapter providing unified API for publishing to WordPress, Shopify, and Haravan when any SEO skill needs CMS interaction"
   - Requires env: varies by CMS (declared per adapter)
   - Steps: (1) read CMS_TARGET env var, (2) load appropriate adapter, (3) authenticate, (4) expose unified methods to calling skill

### 2. Refactor seo-publish-cms (1h)
1. Update SKILL.md to delegate to seo-cms-adapter
2. Replace wp-publisher.py with adapter-based publisher:
   ```python
   import json, os, sys
   CMS = os.environ.get("CMS_TARGET", "wordpress")
   # Import appropriate adapter
   # Call adapter.create_post(), adapter.upload_media(), etc.
   ```
3. Update env requirements: add CMS_TARGET, keep WP/Shopify/Haravan envs as conditional

### 3. Multilingual Hardening (1h)
1. Update `seo-scorer/scripts/seo-score-calculator.py`:
   - Add `detect_language()` function (check frontmatter `lang` field)
   - VI readability: sentence length avg < 25 words, no syllable-based FK
   - VI keyword density: account for Vietnamese compound words
2. Update `seo-scorer/references/scoring-rubric.md` with VI-specific criteria
3. Update `seo-content-write/references/multilingual-rules.md`:
   - VI: formal register for business, informal for lifestyle
   - VI: SEO title patterns (common Vietnamese search patterns)
   - EN: no changes needed

### 4. seo-batch-flow (1h)
1. Write `scripts/batch-runner.py`:
   ```python
   # Pseudocode
   import json, sys, time

   def run_batch(keyword_file, lang, cms_target):
       keywords = open(keyword_file).read().strip().split('\n')
       results = []
       for kw in keywords:
           # Invoke seo-content-flow via ClawFlow API or sequential skill calls
           result = run_content_flow(kw, lang, cms_target)
           results.append(result)
           # Rate limit between runs
       return generate_report(results)
   ```
2. Write `references/batch-report-template.md`
3. Write SKILL.md:
   - Description: "Batch process keyword list through full SEO content pipeline for agency-scale content production when given a keyword list file"
   - Requires env: inherits from seo-content-flow dependencies
   - Steps: (1) read keyword_list.txt, (2) validate keywords (non-empty, dedup), (3) for each keyword invoke seo-content-flow, (4) collect results + scores, (5) generate batch_report.md, (6) report summary to user
   - Error handling: single keyword failure doesn't halt batch; log error, continue

## Todo List
- [x] Create seo-cms-adapter/ directory structure
- [x] Write adapter-interface.py (ABC)
- [x] Write wp-adapter.py (migrate from Phase 1)
- [x] Write shopify-adapter.py
- [x] Write haravan-adapter.py
- [x] Write shopify-api-reference.md + haravan-api-reference.md
- [x] Write seo-cms-adapter/SKILL.md
- [x] Refactor seo-publish-cms to use adapter
- [x] Test WP adapter (regression — should behave same as Phase 1)
- [x] Test Shopify adapter against staging store
- [x] Test Haravan adapter against staging store
- [x] Update seo-scorer for VI locale-aware scoring
- [x] Update multilingual-rules.md
- [x] Test VI article scoring produces reasonable scores
- [x] Create seo-batch-flow/ directory structure
- [x] Write batch-runner.py
- [x] Write batch-report-template.md
- [x] Write seo-batch-flow/SKILL.md
- [x] Test batch-flow with 5-keyword list
- [x] Validate all new/modified SKILL.md files against ClawHub checklist
- [x] End-to-end test: batch-flow with Shopify target, VI language

## Success Criteria
- CMS adapter swap via env var only (no SKILL.md changes)
- WP adapter regression: identical behavior to Phase 1
- Shopify + Haravan publish blog posts with SEO metadata, media, tags
- Batch-flow processes 50 keywords without crashes
- VI articles score > 75 on seo-scorer with locale rules
- batch_report.md includes per-keyword status + aggregate stats

## Risk Assessment

| Risk | Impact | Mitigation |
|------|--------|------------|
| Shopify GraphQL API complexity | Medium | Start with minimal mutations (blogArticleCreate only); expand later |
| Haravan API documentation gaps | Medium | Haravan is Shopify-compatible; start from Shopify adapter, adjust |
| Batch flow resource consumption | Medium | Sequential execution (not parallel) for v1; rate limit between keywords |
| Vietnamese NLP edge cases | Low | Simple heuristics for v1; document known limitations |
| Adapter interface too rigid | Low | Design minimal interface; adapters can extend with CMS-specific extras |

## Security Considerations
- Per-CMS credentials in separate env vars (SHOPIFY_TOKEN never used for WP calls)
- Adapter validates CMS_TARGET against allowlist [wordpress, shopify, haravan]
- Batch-flow inherits security model of individual skills
- No credentials logged in batch_report.md
- Shopify/Haravan tokens scoped to minimum required permissions (write_content, write_files)

## Next Steps
- Post Phase 4: publish all skills to ClawHub (MIT-0 license)
- Consider: monitoring dashboard skill (track published content performance)
- Consider: seo-link-building skill (outreach automation)
- Consider: scheduled batch-flow (cron-based content calendar execution)

## Unresolved Questions
1. Does Haravan API support all Shopify blog article fields? Need to test with staging store.
2. Batch-flow parallel execution: does ClawFlow support parallel iteration, or only sequential?
3. Should batch-flow support resume-from-failure (checkpoint keywords already processed)?
