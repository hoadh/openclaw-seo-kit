# Technical SEO Audit Scoring Rubric

Total: 100 points across 7 modules. Each module is scored independently.

---

## Module 1: Technical Foundation (20 pts)

Assesses basic crawlability and URL hygiene.

| Check | Points | Pass Condition |
|-------|--------|----------------|
| All sampled pages return 200 OK | 6 | < 5% non-200 status codes |
| No redirect chains > 2 hops | 4 | All redirects resolve in ≤ 2 hops |
| Canonical tags present and self-referencing | 5 | ≥ 80% of pages have canonical |
| No duplicate content (title uniqueness) | 5 | ≥ 90% unique page titles |

**Scoring:**
- 18–20: Excellent foundation
- 14–17: Minor issues, fix soon
- 8–13: Moderate technical debt
- 0–7: Critical issues blocking crawl

---

## Module 2: Search Accessibility (15 pts)

Assesses whether search engines can discover and index content.

| Check | Points | Pass Condition |
|-------|--------|----------------|
| robots.txt present and valid | 4 | File returns 200, valid syntax |
| robots.txt doesn't block important paths | 3 | /css/, /js/, images not disallowed |
| XML sitemap present and linked | 4 | Sitemap referenced in robots.txt |
| Sitemap has correct URL count (< 50k) | 2 | URL count within limits |
| Meta robots not blocking indexation | 2 | No `noindex` on key pages |

**Scoring:**
- 13–15: Fully accessible
- 10–12: Minor gaps
- 5–9: Sitemap or robots issues
- 0–4: Search engines likely blocked

---

## Module 3: Structured Data (15 pts)

Assesses Schema.org markup quality for rich results eligibility.

| Check | Points | Pass Condition |
|-------|--------|----------------|
| JSON-LD blocks present on key pages | 5 | ≥ 1 JSON-LD per article/product page |
| Schema type appropriate for page content | 4 | Article, HowTo, FAQ, Product as applicable |
| Required fields populated per type | 4 | No missing `name`, `description`, `url` |
| No validation errors detected | 2 | Clean parse with no unknown types |

**Schema Required Fields by Type:**
- `Article`: headline, author, datePublished, image
- `HowTo`: name, step (array of HowToStep)
- `FAQPage`: mainEntity (array of Question/Answer)
- `Product`: name, description, offers (Offer with price)

**Scoring:**
- 13–15: Rich result eligible
- 10–12: Minor field gaps
- 5–9: Schema present but incomplete
- 0–4: No structured data

---

## Module 4: Content Structure (15 pts)

Assesses heading hierarchy, readability, and keyword signals.

| Check | Points | Pass Condition |
|-------|--------|----------------|
| Single H1 per page | 4 | Exactly 1 H1 on ≥ 90% of pages |
| Logical heading hierarchy (H1→H2→H3) | 4 | No skipped heading levels |
| Meta description present and < 160 chars | 4 | ≥ 80% pages have meta description |
| Title tag 50–60 characters | 3 | ≥ 70% titles in optimal range |

**Scoring:**
- 13–15: Strong content signals
- 10–12: Small fixes needed
- 5–9: Structural issues present
- 0–4: Poor content organization

---

## Module 5: Multimedia (10 pts)

Assesses image accessibility and optimization signals.

| Check | Points | Pass Condition |
|-------|--------|----------------|
| All images have alt text | 5 | ≥ 90% of images have non-empty alt |
| Images use modern formats (WebP/AVIF) | 3 | ≥ 50% images in modern format |
| No images > 200KB inline | 2 | Check src attributes for sizing hints |

**Scoring:**
- 9–10: Fully optimized
- 6–8: Minor gaps
- 3–5: Alt text or format issues
- 0–2: Accessibility problems

---

## Module 6: Content Quality (15 pts)

Assesses freshness, depth, and uniqueness signals.

| Check | Points | Pass Condition |
|-------|--------|----------------|
| Pages have ≥ 300 words of content | 5 | Estimated from HTML text nodes |
| Recent content updates (within 12 months) | 4 | `dateModified` or `lastmod` in sitemap |
| Low boilerplate ratio (nav/footer/content) | 3 | Content text > 40% of total text |
| No placeholder or stub content | 3 | Pages with < 50 words flagged |

**Scoring:**
- 13–15: High-quality content signals
- 10–12: Depth or freshness gaps
- 5–9: Thin content issues
- 0–4: Content quality critical

---

## Module 7: Site Architecture (10 pts)

Assesses internal linking and crawl efficiency.

| Check | Points | Pass Condition |
|-------|--------|----------------|
| Pages reachable within 3 clicks from home | 4 | Crawl depth ≤ 3 for key pages |
| Internal links use descriptive anchor text | 3 | No "click here" or bare URLs |
| No orphan pages (pages with 0 internal links) | 3 | All pages linked from ≥ 1 other page |

**Scoring:**
- 9–10: Excellent architecture
- 6–8: Minor linking gaps
- 3–5: Orphan or depth issues
- 0–2: Poor site structure

---

## Overall Score Interpretation

| Score | Grade | Action |
|-------|-------|--------|
| 85–100 | A | Maintain and monitor |
| 70–84 | B | Address medium-priority issues |
| 55–69 | C | Fix high-impact issues this sprint |
| 40–54 | D | Urgent technical remediation needed |
| 0–39 | F | Full audit and rebuild recommended |
