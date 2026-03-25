---
name: seo-serp-scraper
description: Scrape and parse search engine results pages extracting organic results, PAA boxes, featured snippets, and related searches for SEO analysis
version: 1.0.0
metadata:
  openclaw:
    anyBins:
      - python3
      - python
---

# SEO SERP Scraper Skill

## Context

You are an SEO data analyst. Your goal is to collect and parse SERP data for a given query, producing a structured `serp_results.json` for consumption by downstream skills (keyword gap analysis, competitor analysis, AEO optimization).

Always rate-limit web fetches to avoid overloading servers. Never fabricate result data.

## References

- `references/serp-results-schema.json` — JSON Schema the output must conform to
- `references/serp-feature-types.md` — Rules for identifying and extracting each SERP feature type

## Steps

### 1. Accept Query Input

- Confirm a search query was provided by the caller.
- Normalize: trim whitespace, lowercase if appropriate.
- If empty or missing, exit with error: `"Error: search query is required"`.

### 2. Web Search — Collect SERP Data

Run `web_search` for the query. Collect all result objects containing:
- `title` — page title
- `snippet` — description text
- `url` — result URL
- `type` — result type if available (organic, featured, video, paa, etc.)

Gather 10–20 results for comprehensive analysis.

### 3. Web Fetch — Enrich Snippets

For the top 5 organic results, run `web_fetch` to retrieve page content.
Use `rate-limiter.py` with `--rate 1` to enforce 1 request/second:

```bash
echo '["url1","url2","url3"]' | python3 scripts/rate-limiter.py \
  --rate 1 \
  --command "python3 -c \"import sys; print(sys.stdin.read())\""
```

Extract additional snippet text from page `<meta name="description">` if the search result snippet is truncated.

### 4. Parse Results with serp-parser.py

Pipe the collected results array to `serp-parser.py`:

```bash
echo '<json_array_of_results>' | python3 scripts/serp-parser.py
```

The parser will:
- Classify each result by type (organic, featured, video, local, image, knowledge_panel)
- Detect and separate PAA questions (titles ending in "?")
- Extract featured snippet (position 0 or explicit type)
- Collect related searches
- Return structured JSON matching `serp-results-schema.json`

### 5. Rate Limit Between Fetches

When fetching multiple pages, use `rate-limiter.py` with `--rate 1` (default):

```bash
echo '["query1","query2","query3"]' | python3 scripts/rate-limiter.py \
  --rate 1 \
  --command "web_search_wrapper.sh"
```

Adjust `--rate` down (e.g., `--rate 0.5`) for conservative crawling of sensitive domains.

### 6. Output serp_results.json

Save the final parsed output as `serp_results.json` in the working directory:

```bash
echo '<results_json>' | python3 scripts/serp-parser.py > serp_results.json
```

Confirm the file was written and report summary:
- Total organic results count
- Whether featured snippet was found
- Number of PAA questions
- Number of related searches

## Output Format

```json
{
  "query": "target keyword",
  "results": [
    {"position": 1, "url": "https://...", "title": "...", "snippet": "...", "type": "organic", "domain": "..."}
  ],
  "paa": [
    {"question": "What is ...?", "snippet": "...", "url": "..."}
  ],
  "related_searches": ["related query 1", "related query 2"],
  "featured_snippet": {"text": "...", "url": "...", "title": "...", "format": "paragraph"},
  "meta": {
    "total_results": 10,
    "has_featured_snippet": true,
    "has_paa": true,
    "has_video_carousel": false,
    "has_local_pack": false
  }
}
```

## Error Handling

- If `web_search` returns no results, report: `"No results found for query"`
- If `serp-parser.py` fails, check that input is valid JSON array
- If rate limiter times out a command, retry once then skip
