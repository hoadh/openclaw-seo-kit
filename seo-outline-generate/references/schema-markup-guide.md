# Schema.org Markup Type Selection Guide

Schema markup (structured data) helps search engines understand content type and enables rich results in SERPs. Use this guide to select the correct `schema_type` for the article outline.

---

## Supported Types

### Article

**Use when:** General blog posts, news, editorial content, evergreen guides that don't fit a more specific type.

**Selection criteria:**
- Content informs or educates without step-by-step instructions
- No dominant Q&A structure
- Not primarily a product review or pricing page
- Search intent is **informational** or **commercial** (comparison/opinion)

**Rich result eligibility:** Article rich result (headline, image, date) in Google News and Discover.

**Examples:**
- "What is content marketing"
- "The history of SEO"
- "10 benefits of meditation"
- "Why Python is popular"

**Schema properties to populate:** `headline`, `author`, `datePublished`, `dateModified`, `image`, `publisher`

---

### HowTo

**Use when:** Content describes a sequential process the reader follows to accomplish a task.

**Selection criteria:**
- Article has numbered steps (Step 1, Step 2…)
- Each step has a clear action
- Reader performs the task themselves (tutorial, DIY, recipe-like)
- Search intent is **informational** with "how to" signal words

**Rich result eligibility:** HowTo rich result showing steps directly in SERP — high CTR benefit.

**Examples:**
- "How to set up Google Analytics 4"
- "How to bake sourdough bread"
- "How to fix a leaking faucet"
- "How to write a cover letter"

**Schema properties to populate:** `name`, `description`, `step[]` (name + text per step), optional `supply[]`, `tool[]`, `totalTime`

---

### FAQ

**Use when:** Content is structured primarily as questions and answers, or has a substantial FAQ section as the main content.

**Selection criteria:**
- Article answers 3+ distinct questions
- Each question has a self-contained answer
- Search intent is **informational** with "what", "how", "why" signals
- Long-tail questions dominate the keyword map

**Rich result eligibility:** FAQ rich result expands answers directly under the search result — increases SERP real estate significantly.

**Examples:**
- "FAQ: Everything about intermittent fasting"
- "Common questions about visa applications"
- "WordPress FAQ for beginners"

**Schema properties to populate:** `mainEntity[]` array of `Question` (name) + `Answer` (text) pairs

---

### Product

**Use when:** Content reviews, compares, or describes a specific product or service, including pricing or rating information.

**Selection criteria:**
- Article focuses on one or more commercial products/services
- Includes or implies price, rating, or availability
- Search intent is **commercial** (review/compare) or **transactional**
- Primary keyword includes product name, "review", "price", "buy"

**Rich result eligibility:** Product rich result showing price, availability, rating stars in SERP.

**Examples:**
- "Ahrefs review 2024"
- "Best standing desks under $500"
- "iPhone 15 Pro vs Samsung S24"
- "Shopify pricing plans explained"

**Schema properties to populate:** `name`, `description`, `brand`, `offers` (price, currency, availability), `aggregateRating` (if reviews present)

---

## Decision Matrix

| Search Intent | Dominant Signal Words | Recommended Schema |
|---------------|----------------------|--------------------|
| Informational | what, why, history, benefits | Article |
| Informational | how to, steps, guide, tutorial | HowTo |
| Informational | questions, FAQ, common, answers | FAQ |
| Commercial | review, compare, best, vs | Article or Product |
| Transactional | buy, price, cost, order | Product |
| Navigational | brand name, login, site | Article (minimal schema value) |

---

## Combining Schema Types

Only one `schema_type` is stored in the outline, but you can nest types in the final article:

- An **Article** can contain a `FAQPage` block at the bottom
- A **HowTo** can contain a `FAQPage` in its supplemental section
- A **Product** page can include `Review` and `AggregateRating` sub-schemas

When the outline has both procedural steps AND FAQs, pick whichever dominates the content structure. Record the secondary type in a section note.
