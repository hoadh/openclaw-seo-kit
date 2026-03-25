# Backlink Analysis Guide

This guide explains how to analyze competitor backlinks for SEO gap opportunities,
both with and without paid tools.

---

## With Paid APIs

### SEMrush

Requires `SEMRUSH_API_KEY` environment variable.

**Endpoint — Backlinks Overview:**
```
GET https://api.semrush.com/
  ?type=backlinks_overview
  &target=competitor.com
  &target_type=root_domain
  &key={SEMRUSH_API_KEY}
```

**Endpoint — Referring Domains:**
```
GET https://api.semrush.com/
  ?type=backlinks_refdomains
  &target=competitor.com
  &target_type=root_domain
  &display_limit=100
  &key={SEMRUSH_API_KEY}
```

**Parse response fields:**
- `source_url` — linking page URL
- `source_title` — anchor text
- `source_size` — domain authority proxy
- `external_num` — number of outbound links (lower = more valuable)

### Ahrefs

Requires `AHREFS_API_KEY` environment variable.

**Endpoint — Backlinks:**
```
GET https://apiv2.ahrefs.com/
  ?from=backlinks
  &target=competitor.com
  &mode=domain
  &limit=100
  &token={AHREFS_API_KEY}
```

**Parse response fields:**
- `url_from` — linking page
- `anchor` — anchor text used
- `domain_rating` — Ahrefs DR score
- `ahrefs_rank` — domain rank

---

## Without Paid Tools (Proxy Methods)

### Method 1: Google Search Operators

Use `web_search` with these operators to find linking pages:

| Operator | Purpose | Example |
|----------|---------|---------|
| `link:competitor.com` | Find known backlinks (limited) | `link:ahrefs.com` |
| `"competitor.com"` | Find mentions and citations | `"semrush.com" SEO tool review` |
| `intitle:resources "competitor topic"` | Find resource pages | `intitle:resources "keyword research"` |
| `site:edu "competitor brand"` | Find educational citations | `site:edu "moz.com"` |

### Method 2: Content-Based Link Prospecting

1. Identify competitor's top-linked content types via SERP analysis:
   - Free tools / calculators
   - Comprehensive guides / ultimate guides
   - Original research / studies
   - Infographics / visual content

2. For each content type, search: `[topic] [type] site:competitor.com`

3. Collect URLs of high-performing content that attracts links

4. Find sites linking to that content via: `"competitor.com/page-slug"` search

### Method 3: Brand Mention Analysis

Search for competitor brand mentions that may include links:
```
web_search: '"competitor brand" site:industry-directory.com'
web_search: '"competitor brand" review 2024'
web_search: '"competitor brand" vs [your brand]'
```

---

## Manual Backlink Gap Report Format

When paid APIs are unavailable, structure findings as:

```json
{
  "method": "proxy_analysis",
  "competitor": "competitor.com",
  "opportunities": [
    {
      "type": "resource_page",
      "prospect_url": "https://blog.example.com/seo-resources",
      "rationale": "Links to 3 competitor tools, not to target",
      "priority": "high",
      "action": "Reach out with content offer"
    },
    {
      "type": "guest_post",
      "prospect_url": "https://industry-site.com/write-for-us",
      "rationale": "Competitor has guest post here",
      "priority": "medium",
      "action": "Submit pitch to editor"
    }
  ],
  "note": "Full backlink data requires SEMrush or Ahrefs API key"
}
```

---

## Link Quality Assessment Criteria

Score each link opportunity 1–5:

| Criterion | Weight | Notes |
|-----------|--------|-------|
| Domain relevance | 30% | Same niche = higher value |
| Estimated authority | 25% | Alexa rank proxy, site age |
| Anchor text opportunity | 20% | Can include target keyword |
| Link placement | 15% | Editorial > sidebar > footer |
| Acquisition difficulty | 10% | Guest post = harder than directory |

**Score 4–5:** Priority outreach target
**Score 2–3:** Include in secondary list
**Score 1:** Skip unless very easy to acquire
