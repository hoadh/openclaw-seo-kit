# Gap Analysis Methodology

This document describes the methodology used by `seo-competitor-analyze` to identify content, keyword, and backlink gaps between a target domain and its competitors.

---

## 1. Content Gap Analysis

### Goal
Identify topic clusters that competitors rank for but the target site does not cover.

### Data Sources
- Sitemap XML from target and competitor domains
- Page titles and meta descriptions from crawled pages
- H1/H2 heading text from fetched pages

### Process

1. **Collect page inventory** for target and each competitor via sitemap fetch + `web_fetch`.
2. **Extract topic signals** from each page:
   - Normalize title: lowercase, strip punctuation, tokenize
   - Remove stopwords (the, a, an, in, on, for, etc.)
   - Extract 2-3 word n-grams as topic candidates
3. **Cluster topics** by semantic similarity (word overlap ≥ 40%):
   - Group pages by dominant 2-gram (e.g., "email marketing", "keyword research")
   - Assign each page to its primary topic cluster
4. **Identify gaps**: Topic clusters present in ≥ 1 competitor but absent from target
5. **Prioritize gaps** by:
   - `high`: present in 2+ competitors AND query has SERP results with featured snippet
   - `medium`: present in 1 competitor with clear search volume signals
   - `low`: niche topic with limited SERP presence

### Output
```json
[{"topic": "topic cluster name", "competitor_urls": ["url1"], "priority": "high|medium|low"}]
```

---

## 2. Keyword Gap Analysis

### Goal
Identify keywords that competitors target but the target site does not.

### Data Sources
- Competitor page titles and H1/H2 text (keyword signals)
- SERP data from `seo-serp-scraper` for high-value topics
- Optional: SEMrush/Ahrefs API for volume and difficulty

### Process

1. **Extract keywords** from competitor pages: tokenize titles, headings, meta descriptions
2. **Normalize**: lowercase, stem (strip -ing, -ed, -s suffixes simply)
3. **Filter** target's existing keyword coverage from its own pages
4. **Score** remaining gap keywords by:
   - Frequency across competitor pages (higher = more likely valuable)
   - Presence in SERP titles (indicates ranking signal)
   - Match to commercial/informational intent patterns
5. **Prioritize**:
   - `high`: 3+ competitor pages target this keyword
   - `medium`: 2 competitor pages
   - `low`: 1 competitor page

### Output
```json
[{"keyword": "str", "priority": "high|medium|low", "competitor_count": int}]
```

---

## 3. Backlink Gap Analysis

### Limitations Without Paid Tools
Without SEMrush, Ahrefs, or Moz API access, true backlink data is not available.
The following proxy methods provide limited signal:

- **Citation mentions**: Use `web_search` for `link:competitor.com` (limited results)
- **Brand mentions**: Search for competitor brand name to find linking domains
- **Directory listings**: Check niche directories where competitor appears

### With Paid API (SEMrush)
```
GET https://api.semrush.com/?type=backlinks_overview&target=competitor.com&key={SEMRUSH_API_KEY}
```

### With Paid API (Ahrefs)
```
GET https://apiv2.ahrefs.com/?from=backlinks&target=competitor.com&token={AHREFS_API_KEY}
```

### Manual Analysis Framework (No Paid Tools)

| Signal | How to Find | Value |
|--------|-------------|-------|
| Guest posts | Search `site:competitor.com "guest post"` | Link-building opportunities |
| Resource pages | Search `intitle:resources competitor-topic` | Outreach targets |
| Industry directories | Search `competitor.com site:directory.com` | Listing gaps |
| HARO/PR links | Search competitor brand in news | PR opportunities |

### Output Format (Manual)
```json
{
  "note": "Paid API required for full backlink data",
  "proxy_opportunities": [
    {"type": "resource_page", "domain": "example.com", "url": "..."}
  ]
}
```

---

## Priority Matrix

| Gap Type | High Priority Signal | Action |
|----------|---------------------|--------|
| Content | Featured snippet exists for topic | Create comprehensive guide |
| Keyword | 3+ competitors rank for it | Add to existing page or create new |
| Backlink | Authority site links competitor | Outreach + content matching |
