# SEO Optimization Rules

Rules applied per dimension when `seo-optimize-score` runs. Each rule triggers only when the dimension score falls below its threshold.

---

## 1. Readability — score < 18/25

**Trigger:** Flesch-Kincaid grade > 12 (EN) or avg sentence length > 25 words (VI).

**Agent action (rewrite):**
- Split sentences longer than 25 words at natural conjunction points (and, but, because, which, that)
- Replace multi-syllable words with simpler synonyms where meaning is preserved
- Break dense paragraphs (> 5 sentences) into two shorter paragraphs
- Target grade level 8–10 for EN; 15–20 words/sentence for VI

**Heuristic for finding problem paragraphs:**
1. Split body into paragraphs (blank-line separated)
2. Score each paragraph's avg sentence length
3. Flag paragraphs with avg > 22 words/sentence
4. Present flagged paragraphs to agent for rewrite

**Do not rewrite:** code blocks, blockquotes, lists, table content.

---

## 2. Keyword Density — score < 14/20

**Trigger:** Primary keyword density < 0.5% or > 3%.

### Density too low (< 0.5%)

Suggest insertion points where the primary keyword can be added naturally:
- Introduction paragraph (first 100 words)
- Conclusion paragraph (last 100 words)
- Any H2 subheading that describes the core topic
- First sentence of body paragraphs that introduce a new concept

Agent inserts keyword naturally — never keyword-stuff. Prefer variations:
- Exact match: `running shoes for beginners`
- Natural variation: `shoes for beginning runners`, `beginner running footwear`

### Density too high (> 3%)

Identify the most repetitive paragraphs and suggest pronoun or synonym replacements:
- Replace repeated exact-match keyword with `it`, `they`, `these`, or a synonym
- Do not remove keywords from headings or the intro/conclusion

---

## 3. Internal Links — score < 12/15

**Trigger:** Internal link count < recommended (`word_count / 300`).

**Action:** Run `internal-link-suggester.py` to find candidate pages.

```bash
python3 seo-optimize-score/scripts/internal-link-suggester.py \
  <article.md> \
  <sitemap_url_or_json_file>
```

Output is a JSON array of link suggestions. For each suggestion:
1. Find the suggested `context` string in the article body
2. Replace the `anchor_text` portion with a markdown link: `[anchor_text](target_url)`
3. Inject only as many links as needed to reach the recommended count
4. Prefer links near the top of the article for crawl priority

If no sitemap is available, skip this step and add a manual note for the user.

---

## 4. Schema Markup — missing structured data

**Trigger:** No `<script type="application/ld+json">` block in article or associated HTML template.

**Action:** Inject appropriate JSON-LD schema based on article type:

| Article contains | Schema type to inject |
|---|---|
| Step-by-step instructions, numbered lists | `HowTo` |
| Q&A sections, FAQ heading | `FAQPage` |
| General informational article | `Article` |

Templates are in `references/schema-injection-guide.md`.

**Injection location in markdown:** Append a fenced code block at the end of the article:

````markdown
```json-ld
{ ...schema object... }
```
````

The CMS publish step (`seo-publish-cms`) reads `json-ld` fenced blocks and injects them as `<script>` tags in the WordPress post head.

---

## 5. Heading Structure — score < 15/20

**Trigger:** Missing H1, fewer than 2 H2s, no H3s, or keyword absent from headings.

**Agent action:**
- If no H1: promote the first H2 to H1, or generate one from `meta_title`
- If fewer than 2 H2s: suggest splitting the longest body section into two H2 sections
- If no H3s: suggest adding sub-points under the longest H2 section
- If keyword missing from headings: rephrase the H1 or primary H2 to naturally include it

---

## 6. Meta Quality — score < 15/20

**Trigger:** Title or description outside target length, or keyword missing.

**Agent action (rewrite meta fields in frontmatter):**
- `meta_title` too short: expand with year, modifier (Best, Guide, How to), or location
- `meta_title` too long: remove filler words (the, a, an, for, in, of)
- `meta_description` too short: add a benefit statement or call-to-action
- `meta_description` too long: trim adverbs, redundant phrases
- Keyword missing: insert naturally near the start of the field

---

## Optimization Order

Apply fixes in this sequence to avoid conflicts:

1. Meta quality (frontmatter only — no body changes)
2. Heading structure (structural changes affect word count)
3. Keyword density (after structure is stable)
4. Internal links (after body text is finalized)
5. Readability (last — rewriting can affect keyword density)
6. Schema markup (append-only — no body edits)

After all fixes, re-run `seo-scorer` to confirm score >= 80.
