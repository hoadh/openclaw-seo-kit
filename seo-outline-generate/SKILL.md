---
name: seo-outline-generate
description: Generate SEO-optimized article outline with heading hierarchy, meta tags, and schema markup suggestion from keyword research data
version: 1.0.0
metadata:
  openclaw:
    requires:
      env: []
      anyBins:
        - python3
        - python
---

# SEO Outline Generate Skill

## Context

You are an SEO content strategist. Your goal is to produce a structured `outline.json` for a given `keyword_map.json` produced by `seo-keyword-research`. The outline drives article writing in `seo-content-write` and must be fully validated before saving.

This is a pure LLM skill — no external APIs are required. Quality depends entirely on how well you apply the keyword map to the outline structure.

## References

- `references/outline-schema.json` — JSON Schema the output must conform to
- `references/schema-markup-guide.md` — Rules for selecting Article, HowTo, FAQ, or Product schema type

## Steps

### 1. Read keyword_map.json

Load `keyword_map.json` from the current working directory or from the path provided by the caller.

Extract these fields for use in subsequent steps:
- `primary_keyword` — the seed keyword, will appear in H1, meta title, slug, and intro
- `search_intent` — drives schema type selection and content tone
- `lsi_keywords` — distribute across H2/H3 target_keywords
- `long_tail` — source for FAQ questions and subsection headings
- `clusters` — map to H2 sections (one cluster = one H2 section)
- `language` — determines tone and writing style in `seo-content-write`

If `keyword_map.json` cannot be loaded or is missing required fields, exit with:
`"Error: valid keyword_map.json is required. Run seo-keyword-research first."`

### 2. Analyze Search Intent and Select Schema Type

Use `references/schema-markup-guide.md` to select `schema_type`:

| search_intent | Default schema_type |
|---------------|-------------------|
| informational (no "how to" signals) | Article |
| informational (how/steps signals) | HowTo |
| informational (FAQ/question heavy) | FAQ |
| commercial | Article |
| transactional | Product |
| navigational | Article |

Override to `FAQ` if `long_tail` contains 5+ question strings (ending in `?`).
Override to `HowTo` if `primary_keyword` starts with "how to".

### 3. Generate H2/H3 Heading Structure

Map keyword clusters to H2 sections. Each cluster becomes one H2. For clusters with 3+ keywords, create H3 subsections within that H2.

Rules:
- H1 is the article title — do not include it as a section
- Every H2 must have at least 1 entry in `target_keywords` drawn from that cluster's keywords and relevant LSI terms
- Create 4–7 H2 sections for adequate coverage (adjust based on cluster count)
- Add subsections (H3) where the topic warrants deeper breakdown
- Always include: Introduction (implicit, not a section), Conclusion (final H2)
- Write `notes` for each subsection describing key points, data, or examples to include
- Use the `language` field to determine heading phrasing style (formal VI vs conversational EN)

### 4. Write Meta Title and Meta Description

**meta_title** rules:
- Must be under 60 characters
- Include `primary_keyword` near the start
- Convey value/benefit
- Do not end with brand name (unless brand is the keyword)

**meta_description** rules:
- Must be under 160 characters
- Include `primary_keyword` naturally
- Include a call-to-action or value statement
- Do not duplicate meta_title wording

**title** (H1):
- Slightly longer than meta_title is acceptable
- Make it compelling and keyword-rich
- Can include power words (complete, ultimate, proven, step-by-step)

**slug** rules:
- Lowercase, hyphens only
- Derived from `primary_keyword` — replace spaces with hyphens, remove special chars
- Keep under 60 characters

### 5. Generate FAQ from Long-Tail Keywords

From the `long_tail` array, select questions (strings ending in `?`) as FAQ items.
- Minimum: 3 FAQ items
- Maximum: 8 FAQ items
- For each question, write a concise `answer_hint` (1–2 sentences) describing what the answer should cover
- If fewer than 3 questions exist in `long_tail`, generate sensible questions from the non-question long-tail phrases

### 6. Validate with outline-validator.py

Run the validator script on the generated outline:

```bash
echo '<outline_json>' | python3 scripts/outline-validator.py
```

If the validator exits with code 1, parse the error list and fix all reported issues:
- Truncate `meta_title` or `meta_description` if over limit
- Fix heading levels (H2 = 2, H3 = 3)
- Add missing `target_keywords` to empty sections
- Fix slug format

Re-run validator after fixes. If still failing after one correction pass, exit with the error JSON.

### 7. Save Output

Write the validated outline to `outline.json` in the current working directory (or caller-specified path).

Report:
- Output path: `./outline.json`
- Title
- Schema type selected
- Number of H2 sections
- Total subsections
- FAQ item count
- meta_title length
- meta_description length

## Error Handling

| Situation | Action |
|-----------|--------|
| keyword_map.json missing | Exit with error, instruct to run seo-keyword-research |
| keyword_map.json missing required fields | Exit with field list |
| No clusters in keyword_map | Generate sections from lsi_keywords directly |
| meta_title over 60 chars | Truncate and warn |
| meta_description over 160 chars | Truncate and warn |
| validator exits 1 after fixes | Exit with validator error JSON |
| Output path not writable | Exit with error listing path |

## Output

```
outline.json written to: ./outline.json
title: <value>
schema_type: <value>
H2 sections: <count>
subsections: <count>
FAQ items: <count>
meta_title: <length>/60 chars
meta_description: <length>/160 chars
```
