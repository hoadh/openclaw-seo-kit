# Core Web Vitals Proxy Signals

Since Lighthouse cannot run in this environment, these HTML-level proxy signals
approximate CWV performance without browser execution.

---

## LCP Proxies (Largest Contentful Paint)

LCP measures time to render the largest visible element. Target: < 2.5s

### What to check in HTML:

| Signal | Good | Bad | How to detect |
|--------|------|-----|---------------|
| Hero image has `loading="eager"` or no lazy | Present | Missing | `<img` without `loading="lazy"` in first viewport |
| `<link rel="preload">` for hero image | Present | Missing | Check `<head>` for preload hints |
| HTML document size | < 100KB | > 200KB | `len(html_bytes)` |
| Server-side rendered content | Text in HTML | Empty `<div>` shells | Check `<main>` or `<article>` has text nodes |
| Above-fold images are not lazy-loaded | Correct | `loading="lazy"` on hero | First 2 `<img>` tags |

---

## FID / INP Proxies (Interaction to Next Paint)

INP measures responsiveness. Target: < 200ms

### What to check in HTML:

| Signal | Good | Bad | How to detect |
|--------|------|-----|---------------|
| External script count | ≤ 5 | > 10 | Count `<script src=` tags |
| Render-blocking scripts in `<head>` | 0 blocking | Any without `defer`/`async` | `<script src=` without `defer` or `async` in `<head>` |
| Third-party tag count | ≤ 3 | > 6 | Count unique external domains in `<script src=` |
| Inline script size | < 10KB total | > 50KB | Sum `len()` of inline `<script>` content |

---

## CLS Proxies (Cumulative Layout Shift)

CLS measures visual stability. Target: < 0.1

### What to check in HTML:

| Signal | Good | Bad | How to detect |
|--------|------|-----|---------------|
| Images have explicit `width` + `height` | Present on all | Missing | `<img` without both `width=` and `height=` |
| Ad/iframe slots have explicit dimensions | Present | Missing | `<iframe` without `width`/`height` |
| Web fonts use `font-display: swap` | Present | Missing or `block` | Check `<style>` or linked CSS for `font-display` |
| No late-injected content above fold | N/A | Dynamic banners | Look for empty `<div class="banner">` placeholders |

---

## TTFB Proxies (Time to First Byte)

TTFB measures server response speed. Target: < 800ms

### What to check in HTML:

| Signal | Good | Bad | How to detect |
|--------|------|-----|---------------|
| Server response headers hint caching | `Cache-Control` present | Missing | Parse HTTP headers if available |
| CDN indicators | CDN domain in assets | All on same origin | Check asset URLs for cdn., cloudfront., etc. |
| HTML minification | Compact HTML | Excessive whitespace | `len(minified) / len(raw)` ratio |

---

## Lazy Loading Assessment

| Element | Correct Use | Incorrect Use |
|---------|-------------|---------------|
| Below-fold images | `loading="lazy"` | No lazy attribute |
| Above-fold hero | No lazy / `loading="eager"` | `loading="lazy"` |
| iframes | `loading="lazy"` | No lazy on heavy embeds |

---

## Render-Blocking Resource Check

Render-blocking resources delay First Contentful Paint.

**Flag these patterns in `<head>` (before `</head>`):**
- `<script src="...">` without `defer` or `async`
- `<link rel="stylesheet">` from third-party domains (Google Fonts, etc.) without `media` attribute tricks

**Safe patterns:**
- `<script src="..." defer>`
- `<script src="..." async>`
- `<link rel="preconnect">` (non-blocking)
- Inline critical CSS in `<style>`

---

## Proxy Signal Scoring

Each category contributes to an estimated performance grade:

| Issues Found | Estimated CWV Impact |
|-------------|----------------------|
| 0–1 | Likely Good |
| 2–3 | Likely Needs Improvement |
| 4+ | Likely Poor |

Report findings as proxy indicators, not absolute CWV scores.
Always recommend a real Lighthouse audit for definitive measurements.
