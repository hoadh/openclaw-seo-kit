---
name: seo-scorer
description: "Score SEO quality of any article measuring keyword density, readability, heading structure, internal links, and meta tags on a 0-100 scale"
metadata:
  openclaw:
    type: skill
    requires:
      anyBins:
        - python3
        - python
---

# seo-scorer

## Overview

Scores a markdown article across 5 SEO dimensions and produces a JSON report. Articles scoring below 70 are flagged for optimization. Use before publishing or after writing to identify gaps.

**Total: 100 points**

| Dimension | Max pts |
|---|---|
| Keyword Density | 20 |
| Readability | 25 |
| Heading Structure | 20 |
| Internal Links | 15 |
| Meta Quality | 20 |

---

## Requirements

- Article must be a markdown file (`.md`) with YAML frontmatter
- Required frontmatter fields:
  - `primary_keyword` — the target keyword to optimize for
  - `meta_title` — SEO page title
  - `meta_description` — SEO meta description
- Optional frontmatter fields:
  - `secondary_keywords` — list of supporting keywords
  - `language` — `en` (default) or `vi`

**Example frontmatter:**

```yaml
---
primary_keyword: "running shoes for beginners"
secondary_keywords: [beginner running gear, best running shoes]
meta_title: "Best Running Shoes for Beginners in 2025"
meta_description: "Discover the top running shoes for beginners with our expert guide covering fit, cushioning, and budget options for new runners."
language: en
---
```

---

## Steps

### Step 1 — Read the target article

Read the article markdown file to confirm it exists and has YAML frontmatter with the required fields (`primary_keyword`, `meta_title`, `meta_description`).

If any required field is missing, warn the user and proceed — the affected dimension will score 0.

### Step 2 — Run seo-score-calculator.py

```bash
python3 seo-scorer/scripts/seo-score-calculator.py <path/to/article.md>
```

The script outputs a JSON score report to stdout. Capture it:

```bash
python3 seo-scorer/scripts/seo-score-calculator.py article.md > score_report.json
```

### Step 3 — Output score_report.json

Present the score report to the user. Summarize as:

```
Overall SEO Score: 85/100

Breakdown:
  Keyword Density:  18/20
  Readability:      22/25
  Heading Structure: 20/20
  Internal Links:    10/15
  Meta Quality:      15/20

Suggestions:
  - Add 2 more internal links (have 1, target 3)
  - Shorten meta_title to 50-60 chars (currently 63)
```

### Step 4 — Flag low-scoring articles

If `overall_score < 70`, display a prominent warning:

```
WARNING: SEO score is 65/100 — below the 70-point publishing threshold.
Run seo-optimize-score to improve before publishing.
```

If score >= 70, confirm the article is ready or note dimensions that could still be improved.

---

## Scoring Details

See `references/scoring-rubric.md` for full point breakdowns per dimension.

### Keyword Density (20 pts)
- Primary keyword target: 1–2% of total words
- Secondary keywords target: 0.5–1% each

### Readability (25 pts)
- **English:** Flesch-Kincaid Grade Level target 8–10
- **Vietnamese:** Average sentence length target 15–20 words/sentence

### Heading Structure (20 pts)
- Exactly one H1, at least 2 H2s, at least one H3
- Primary keyword must appear in H1 or an H2

### Internal Links (15 pts)
- Target = `round(word_count / 300)` internal (relative) links
- Only `[text](/relative-path)` links count; external http links excluded

### Meta Quality (20 pts)
- `meta_title`: 50–60 characters, contains primary keyword
- `meta_description`: 120–160 characters, contains primary keyword

---

## Output Schema

The full JSON schema for `score_report.json` is in `references/score-report-schema.json`.

```json
{
  "overall_score": 85,
  "word_count": 1240,
  "language": "en",
  "breakdown": {
    "keyword_density": {"score": 18, "details": "Primary 'running shoes': 1.6%", "primary_density": 1.6, "primary_count": 20},
    "readability": {"score": 22, "grade_level": 9.2, "target": "8-10", "method": "flesch-kincaid-en"},
    "heading_structure": {"score": 20, "h1_count": 1, "h2_count": 4, "h3_count": 2, "issues": []},
    "internal_links": {"score": 10, "count": 1, "recommended": 3, "total_links": 4},
    "meta_quality": {"score": 15, "title_length": 63, "desc_length": 145, "keyword_in_title": true, "keyword_in_desc": true}
  },
  "suggestions": ["Add 2 more internal links", "Shorten meta_title to 50-60 chars"]
}
```

---

## Troubleshooting

**Script exits with "file not found":**
- Pass the absolute or correct relative path to the markdown file

**All scores are 0 or very low:**
- Confirm the file has valid YAML frontmatter delimited by `---`
- Check that `primary_keyword` is set in frontmatter

**Readability score seems wrong for Vietnamese:**
- Set `language: vi` in frontmatter; default is English (Flesch-Kincaid)

**Internal links score is 0 despite having links:**
- The script counts only relative (internal) links — links starting with `http` are treated as external
- Use relative paths like `/blog/related-post` for internal links
