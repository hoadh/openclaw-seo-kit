# SEO Scoring Rubric

Total: 100 points across 5 dimensions.

---

## 1. Keyword Density (20 pts)

Measures how well the article uses primary and secondary keywords.

| Condition | Points |
|---|---|
| Primary keyword density 1–2% | 20 |
| Primary keyword density 0.5–1% or 2–3% | 14 |
| Primary keyword density < 0.5% or > 3% | 6 |

Secondary keyword bonus (applied proportionally up to full 20 pts):
- Each secondary keyword at 0.5–1% density adds up to 3 pts (capped at total dimension max)

**Density formula:** `(keyword_occurrences / total_words) * 100`

---

## 2. Readability (25 pts)

### English (language: en)

Uses Flesch-Kincaid Grade Level approximation:

```
FK Grade = 0.39 * (words/sentences) + 11.8 * (syllables/words) - 15.59
```

Syllable counting heuristic (per word):
- Count vowel groups (a, e, i, o, u sequences)
- Minimum 1 syllable per word
- Subtract 1 for silent 'e' at end of word (if > 1 syllable)

| Grade Level | Points |
|---|---|
| 8–10 (target zone) | 25 |
| 7–8 or 10–12 | 18 |
| 6–7 or 12–14 | 10 |
| < 6 or > 14 | 4 |

### Vietnamese (language: vi)

Uses average sentence length heuristic (Vietnamese lacks reliable syllable counting):

| Avg words/sentence | Points |
|---|---|
| 15–20 (target zone) | 25 |
| 12–15 or 20–25 | 18 |
| 10–12 or 25–30 | 10 |
| < 10 or > 30 | 4 |

---

## 3. Heading Structure (20 pts)

| Criterion | Points |
|---|---|
| H1 present (exactly one `# ` heading) | 8 |
| At least 2 H2 headings (`## `) | 6 |
| At least one H3 heading (`### `) | 3 |
| Primary keyword appears in H1 or at least one H2 | 3 |

Maximum: 20 pts

Issues to flag:
- Multiple H1 headings
- H3 with no parent H2
- No keywords in any heading

---

## 4. Internal Links (15 pts)

Counts Markdown link patterns: `[anchor text](url)`

Target link count = `round(word_count / 300)` (minimum 1)

| Actual vs Target | Points |
|---|---|
| >= target | 15 |
| target - 1 | 12 |
| target - 2 | 8 |
| target - 3 | 4 |
| < target - 3 or 0 links | 0 |

External links (containing `http`) are counted separately but do not contribute to the internal link score.

---

## 5. Meta Quality (20 pts)

Sourced from YAML frontmatter fields: `meta_title`, `meta_description`, `primary_keyword`.

| Criterion | Points |
|---|---|
| `meta_title` length 50–60 chars | 6 |
| `meta_title` length 40–50 or 60–70 chars | 3 |
| `meta_description` length 120–160 chars | 6 |
| `meta_description` length 100–120 or 160–180 chars | 3 |
| `primary_keyword` appears in `meta_title` | 4 |
| `primary_keyword` appears in `meta_description` | 4 |

Maximum: 20 pts

---

## Scoring Thresholds

| Overall Score | Quality Label |
|---|---|
| 90–100 | Excellent |
| 80–89 | Good |
| 70–79 | Acceptable |
| 60–69 | Needs Work |
| < 60 | Poor |

Articles scoring below 70 should be flagged for optimization before publishing.
