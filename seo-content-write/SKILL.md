---
name: seo-content-write
description: Write full SEO article from outline with natural keyword placement, proper heading structure, and multilingual support (Vietnamese/English)
version: 1.0.0
metadata:
  openclaw:
    requires:
      env: []
      anyBins:
        - python3
        - python
---

# SEO Content Write Skill

## Context

You are an expert SEO content writer. Your goal is to produce a full, publish-ready article in Markdown format based on `outline.json` and `keyword_map.json`. The article must meet keyword density targets, readability standards, and heading structure requirements defined in the references.

This is a pure LLM skill — no external APIs required. Quality depends on disciplined adherence to the outline structure and writing guidelines.

## References

- `references/writing-guidelines.md` — Keyword density targets, readability standards, word count, placement rules, internal linking
- `references/multilingual-rules.md` — Language-specific tone, loan word policy, sentence length, formatting

## Steps

### 1. Read outline.json

Load `outline.json` from the current working directory or caller-specified path. Extract:

- `title` → H1 of the article
- `meta_title`, `meta_description`, `slug` → YAML frontmatter
- `schema_type` → determines FAQ/HowTo structural requirements
- `sections[]` → H2/H3 structure with `target_keywords` and `notes`
- `faq[]` → FAQ questions and answer hints
- `language` → writing language (`en` or `vi`)

Also load `keyword_map.json` to access:
- `primary_keyword` → must appear in H1, first 100 words, conclusion
- `lsi_keywords` → secondary terms to distribute naturally
- `search_intent` → informs tone and angle

If either file is missing, exit with:
`"Error: outline.json and keyword_map.json are required. Run seo-keyword-research and seo-outline-generate first."`

### 2. Determine Language and Apply Rules

Read `language` from `outline.json` (fallback: `keyword_map.json`, then default `en`).

Load the corresponding rules from `references/multilingual-rules.md`:
- `en`: conversational tone, active voice, Grade 8–10 readability, contractions allowed
- `vi`: formal tone, < 25 words per sentence avg, prefer Vietnamese over loan words, no contractions

Apply these rules throughout all writing steps below.

### 3. Write Introduction (First 100 Words)

The introduction must:
- Open with a compelling hook (question, surprising stat, or bold statement)
- Include `primary_keyword` **within the first 100 words** — ideally within the first 50
- Briefly state what the article covers (2–3 sentences)
- Signal the search intent (informational: "In this guide…", commercial: "We compared…", transactional: "Here's how to get…")
- Length: 120–180 words total for the intro section

Do NOT use "In this article, I will…" as the first sentence — it is weak. Lead with value.

### 4. Write Each Section per H2/H3 Structure

For each entry in `sections[]`:

**H2 sections:**
- Write the H2 heading exactly as specified in the outline
- Open with a transitional sentence that flows from the previous section
- Naturally incorporate `target_keywords` for this section — do not front-load them
- Length guideline: 250–400 words per H2 section (including its H3 subsections)

**H3 subsections:**
- Write the H3 heading exactly as specified
- Follow the `notes` field: cover the key points, data, or examples listed
- Length: 80–180 words per H3 subsection

**Keyword placement discipline:**
- Check `target_keywords` for each section and use them at least once, naturally
- Distribute `lsi_keywords` across sections — do not cluster all LSI terms in one section
- If a keyword feels forced, use a semantic variant instead

**HowTo schema_type additional rule:**
Sections that describe steps must number them explicitly:
```
**Step 1: [Action]**
[Instruction text]
```

### 5. Write FAQ Section

Use the `faq[]` array from the outline. Format as:

```markdown
## Frequently Asked Questions

### [question text]
[Full answer — 2–4 sentences. Follow the answer_hint from the outline.]

### [next question]
[Answer]
```

Rules:
- Answer each question fully in 2–4 sentences
- Do not reference the article itself ("As mentioned above…")
- Each answer must be self-contained for FAQPage schema extraction
- For `vi`: maintain formal tone in questions and answers

If `schema_type` is `FAQ`, this section is the primary content type and must be prominent and thorough.

### 6. Write Conclusion with CTA

The conclusion must:
- Summarize the article's key value in 2–3 sentences
- Include `primary_keyword` at least once
- End with a clear, specific call-to-action (CTA)

CTA examples by intent:
- Informational: "Start applying these techniques today and track your rankings over the next 30 days."
- Commercial: "Compare your top options using our criteria above and choose the tool that fits your workflow."
- Transactional: "Sign up for a free trial and see results within your first campaign."

Length: 100–150 words.

### 7. Run content-formatter.py

Pipe the complete article markdown through the formatter:

```bash
echo '<article_markdown>' | python3 scripts/content-formatter.py \
  --keywords "{primary_keyword},{top_lsi_1},{top_lsi_2}" \
  --slug "{slug}" \
  --title "{title}" \
  --lang "${CONTENT_LANG:-en}"
```

The formatter will:
- Inject or update YAML frontmatter (title, meta_title, meta_description, slug, date, language, draft)
- Report keyword density stats to stderr — review them
- Output the formatted article to stdout

**If density is under-optimized** (primary < 1%): add 3–5 natural occurrences in body text, re-run.
**If density is over-optimized** (primary > 2.5%): replace some occurrences with semantic variants, re-run.

### 8. Save Output

Write the formatter output to `article.md` in the current working directory (or caller-specified path).

Report:
- Output path: `./article.md`
- Word count (approximate)
- Primary keyword density
- Language
- Schema type
- Section count

## Error Handling

| Situation | Action |
|-----------|--------|
| outline.json missing | Exit with error, instruct to run seo-outline-generate |
| keyword_map.json missing | Exit with error, instruct to run seo-keyword-research |
| language not en or vi | Default to en, warn |
| content-formatter.py exits non-zero | Show stderr, fix frontmatter manually and retry |
| Density over 2.5% after fix | Warn but proceed — do not sacrifice readability |
| Density under 1% after fix | Add targeted placements in intro and conclusion |

## Output

```
article.md written to: ./article.md
word_count: ~<N> words
primary_keyword_density: <X>%
language: <en|vi>
schema_type: <value>
sections: <count> H2 sections
```
