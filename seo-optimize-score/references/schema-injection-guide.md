# JSON-LD Schema Injection Guide

Structured data helps search engines understand article content. Inject the appropriate JSON-LD template based on article type. Templates below are complete and ready to use — replace placeholder values in `{{ }}`.

---

## How to Inject

Append a fenced `json-ld` block at the end of the markdown article:

````markdown
```json-ld
{
  "@context": "https://schema.org",
  ...
}
```
````

The `seo-publish-cms` skill reads these blocks and injects them as `<script type="application/ld+json">` tags in the WordPress post `<head>`.

Only inject **one** schema type per article. Choose the best match from the options below.

---

## Template 1: Article (General Informational Content)

Use for: blog posts, guides, opinion pieces, news articles.

```json
{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "{{ meta_title }}",
  "description": "{{ meta_description }}",
  "image": "{{ featured_image_url }}",
  "author": {
    "@type": "Person",
    "name": "{{ author_name }}"
  },
  "publisher": {
    "@type": "Organization",
    "name": "{{ site_name }}",
    "logo": {
      "@type": "ImageObject",
      "url": "{{ site_logo_url }}"
    }
  },
  "datePublished": "{{ publish_date_iso8601 }}",
  "dateModified": "{{ modified_date_iso8601 }}",
  "mainEntityOfPage": {
    "@type": "WebPage",
    "@id": "{{ canonical_url }}"
  }
}
```

**Required placeholders:**
- `meta_title` — from frontmatter
- `meta_description` — from frontmatter
- `featured_image_url` — URL of the OG/featured image (from `seo-image-generate` output)
- `author_name` — article author (from frontmatter `author` field or site default)
- `site_name` — website name
- `site_logo_url` — absolute URL to site logo (recommended: 112x112px PNG)
- `publish_date_iso8601` — e.g. `2025-06-15T09:00:00+07:00`
- `modified_date_iso8601` — same format as publish date
- `canonical_url` — full URL of the published page

---

## Template 2: HowTo (Step-by-Step Instructions)

Use for: tutorials, recipe-style guides, installation instructions, any article with numbered steps.

**Detection signals:** Article has a section with numbered list items, headings like "How to", "Step 1", "Steps to".

```json
{
  "@context": "https://schema.org",
  "@type": "HowTo",
  "name": "{{ meta_title }}",
  "description": "{{ meta_description }}",
  "image": "{{ featured_image_url }}",
  "totalTime": "{{ estimated_time_iso8601 }}",
  "estimatedCost": {
    "@type": "MonetaryAmount",
    "currency": "{{ currency_code }}",
    "value": "{{ cost_value }}"
  },
  "supply": [
    {
      "@type": "HowToSupply",
      "name": "{{ supply_item_1 }}"
    }
  ],
  "tool": [
    {
      "@type": "HowToTool",
      "name": "{{ tool_item_1 }}"
    }
  ],
  "step": [
    {
      "@type": "HowToStep",
      "name": "{{ step_1_heading }}",
      "text": "{{ step_1_description }}",
      "image": "{{ step_1_image_url }}",
      "url": "{{ canonical_url }}#step-1"
    },
    {
      "@type": "HowToStep",
      "name": "{{ step_2_heading }}",
      "text": "{{ step_2_description }}",
      "image": "{{ step_2_image_url }}",
      "url": "{{ canonical_url }}#step-2"
    }
  ]
}
```

**Required placeholders:**
- `meta_title`, `meta_description`, `featured_image_url`, `canonical_url` — same as Article
- `estimated_time_iso8601` — ISO 8601 duration e.g. `PT30M` (30 minutes), `PT1H` (1 hour)
- `step_N_heading` — text of each numbered step heading (from H3 or list items)
- `step_N_description` — first sentence or summary of each step

**Optional placeholders** (remove block if not applicable):
- `estimatedCost` — omit if article is not about a process with a cost
- `supply` / `tool` — omit if article doesn't reference materials or tools
- `step_N_image_url` — section image URL from `seo-image-generate` output

**Populating steps automatically:**
Extract steps from the article by finding:
1. Numbered list items directly under an H2 (each item = one step)
2. H3 headings under a "Steps" or "How to" H2 (each H3 = one step)

---

## Template 3: FAQPage (Frequently Asked Questions)

Use for: articles with a dedicated FAQ section, Q&A format content, articles answering multiple user questions.

**Detection signals:** Article has an H2 or H3 heading containing "FAQ", "Frequently Asked", "Questions", or a section with alternating bold questions and paragraph answers.

```json
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "{{ question_1 }}",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "{{ answer_1 }}"
      }
    },
    {
      "@type": "Question",
      "name": "{{ question_2 }}",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "{{ answer_2 }}"
      }
    },
    {
      "@type": "Question",
      "name": "{{ question_3 }}",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "{{ answer_3 }}"
      }
    }
  ]
}
```

**Required placeholders:**
- `question_N` — the question text (from H3 heading or bold text in FAQ section)
- `answer_N` — the answer text (paragraph following the question, plain text only — no markdown)

**Rules for FAQ schema:**
- Include 3–10 question/answer pairs; Google displays up to 3 in rich results
- `answer` text must be plain text — strip markdown formatting before injecting
- Maximum answer length: 300 words (Google truncates longer answers in SERPs)
- Questions must match exactly what appears in the article content

**Populating FAQ pairs automatically:**
Parse the FAQ section of the article by finding:
1. H3 headings within an H2 section named "FAQ" or "Frequently Asked Questions" (H3 = question, following paragraph = answer)
2. Bold text patterns: `**Question text?**` followed by a paragraph (bold = question, paragraph = answer)

---

## Choosing the Right Schema

```
Article has numbered steps or "How to" sections?
  → Use HowTo

Article has a FAQ section with 3+ Q&A pairs?
  → Use FAQPage

Neither of the above?
  → Use Article (default)
```

If the article qualifies for both HowTo and FAQPage (e.g., a how-to guide with an FAQ at the end), choose **HowTo** as the primary schema — it typically yields richer SERP features.

---

## Validation

After injecting schema, validate at:
- Google Rich Results Test: https://search.google.com/test/rich-results
- Schema.org Validator: https://validator.schema.org/
