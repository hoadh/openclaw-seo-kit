# Code Review: OpenClaw SEO Skills Suite

**Date:** 2026-03-25
**Reviewer:** code-reviewer
**Scope:** 15 directories (12 skills + 3 ClawFlow workflows), 23 Python scripts, 5 JSON schemas, ~5,100 LOC Python

---

## Summary

**Overall Quality Score: 8/10**
**Critical Issues: 1**
**High Priority: 5**
**Medium Priority: 7**

Strong, well-architected skill suite. All 23 Python scripts compile cleanly. Stdlib-only constraint respected everywhere. SKILL.md files are well-structured with numbered steps, error handling tables, and clear I/O contracts. Cross-skill pipeline contracts are coherent. Main concerns: several scripts exceed 200-line limit, one security issue with shell=True, and some duplicated frontmatter parsing code.

---

## Per-Skill Findings

### 1. seo-keyword-research
**SKILL.md:** Excellent. Clear 7-step flow, env vars declared, error handling table, schema referenced.
**keyword-analyzer.py (313 lines):** Over 200-line limit. Clean TF-IDF implementation.
- Medium: Consider splitting clustering/intent logic into separate module
- Low: `extract_questions` splits on `[.!]` but misses `?` as sentence terminator; questions embedded mid-sentence could be missed

### 2. seo-outline-generate
**SKILL.md:** Well structured. Schema type selection table is clear.
**outline-validator.py (249 lines):** Over limit. Good validation coverage.
- Medium: `import re` inside `validate_slug()` (line 184) — should be at module top level. Works but non-idiomatic.
- Low: Missing `language` field validation (schema has it as optional, validator does not check it)

### 3. seo-content-write
**SKILL.md:** Good. Writing guidelines and multilingual rules properly referenced.
**content-formatter.py (272 lines):** Over limit. Custom YAML parser is brittle but acceptable for stdlib-only.
- Medium: `parse_frontmatter()` does not handle YAML arrays (e.g., `categories: [1, 2]`). Only handles `key: value` and block scalars.
- Low: `_density_status()` uses `keywords.index(kw)` which is O(n) per call but list is small

### 4. seo-scorer
**SKILL.md:** Good. Missing `version` field in frontmatter (has `name` and `metadata` but no `version`). Clear scoring rubric.
**seo-score-calculator.py (245 lines):** Over limit. Sibling import via importlib is correct pattern.
**seo-scoring-dimensions.py (285 lines):** Over limit. Well-structured dimension functions.
- High: `score_heading_structure()` uses `re.findall(r'^# (.+)$', body, re.MULTILINE)` which also matches `## ` and `### ` prefixed lines because `#` followed by space matches. **Wait -- checked: `^# (.+)$` requires exactly one `#` then space. This is correct because `##` starts with `##` not `# `.** False alarm. Actually correct.
- Medium: `readability` scoring returns `"method": "none"` when no sentences/words found, but schema enum only allows `flesch-kincaid-en` or `sentence-length-vi`. Output violates schema in edge case.

### 5. seo-optimize-score
**SKILL.md:** Well structured. Step 5 duplicates Step 3d content (redundant). Steps 6 and 7 also overlap. Could be cleaner.
**internal-link-suggester.py (370 lines):** **Largest file.** Significantly over 200-line limit.
- High: Should be split into modules: frontmatter parsing, sitemap fetching, keyword matching, main logic.
- Medium: Duplicates `parse_frontmatter()` from seo-score-calculator.py verbatim. DRY violation.

### 6. seo-publish-cms
**SKILL.md:** Good. Env vars table complete. Error handling table clear. Notes about never logging tokens is good security practice.
**media-uploader.py (164 lines):** Clean. Under limit.
**wp-publisher.py (131 lines):** Clean. Adapter integration works correctly.
- Medium: SKILL.md still references WordPress-specific steps (step 4: "Upload images to WordPress") despite now supporting Shopify/Haravan via adapter. Steps 4-6 should be generalized.

### 7. seo-serp-scraper
**SKILL.md:** Adequate. Step 5 rate-limiter example references `web_search_wrapper.sh` which does not exist in the repo.
**serp-parser.py (186 lines):** Clean. Under limit. Good type classification mapping.
**rate-limiter.py (134 lines):** Clean. TokenBucket is well implemented.
- **CRITICAL (Security): `rate-limiter.py` line 54 uses `shell=True` in `subprocess.run()`.** The `--command` argument is passed directly to shell. If user-controlled input reaches `--command`, this is a command injection vector. The `input_data` is piped via stdin (safe), but the command string itself is shell-interpreted.
  - **Fix:** Use `shlex.split(command)` and `shell=False`, or document that `--command` must be hardcoded by the skill, never user-supplied.
- Low: `serp-parser.py` output `query` field defaults to empty string `''` when input is array — schema marks `query` as required.

### 8. seo-technical-audit
**SKILL.md:** Excellent. 7-module scoring table, clear data flow.
**site-crawler.py (231 lines):** Over limit. HTML parser is well done.
**structured-data-checker.py (189 lines):** Clean. Good schema validation coverage.
**robots-sitemap-checker.py (243 lines):** Over limit. Thorough robots.txt parsing.
- Medium: `site-crawler.py` PageHTMLParser accesses `self._in_heading` via `hasattr()` check (lines 128, 138) — attribute should be initialized in `__init__`. Works but fragile pattern.

### 9. seo-image-generate
**SKILL.md:** Good. Dimensions table, troubleshooting, integration notes.
**image-prompt-builder.py (273 lines):** Over limit. Duplicates `parse_frontmatter()` again.
**alt-text-generator.py (199 lines):** Just under limit. Clean alt text generation logic.
- Medium: `image-prompt-builder.py` duplicates frontmatter parsing (3rd copy).

### 10. seo-competitor-analyze
**SKILL.md:** Good. Clear methodology, SERP enrichment step.
**content-gap-finder.py (211 lines):** Slightly over limit. `cluster_topics()` is O(n^2) — fine for typical input sizes (<500 topics).
**keyword-gap-analyzer.py (178 lines):** Clean. Under limit.
- Low: `stem()` is extremely naive — only strips English suffixes. Vietnamese keywords pass through unchanged. Acceptable for gap detection.

### 11. seo-aeo-optimize
**SKILL.md:** Good. Steps 3 and 6 are duplicated (both say "Run aeo-formatter.py"). Confusing.
**aeo-formatter.py (238 lines):** Over limit.
- Medium: `enhance_faq_section()` checks `plain_q` with `stripped[0].isupper()` — fails on Vietnamese characters that start with diacritical marks (e.g., `Nh` is uppercase but `nh` would also pass). Minor edge case.

### 12. seo-cms-adapter
**SKILL.md:** Excellent. Platform differences table, usage pattern, error handling.
**adapter-interface.py (166 lines):** Clean ABC. Good factory pattern.
**wp-adapter.py (207 lines):** Over limit. Clean REST API implementation.
**shopify-adapter.py (209 lines):** Over limit. Media upload via theme assets is correct approach.
**haravan-adapter.py (213 lines):** Over limit. Near-identical to shopify-adapter.py.
- High: **shopify-adapter.py and haravan-adapter.py are ~90% identical.** Both duplicate `_request()`, `authenticate()`, `create_post()`, `get_sitemap()`, `get_post_url()`, and `set_tags()`. Only differences: auth header name, API URL pattern, and class name. Should extract shared `ShopifyCompatibleAdapter` base class.
- Medium: `shopify-adapter.py` line 129 has `import base64` inside method body. Should be top-level.

### 13. seo-content-flow (ClawFlow)
**SKILL.md:** Excellent. 289 lines. Best-documented skill. ClawFlow YAML definition, step-by-step I/O contracts, quality gate, approval flow, comprehensive troubleshooting.
- High: `LANG` env var conflicts with system locale `LANG`. Using `LANG=vi` will also change Python's locale behavior (e.g., `locale.getdefaultlocale()`). Recommend renaming to `CONTENT_LANG` or `SEO_LANG`.
- Low: Step I/O contract mentions `target_word_count` and `competitor_urls` as key output fields of research step, but `keyword-analyzer.py` output schema does not include these fields.

### 14. seo-audit-flow (ClawFlow)
**SKILL.md:** Good. Flow diagram is helpful. Parallel execution correctly documented.
- Medium: `aeo-check` step receives `tech-audit.output` as input, but `seo-aeo-optimize` expects a markdown article, not an audit report JSON. **Input type mismatch.** The SKILL.md prose (Phase 2b) explains it operates on "top-performing pages" from the audit, but the ClawFlow YAML pipes the raw audit output directly.

### 15. seo-batch-flow (ClawFlow)
**SKILL.md:** Good. Error handling table covers all scenarios.
**batch-runner.py (237 lines):** Over limit. Well-structured with clean separation.
- High: `_invoke_content_flow()` looks for `scripts/content-flow-runner.py` which does not exist anywhere in the repo. This means every keyword will always fail with "seo-content-flow runner not found; manual execution required". The batch runner is effectively a stub.
- Medium: `OPENAI_API_KEY` listed in env vars table but not actually used by any script. Misleading.

---

## Cross-Cutting Concerns

### A. Duplicated Frontmatter Parser (DRY Violation)
`parse_frontmatter()` is independently implemented in **5 scripts**:
1. `seo-content-write/scripts/content-formatter.py`
2. `seo-scorer/scripts/seo-score-calculator.py`
3. `seo-optimize-score/scripts/internal-link-suggester.py`
4. `seo-image-generate/scripts/image-prompt-builder.py`
5. `seo-aeo-optimize/scripts/aeo-formatter.py` (different approach, splits sections)

Each implementation has slightly different capabilities (some handle arrays, some don't). Should extract to a shared `seo-shared-utils/` module.

### B. File Size Violations
13 of 23 scripts exceed the 200-line project limit:
| Script | Lines |
|--------|-------|
| internal-link-suggester.py | 370 |
| keyword-analyzer.py | 313 |
| seo-scoring-dimensions.py | 285 |
| image-prompt-builder.py | 273 |
| content-formatter.py | 272 |
| outline-validator.py | 249 |
| seo-score-calculator.py | 245 |
| robots-sitemap-checker.py | 243 |
| aeo-formatter.py | 238 |
| batch-runner.py | 237 |
| site-crawler.py | 231 |
| haravan-adapter.py | 213 |
| content-gap-finder.py | 211 |

### C. Exit Code Consistency
Most scripts follow the documented convention (0=success, 1=validation, 2=input error). `aeo-formatter.py` and `content-formatter.py` only use exit code 1 for all errors. Minor inconsistency.

### D. Cross-Skill I/O Chain Verification

| Chain | Status | Notes |
|-------|--------|-------|
| keyword-research -> outline-generate | **OK** | keyword_map.json schema matches outline reader expectations |
| outline-generate -> content-write | **OK** | outline.json fields align with content-write input parsing |
| content-write -> publish-cms | **OK** | article.md with frontmatter -> wp-publisher.py JSON input |
| content-write -> scorer | **OK** | article.md frontmatter fields match scorer requirements |
| scorer -> optimize-score | **OK** | score_report.json schema matches optimize-score reader |
| CMS adapter interface -> publish-cms | **OK** | wp-publisher.py correctly imports and uses adapter factory |
| content-flow pipeline | **Partial** | `target_word_count` and `competitor_urls` in I/O contract but not in keyword_map schema |
| audit-flow -> aeo-optimize | **Mismatch** | Audit output (JSON) piped to AEO optimizer that expects markdown |
| batch-flow -> content-flow | **Broken** | Missing `content-flow-runner.py` script |

### E. Security

- **CRITICAL:** `rate-limiter.py` uses `shell=True` for subprocess execution. Command injection risk if `--command` value is ever derived from user input.
- **Good:** Credentials never logged in output. `WORDPRESS_TOKEN` handling is security-conscious. Base64 encoding happens at runtime only.
- **Good:** No hardcoded URLs or credentials anywhere.
- **Good:** File path validation present in media-uploader.py and other file-reading scripts.

---

## Schema Consistency

| Schema | Script Output | Status |
|--------|--------------|--------|
| keyword-map-schema.json | keyword-analyzer.py | **Match** |
| outline-schema.json | outline-validator.py checks | **Match** |
| score-report-schema.json | seo-score-calculator.py | **Near match** — `readability.method` can output `"none"` which is not in schema enum |
| serp-results-schema.json | serp-parser.py | **Near match** — `parsed_at` field in output but not in all schema versions |
| image-map-schema.json | image-prompt-builder.py | **Match** — prompt builder outputs prompts; image_map.json is assembled by the LLM caller |

---

## Reference Doc Quality

Checked all `references/` directories. Docs are actionable with specific rules, not filler:
- `scoring-rubric.md`, `optimization-rules.md`: Point-by-point scoring criteria
- `search-intent-guide.md`: Clear classification rules
- `writing-guidelines.md`, `multilingual-rules.md`: Specific density targets and language rules
- `schema-markup-guide.md`: Schema type selection matrix
- `aeo-optimization-guide.md`, `citation-patterns.md`, `answer-block-templates.md`: Concrete AEO patterns
- `cwv-proxy-signals.md`: Proxy metrics without Lighthouse
- `batch-report-template.md`: Markdown template ready to fill

---

## Recommendations (Priority Ordered)

### 1. [CRITICAL] Fix shell=True in rate-limiter.py
Replace `shell=True` with `shlex.split(command)` + `shell=False`. Or add prominent doc warning that `--command` must never contain user input.

### 2. [HIGH] Extract shared frontmatter parser
Create `seo-shared-utils/frontmatter.py` with canonical `parse_frontmatter()`. Import via importlib (same pattern as adapter-interface). Eliminates 5 independent implementations.

### 3. [HIGH] Extract ShopifyCompatibleAdapter base class
Shopify and Haravan adapters share ~90% code. Extract `ShopifyCompatibleAdapter(CMSAdapter)` with configurable auth header, API URL pattern, and store URL env var names. Both concrete adapters become ~30 lines each.

### 4. [HIGH] Rename LANG to CONTENT_LANG
`LANG` clashes with POSIX locale. Rename to `CONTENT_LANG` or `SEO_LANG` in seo-content-flow and seo-content-write.

### 5. [HIGH] Fix audit-flow AEO input mismatch
`seo-aeo-optimize` expects markdown articles, not audit JSON. Either:
- Add preprocessing in audit-flow to extract top pages as individual markdown inputs
- Or document that aeo-check step requires the LLM to fetch and convert pages first

### 6. [HIGH] Implement or stub content-flow-runner.py
`batch-runner.py` references `seo-content-flow/scripts/content-flow-runner.py` which does not exist. Either create it or update batch-runner to invoke skills via a different mechanism.

### 7. [MEDIUM] Split scripts exceeding 200 lines
Priority targets (most over limit): `internal-link-suggester.py` (370), `keyword-analyzer.py` (313), `seo-scoring-dimensions.py` (285).

### 8. [MEDIUM] Fix seo-optimize-score SKILL.md duplicate steps
Steps 3d/5 and 6/7 are redundant. Consolidate.

### 9. [MEDIUM] Fix seo-aeo-optimize SKILL.md duplicate steps
Steps 3 and 6 both describe running aeo-formatter.py. Consolidate.

### 10. [MEDIUM] Fix readability schema violation
`seo-scoring-dimensions.py` can return `"method": "none"` — add to schema or default to a valid value.

### 11. [MEDIUM] Update seo-publish-cms SKILL.md for multi-CMS
Steps 4-6 still reference WordPress-specific operations. Generalize to "Upload images to CMS" etc.

### 12. [MEDIUM] Fix content-flow I/O contract
Remove `target_word_count` and `competitor_urls` from Step 1 output description, or add them to keyword_map schema.

### 13. [LOW] Initialize `_in_heading` in site-crawler.py PageHTMLParser.__init__
### 14. [LOW] Move inline `import re` and `import base64` to module top level
### 15. [LOW] Remove phantom `OPENAI_API_KEY` from batch-flow env vars table

---

## Positive Observations

- **Stdlib-only discipline:** Zero pip dependencies across all 23 scripts
- **Consistent error handling:** All scripts validate stdin/file input, handle JSON parse errors, use appropriate exit codes
- **Clean adapter pattern:** CMS adapter abstraction is well-designed with proper ABC
- **Security awareness:** Token logging prevention, draft-only publishing, auth error messages guide users without exposing secrets
- **Comprehensive SKILL.md files:** Error handling tables, I/O contracts, troubleshooting sections in every skill
- **Bilingual support:** Vietnamese language handling in scorer, content-write, and keyword-research
- **Schema validation:** JSON schemas exist for all major data exchange formats
- **All scripts compile cleanly** on Python 3.13

---

## Metrics

- **Type Coverage:** N/A (Python, no type checker configured; type hints used in some but not all scripts)
- **Test Coverage:** 0% — no test files found
- **Linting Issues:** ~15 medium (inline imports, duplicate code, file size)
- **Compilation:** 23/23 pass

---

## Unresolved Questions

1. Is `content-flow-runner.py` intentionally missing, or was it planned but not yet implemented?
2. Should the audit-flow's aeo-check step actually invoke seo-aeo-optimize per-page, or is it meant to be a read-only AEO assessment?
3. Is the `OPENAI_API_KEY` in batch-flow env vars a remnant from an earlier design, or is it needed by a component not yet visible?
4. Are there plans to add unit tests for the Python scripts?
