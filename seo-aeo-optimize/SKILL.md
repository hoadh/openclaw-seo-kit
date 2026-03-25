---
name: seo-aeo-optimize
description: Optimize article for AI search engines (Google AI Overview, ChatGPT, Perplexity) by adding citation-friendly formatting and answer blocks when preparing content for AEO
version: 1.0.0
metadata:
  openclaw:
    anyBins:
      - python3
      - python
---

# SEO AEO Optimize Skill

## Context

You are an Answer Engine Optimization (AEO) specialist. Your goal is to reformat
a markdown article to maximize its probability of being cited by AI search engines
(Google AI Overviews, ChatGPT Browse, Perplexity, Bing Copilot).

Never remove or alter the factual content of the article. Only add structural
improvements — TL;DR blocks, direct answer summaries, and enhanced FAQ formatting.

## References

- `references/aeo-optimization-guide.md` — AEO ranking factors and platform patterns
- `references/citation-patterns.md` — How AI systems select and cite content
- `references/answer-block-templates.md` — Copy-paste templates for each answer type

## Steps

### 1. Read Article

Accept path to `article.md` or receive content via stdin.

Confirm the article:
- Is valid markdown with at least one H1 heading
- Has meaningful content (> 200 words)
- Is the version intended for publication (not a draft)

### 2. Analyze AEO Readiness

Before formatting, evaluate the article against the AEO checklist:

```
[ ] Has TL;DR block after H1
[ ] Each H2 opens with a direct 2-3 sentence answer
[ ] FAQ section uses H3 per question with answer directly below
[ ] datePublished/dateModified in JSON-LD (check if HTML target)
[ ] No critical answer buried past paragraph 3 of any section
[ ] Lists have 3-8 items (not prose-style comma lists)
[ ] Key Takeaways section present
```

Report which checks pass/fail before applying changes.

### 3. Add Answer Blocks Per Section

Run `aeo-formatter.py` to apply all transformations:

```bash
cat article.md | python3 scripts/aeo-formatter.py > aeo_article.md
```

Transformations applied automatically:
- **TL;DR block**: Inserted after H1, extracted from opening paragraph
- **Answer blocks**: `> **In brief:** ...` inserted after each H2 heading
- **FAQ enhancement**: Converts bold questions and Q:/A: patterns to H3 headings
- **Key Takeaways**: Added at end if not already present

### 4. Enhance FAQ Section

If the article has an FAQ section, verify the formatter converted all questions:
- Each question should be an H3 heading
- Answer should appear immediately below (no blank line between H3 and answer)
- Each answer: 1–3 sentences, 20–50 words

If questions were missed, manually add H3 headings per the template in
`references/answer-block-templates.md` section 4.

### 5. Add TL;DR (Verify)

Confirm TL;DR block appears immediately after H1:
- Should be 2–3 sentences
- Should include primary keyword naturally
- Should state the article's key takeaway
- Format: `**TL;DR:** [content]`

If the auto-generated TL;DR is vague, rewrite it manually with the article's
most specific insight.

### 6. Run aeo-formatter.py

```bash
cat article.md | python3 scripts/aeo-formatter.py > aeo_article.md
```

Verify output:
- Word count should be similar to input (± 10%)
- All original headings preserved
- No content removed

### 7. Verify SEO Score Not Degraded

If `seo-scorer` skill is available, run it on both versions:

```
seo-scorer: article.md -> score A
seo-scorer: aeo_article.md -> score B
```

Confirm score B >= score A. AEO formatting should not reduce SEO signals.
If score drops, check that title tag, meta description, and H1 are unchanged.

### 8. Save aeo_article.md

Save the formatted output as `aeo_article.md` in the working directory.

Report:
- AEO readiness score before and after (count of checklist items passed)
- Number of answer blocks added
- Number of FAQ questions restructured
- TL;DR status (added / already present / skipped)
- Word count change

## Output

```
aeo_article.md — AEO-optimized version of the article
```

Plus a summary report:

```
AEO Optimization Summary
- TL;DR: Added
- Answer blocks added: 4
- FAQ questions restructured: 6
- Key Takeaways: Added
- AEO readiness: 7/7 checks passing
- Word count: 1,520 → 1,680 (+10%)
```

## Error Handling

- If article has no H1, add one based on the filename or first bold line
- If article has no H2 sections, report it and recommend restructuring
- If FAQ section has no questions, skip FAQ enhancement step
- If word count increases > 20%, review generated blocks for verbosity
