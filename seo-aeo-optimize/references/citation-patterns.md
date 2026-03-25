# Citation Patterns for AI Search Engines

This document describes how AI assistants select and cite web content,
and how to format content to maximize citation frequency.

---

## How AI Assistants Select Sources to Cite

### Selection Criteria (Approximate Priority)

1. **Relevance**: Content directly answers the query intent
2. **Extraction ease**: Short, self-contained answer blocks < 100 words
3. **Authority signals**: Domain trust, author credentials, backlinks
4. **Freshness**: Recently published or updated content preferred
5. **Consistency**: Content that agrees with majority of top sources
6. **Format clarity**: Structured HTML without heavy JS rendering

### What Gets Skipped
- Answers buried in paragraph 4+ of a section
- Content requiring JavaScript to render
- Paywalled or login-gated content
- Duplicate / thin content pages
- Pages with aggressive interstitials or popups

---

## Optimal Answer Length by Type

| Answer Type | Optimal Length | Notes |
|-------------|---------------|-------|
| Definition ("What is X") | 2–3 sentences, 30–50 words | Open with "X is a Y that Z" |
| Process ("How to X") | 3–8 numbered steps, 10–20 words each | Number every step explicitly |
| Comparison ("X vs Y") | Table or 2-column structure | Keep rows < 15 words |
| List ("Best X for Y") | 3–8 items with 1-line description each | Avoid comma-separated prose lists |
| FAQ answer | 1–3 sentences, 20–40 words per answer | Directly under the question heading |

---

## Authority Signals AI Systems Recognize

### Schema.org Signals
```json
{
  "@type": "Article",
  "author": {
    "@type": "Person",
    "name": "Author Name",
    "jobTitle": "SEO Specialist",
    "url": "https://example.com/author/name"
  },
  "datePublished": "2024-01-15",
  "dateModified": "2024-11-20",
  "publisher": {
    "@type": "Organization",
    "name": "Publisher Name"
  }
}
```

### HTML Signals
- `<time datetime="2024-01-15">January 15, 2024</time>` — explicit date markup
- `<address>` tag for author/contact information
- `<cite>` tag wrapping source references
- `<blockquote cite="url">` for external citations

### Content Signals
- "According to [Source], [Year]..." — inline attribution
- "[Statistic] (Source: [Authority], Year)" — data citation format
- "Researchers at [Institution] found..." — authority attribution
- "As of [Month Year]..." — freshness marker

---

## Perplexity-Specific Citation Optimization

Perplexity extracts from the **first 150 words of each section**.

Structure every H2 section as:
```
## [Section Heading]

[Direct answer in 2–3 sentences. Include the key fact/number/definition here.]

[Elaboration paragraph — additional context, nuance, examples.]

[Optional: List or table if the topic has multiple components]
```

The first paragraph is the citation target. Never put the answer second.

---

## ChatGPT Browse Citation Patterns

ChatGPT Browse reads pages as structured documents. It favors:

1. **First paragraph of article**: Often quoted verbatim in responses
2. **Numbered lists**: Reproduced step-by-step in answers
3. **Definition blocks**: "X is defined as..." sentences
4. **Code blocks**: Reproduced exactly for technical queries
5. **Tables**: Column headers and rows preserved in AI output

To maximize ChatGPT citations, ensure your first 200 words contain the core answer.

---

## Google AI Overview Citation Patterns

Google AI Overviews synthesize from multiple sources. Content is cited when:

- It matches the featured snippet exactly (highest priority)
- The snippet is ≤ 60 words and directly addresses the query
- The page has high organic ranking (positions 1–5)
- The content format matches query type:
  - How-to query → numbered list preferred
  - Definition query → paragraph preferred
  - Comparison query → table preferred
  - Best-of query → bulleted list preferred

---

## Source Attribution Best Practices

When writing content that AI will cite, use these attribution patterns:

**Inline citation (preferred):**
> "Studies show X increases Y by 30% (Harvard Business Review, 2023)."

**End-of-claim citation:**
> "The average conversion rate is 3.2%. [Source: WordStream, 2024]"

**Blockquote with cite:**
```html
<blockquote cite="https://source.com/study">
  "Direct quote from authoritative source."
</blockquote>
<cite>Source Name (Year)</cite>
```

These formats help AI systems attribute and trust the content they extract.
