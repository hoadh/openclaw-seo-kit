# Search Intent Classification Guide

Search intent (user intent) is the primary goal behind a search query. Correct classification is critical for content alignment and ranking.

---

## 1. Informational Intent

The user wants to learn or understand something. No purchase decision is implied.

**Signal Words:**
- how, what, why, who, when, where
- guide, tutorial, tips, examples, explained, definition
- "what is", "how to", "learn", "understand", "vs" (comparison for knowledge)

**Examples:**
- "what is SEO"
- "how to bake sourdough bread"
- "why is the sky blue"
- "python list comprehension explained"
- "best time to plant tomatoes" (research, not buy)

**Content Match:** Blog posts, guides, tutorials, explainers, wikis

---

## 2. Commercial Intent

The user is researching before making a purchase or decision. They compare options.

**Signal Words:**
- best, top, review, reviews, compare, comparison, vs, versus
- "best X for Y", "X vs Y", "top 10", "alternatives to"
- recommended, rated, ranked, worth it, pros and cons

**Examples:**
- "best laptops for students 2024"
- "Shopify vs WooCommerce"
- "top project management tools"
- "iPhone 15 review"
- "cheap VPN worth it"

**Content Match:** Comparison articles, listicles, review posts, buying guides

---

## 3. Transactional Intent

The user is ready to take an action — buy, sign up, download, or complete a task.

**Signal Words:**
- buy, order, purchase, shop, get, deal, discount, coupon, price, cost
- "for sale", "cheap", "free trial", "download", "sign up", "subscribe"
- brand + model names (e.g., "Nike Air Max buy")

**Examples:**
- "buy iPhone 15 online"
- "Netflix free trial"
- "download Photoshop"
- "coupon code for Shopify"
- "order pizza near me"

**Content Match:** Product pages, landing pages, pricing pages, checkout flows

---

## 4. Navigational Intent

The user wants to reach a specific website, brand, or page. They already know where they want to go.

**Signal Words:**
- brand names, product names, site names
- "login", "sign in", "official site", "homepage"
- "[brand] + location/contact/support"

**Examples:**
- "facebook login"
- "github"
- "amazon customer service"
- "NYTimes official site"
- "OpenAI playground"

**Content Match:** Homepage, login pages, brand pages (hard to rank against — focus on brand terms you own)

---

## Classification Decision Flow

```
Does query contain a brand/site name the user wants to visit?
  YES → Navigational

Does query contain buy/order/price/download/sign up signals?
  YES → Transactional

Does query contain best/review/compare/vs signals?
  YES → Commercial

Otherwise → Informational
```

---

## Mixed Intent Handling

Some queries carry mixed signals. Use the dominant signal:

- "best free project management software" → Commercial (best/compare dominates over "free")
- "how to buy Bitcoin" → Informational (how-to dominates; user is learning, not buying now)
- "download Python 3.12" → Transactional (download = action)

When uncertain, default to **Informational** as the safest classification for content strategy.
