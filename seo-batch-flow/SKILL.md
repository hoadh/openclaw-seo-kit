---
name: seo-batch-flow
description: "Batch process keyword list through full SEO content pipeline for agency-scale content production when given a keyword list file"
metadata:
  openclaw:
    requires:
      env:
        - CMS_TARGET
      primaryEnv: CMS_TARGET
      anyBins:
        - python3
        - python
---

# seo-batch-flow

## Context

You are a batch content production coordinator. Your job is to take a list of keywords and run each one through the complete SEO content pipeline (seo-content-flow), collecting results into a structured batch report. A single keyword failure must never halt the batch — log the error and continue.

## Input

A keyword list provided as either:
- A file path: `keyword_list.txt` — one keyword per line
- stdin: pipe keywords one per line

**Example `keyword_list.txt`:**
```
content marketing strategy
seo for beginners
tối ưu hóa trang web
best wordpress plugins 2024
```

Empty lines are ignored. Duplicate keywords (case-insensitive) are skipped after the first occurrence.

## Environment Variables

Inherits all env vars from seo-content-flow and seo-cms-adapter:

| Variable | Description |
|---|---|
| `CMS_TARGET` | Target CMS: `wordpress` \| `shopify` \| `haravan` |
| `WORDPRESS_URL` / `WORDPRESS_TOKEN` | If CMS_TARGET=wordpress |
| `SHOPIFY_STORE_URL` / `SHOPIFY_ACCESS_TOKEN` / `SHOPIFY_BLOG_ID` | If shopify |
| `HARAVAN_STORE_URL` / `HARAVAN_ACCESS_TOKEN` / `HARAVAN_BLOG_ID` | If haravan |
| `OPENAI_API_KEY` | Required by seo-content-flow for content generation |

## Steps

1. **Read keyword_list.txt**
   - Accept file path as argument or read from stdin
   - Strip empty lines and whitespace
   - Report count of raw keywords found

2. **Validate and deduplicate**
   - Skip blank lines silently
   - Detect duplicates (case-insensitive): keep first occurrence, log skipped count
   - Report: "X unique keywords, Y duplicates skipped"

3. **For each keyword invoke seo-content-flow**
   - Run the full pipeline: research → outline → write → score → optimize → publish
   - Track start and end time for each keyword
   - Capture: `seo_score`, `url` (draft post URL), `status`
   - On failure: log error message, set status=failed, continue to next keyword
   - Progress indicator to stderr: `[N/total] Processing: {keyword}`

4. **Collect results**
   - Accumulate per-keyword result dicts:
     ```json
     {
       "keyword":      "content marketing strategy",
       "status":       "success",
       "seo_score":    82,
       "url":          "https://example.com/?p=42",
       "time_seconds": 45.3,
       "error":        null
     }
     ```

5. **Generate batch_report.md**
   - Use template from `references/batch-report-template.md`
   - Fill summary: total, success, failed, skipped duplicates, avg time
   - Fill results table: one row per keyword
   - List failed keywords separately with error messages
   - Save as `batch_report.md` in the current working directory

6. **Report summary to user**
   - Print the JSON report to stdout (for programmatic use)
   - Print human-readable summary to stderr:
     ```
     Batch complete.
     Keywords: 10 total | 8 success | 2 failed | 1 duplicate skipped
     Total time: 7m 23s | Avg per keyword: 44s

     Failed keywords (retry individually):
       - "tối ưu hóa trang web": seo-content-flow runner not found
       - "best wordpress plugins 2024": API timeout

     Report saved: batch_report.md
     ```

## Running the Batch

```bash
# From file
python3 scripts/batch-runner.py keyword_list.txt

# From stdin
cat keyword_list.txt | python3 scripts/batch-runner.py

# Capture JSON report
python3 scripts/batch-runner.py keyword_list.txt > batch_report.json
```

## Error Handling

| Error | Behavior |
|---|---|
| Keyword file not found | Exit immediately with clear message |
| Empty keyword list | Output empty report, exit 0 |
| Single keyword fails | Log error, mark status=failed, continue batch |
| seo-content-flow runner missing | Mark all keywords as failed with explanation |
| CMS auth failure | Mark keyword as failed; include auth hint in error |
| Timeout (>300s per keyword) | Mark as failed: "timeout after 300s" |

## Output Files

| File | Description |
|---|---|
| stdout | Full JSON batch report |
| `batch_report.md` | Human-readable markdown report (saved to CWD) |
| stderr | Progress log and final summary |

## References

- `references/batch-report-template.md` — Markdown report template
- `../seo-content-flow/SKILL.md` — Single-keyword pipeline this batch orchestrates
- `../seo-cms-adapter/SKILL.md` — CMS adapter used for publishing each article
