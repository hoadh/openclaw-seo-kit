---
name: seo-keyword-research
description: Research SEO keywords with search intent analysis, LSI discovery, and clustering when given a keyword or topic
version: 1.0.0
metadata:
  openclaw:
    requires:
      env:
        - name: SEMRUSH_API_KEY
          required: false
          description: SEMrush API key for volume and difficulty data. If absent, skill falls back to web_search only.
      anyBins:
        - python3
        - python
---

# SEO Keyword Research Skill

## Context

You are an SEO keyword researcher. Your goal is to produce a comprehensive `keyword_map.json` for a given seed keyword or topic. The map will be consumed by `seo-outline-generate` to build a content outline.

Always prioritize data quality over speed. If SEMrush data is unavailable, web search results are sufficient. Never fabricate keyword data.

## References

- `references/keyword-map-schema.json` — JSON Schema the output must conform to
- `references/search-intent-guide.md` — Rules for classifying informational / commercial / transactional / navigational intent

## Steps

### 1. Validate Input Keyword

- Confirm a seed keyword or topic was provided by the caller.
- Normalize: trim whitespace, lowercase.
- If empty or missing, exit with error: `"Error: seed keyword is required"`.
- Detect language hint from the keyword (Latin script → `en`, Vietnamese diacritics → `vi`). This sets the `language` field.

### 2. Web Search — Primary Keyword Variations

Run `web_search` for the following queries (replace `{kw}` with the seed keyword):

- `{kw}` — baseline SERP
- `{kw} guide`
- `{kw} tips`
- `{kw} how to`

Collect all result objects containing `title`, `snippet`, and `url`. Aggregate into a single JSON array.

### 3. Web Search — PAA and Related Queries

Run additional `web_search` queries to capture People Also Ask and related questions:

- `{kw} what is`
- `{kw} vs`
- `{kw} best`
- `related:{kw}` (if the search engine supports it)

Append results to the aggregated array. Total results should be 20–60 objects for good coverage.

### 4. Optional — SEMrush API Enrichment

If `SEMRUSH_API_KEY` is set in the environment:

```
GET https://api.semrush.com/?type=phrase_related&key={SEMRUSH_API_KEY}&phrase={kw}&database=us&display_limit=20
```

Parse the CSV response. Extract keyword phrases and append as additional result objects with `title` = keyword, `snippet` = "", `url` = "".

If the API call fails (network error, 401, 403, quota exceeded), log a warning to stderr and continue without SEMrush data. Do not abort the skill.

### 5. Run keyword-analyzer.py

Pipe the aggregated JSON array to the analyzer script:

```bash
echo '<aggregated_json>' | python3 scripts/keyword-analyzer.py --keyword "{kw}" --lang {detected_lang}
```

Capture stdout as the raw `keyword_map` JSON. Capture stderr for warnings.

If the script exits non-zero, inspect stderr and retry once with a reduced result set (remove malformed entries). If still failing, exit with the error message.

### 6. Validate Output Against Schema

Load `references/keyword-map-schema.json` and validate the script output:

- All required fields present: `primary_keyword`, `search_intent`, `lsi_keywords`, `long_tail`, `clusters`, `volume_estimate`, `language`
- `search_intent` is one of: `informational`, `commercial`, `transactional`, `navigational`
- `volume_estimate` is one of: `low`, `medium`, `high`
- `language` is one of: `en`, `vi`
- `lsi_keywords` and `long_tail` are non-empty arrays

If validation fails, log the errors and attempt a minimal repair (fill missing arrays with `[]`, default `search_intent` to `"informational"`).

### 7. Save Output

Write the validated `keyword_map` JSON to `keyword_map.json` in the current working directory (or the path specified by the caller).

Report:
- Output path: `./keyword_map.json`
- Primary keyword detected
- Search intent classified as
- LSI keyword count
- Long-tail count
- Cluster count
- Volume estimate
- Language

## Error Handling

| Situation | Action |
|-----------|--------|
| No seed keyword provided | Exit with error |
| web_search returns 0 results | Warn and try broader query (remove modifiers) |
| SEMrush API unavailable | Skip, continue with web search data only |
| keyword-analyzer.py exits non-zero | Retry once with cleaned input, then exit with error |
| Schema validation fails | Attempt repair, warn about fields that were defaulted |
| Output path not writable | Exit with error listing the path |

## Output

```
keyword_map.json written to: ./keyword_map.json
primary_keyword: <value>
search_intent: <value>
lsi_keywords: <count> terms
long_tail: <count> phrases/questions
clusters: <count> groups
volume_estimate: <value>
language: <value>
```
