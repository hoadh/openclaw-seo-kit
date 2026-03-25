# AEO Optimization Guide

Answer Engine Optimization (AEO) adapts content for AI-powered search surfaces
including Google AI Overviews, ChatGPT Browse, Perplexity, and Bing Copilot.

---

## What is AEO?

AEO extends traditional SEO by optimizing content to be cited and quoted by
AI assistants rather than just ranked in blue-link results. AI engines extract
direct answers from pages; poorly structured content gets skipped even if it
ranks well organically.

---

## AI Search Ranking Factors

### 1. Topical Authority
- AI systems prefer sources that comprehensively cover a topic
- Single-page depth beats thin coverage across many pages
- Cite data, studies, and authoritative sources inline
- Keep content updated — AI systems weight freshness for evolving topics

### 2. Citation-Friendly Formatting
- **Direct answers first**: Lead with a 2–3 sentence answer before elaborating
- **Short paragraphs**: 3–5 sentences max per paragraph
- **Active voice**: Easier for AI to parse and extract
- **Concrete specifics**: Numbers, dates, named entities > vague claims
- **Structured sections**: H2/H3 headings that match question patterns

### 3. Structured Answers
- Numbered lists for sequential processes (AI can extract step N directly)
- Bulleted lists for features, comparisons, definitions
- Definition-style openings: "X is a Y that Z"
- FAQ blocks with explicit Question/Answer pairs
- Tables for comparisons AI can cite as-is

---

## Platform-Specific Patterns

### Google AI Overviews
- Prefers content that already appears in featured snippets
- Paragraph answers: 40–60 words, single concept per paragraph
- Lists: 3–8 items, each item < 20 words
- Cite sources inline with dates: "According to [Study], in [Year]..."
- Recency signal: include `dateModified` in JSON-LD

### ChatGPT (Browse / GPT-4o)
- Favors well-structured HTML with clear heading hierarchy
- Tables and code blocks are preserved and cited verbatim
- Author byline and publication date increase trust score
- Avoid heavy JavaScript rendering — static HTML preferred

### Perplexity AI
- Aggressive snippet extraction: first 150 words of each section matter most
- Multi-source synthesis: content that agrees with other top sources cited more
- Question-style H2 headings dramatically increase extraction rate
- Include "TL;DR" or "Summary" section — Perplexity often quotes these

### Bing Copilot / Microsoft AI
- Prefers Bing-indexed pages with strong E-E-A-T signals
- Author schema (Person type with credentials) boosts trust
- Microsoft News-indexed content cited more frequently
- Include breadcrumb schema for context

---

## Traditional SEO vs. AEO

| Factor | Traditional SEO | AEO |
|--------|----------------|-----|
| Goal | Rank in blue links | Get cited/quoted by AI |
| Format | Any readable format | Direct answer blocks required |
| Length | 1,500+ words for authority | Concise per-section answers |
| Keywords | Keyword density/placement | Natural language, question-matching |
| Structured data | Helpful for rich results | Critical for AI extraction |
| Freshness | Important for news | Critical for AI citation |
| Authority | Domain authority / backlinks | E-E-A-T signals, citations, author |

---

## AEO Readiness Checklist

- [ ] TL;DR block at top of article (2–3 sentences)
- [ ] Each H2 section opens with direct 2–3 sentence answer
- [ ] FAQ section with explicit Q&A format
- [ ] `datePublished` and `dateModified` in JSON-LD
- [ ] Author schema with credentials
- [ ] No answer buried past paragraph 3 of any section
- [ ] Lists use 3–8 items with consistent structure
- [ ] Tables for all comparisons
- [ ] Definition-style opening for key concepts
- [ ] Citations to authoritative sources inline
