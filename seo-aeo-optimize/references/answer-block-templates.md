# Answer Block Templates

Copy-paste templates for structuring content to maximize AI engine citation.
Replace `[TOPIC]`, `[ANSWER]`, etc. with actual content.

---

## 1. TL;DR Block (Top of Article)

Place immediately after the H1 heading, before the introduction.

```markdown
**TL;DR:** [2–3 sentence direct answer covering the main point of the article.
Include the primary keyword naturally. State the key takeaway a reader gets
from reading this article.]
```

**Example:**
```markdown
**TL;DR:** Email marketing delivers an average ROI of $36 for every $1 spent,
making it the highest-ROI digital channel for most businesses. The key is
segmentation — targeted campaigns outperform batch-and-blast emails by 760%
in revenue. This guide covers the exact setup, tools, and strategies to get there.
```

---

## 2. "What is X" Definition Block

Place at the start of any section introducing a new concept.

```markdown
## What is [TOPIC]?

[TOPIC] is [CATEGORY] that [DOES/PROVIDES/ENABLES] [BENEFIT/FUNCTION].
[One sentence of additional context]. [One sentence on why it matters].

[Elaboration paragraph with examples, nuance, or history]
```

**Example:**
```markdown
## What is Anchor Text?

Anchor text is the clickable, visible text in a hyperlink that tells both users
and search engines what the linked page is about. Search engines use anchor text
as a relevance signal for the destination page. Optimized anchor text can
significantly improve ranking for the linked page's target keyword.

Anchor text appears blue and underlined by default in most browsers...
```

---

## 3. "How to X" Process Block

Use numbered lists. Each step must be self-contained and actionable.

```markdown
## How to [ACCOMPLISH TASK]

To [accomplish task], follow these [N] steps:

1. **[Step Name]**: [One sentence action description]. [Optional: expected outcome].
2. **[Step Name]**: [One sentence action description]. [Optional: expected outcome].
3. **[Step Name]**: [One sentence action description]. [Optional: expected outcome].

[Optional: brief summary sentence after the list]
```

**Example:**
```markdown
## How to Set Up Google Search Console

To set up Google Search Console, follow these 4 steps:

1. **Create a property**: Go to search.google.com/search-console and click
   "Add property", then enter your website URL.
2. **Verify ownership**: Download the HTML verification file and upload it
   to your website's root directory.
3. **Submit your sitemap**: Navigate to Sitemaps, enter your sitemap URL
   (usually `/sitemap.xml`), and click Submit.
4. **Wait for data**: Initial data appears within 24–48 hours; full data
   populates within 2–3 weeks.
```

---

## 4. FAQ Enhancement Block

Wrap each question in its own heading with a direct answer immediately below.

```markdown
## Frequently Asked Questions

### [Question ending with ?]

[Direct answer in 1–3 sentences. No preamble. No "Great question!"]

### [Question ending with ?]

[Direct answer in 1–3 sentences.]
```

**Example:**
```markdown
## Frequently Asked Questions

### How long does SEO take to show results?

SEO typically takes 3–6 months to show measurable results for new content,
and 6–12 months for competitive keywords. Technical fixes like canonicalization
and site speed improvements can show results within 2–4 weeks.

### Is SEO better than paid ads?

SEO has a higher long-term ROI than paid ads because organic traffic continues
after you stop investing. Paid ads stop delivering traffic the moment you pause
spending. Most businesses benefit from combining both channels.
```

---

## 5. Comparison Table Block

Use for any X vs. Y or feature comparison content.

```markdown
## [Topic A] vs. [Topic B]

| Feature | [Topic A] | [Topic B] |
|---------|-----------|-----------|
| [Feature 1] | [Value A] | [Value B] |
| [Feature 2] | [Value A] | [Value B] |
| [Feature 3] | [Value A] | [Value B] |
| Best for | [Use case A] | [Use case B] |
| Price | [Price A] | [Price B] |

**Bottom line:** [1–2 sentence summary of when to choose each option.]
```

---

## 6. Key Takeaways Block (End of Article)

Place before or after the conclusion to aid AI extraction of summary content.

```markdown
## Key Takeaways

- [Most important point from the article — include primary keyword]
- [Second most important point — specific, actionable]
- [Third point — include data or statistic if possible]
- [Fourth point — practical next step for the reader]
```

---

## Insertion Rules for aeo-formatter.py

The formatter applies these templates automatically:

| Template | Trigger | Insertion Point |
|----------|---------|-----------------|
| TL;DR | Always | After H1, before first paragraph |
| Answer block | Each H2 | First paragraph after H2 heading |
| FAQ enhancement | Heading containing "FAQ" or "Question" | Restructure Q&A pairs under sub-headings |
| Key Takeaways | Always (if not present) | Before last heading or end of document |
