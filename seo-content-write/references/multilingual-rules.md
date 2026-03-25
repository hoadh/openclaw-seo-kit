# Multilingual Content Rules

## Language Detection

Language is determined in this priority order:

1. `language` field in `outline.json` — highest priority
2. `language` field in `keyword_map.json` — fallback
3. Script detection from primary keyword — Vietnamese diacritics → `vi`, Latin → `en`
4. Default to `en` if undetectable

Supported values: `en` (English), `vi` (Vietnamese)

---

## English (EN) Rules

### Tone
- **Conversational and approachable** — write as if explaining to a knowledgeable friend
- Use second-person ("you", "your") to engage the reader directly
- Avoid overly formal or academic phrasing

### Voice
- **Active voice strongly preferred**
- Passive voice acceptable only when the actor is unknown or unimportant
- Target: < 15% passive sentences across the article

### Sentence Structure
- Average sentence length: **15–20 words**
- Vary sentence length for rhythm — short punchy sentences after complex ones
- Avoid sentences over 35 words; split them

### Contractions
- Use contractions freely: don't, it's, you'll, we're, isn't, can't
- Contractions improve readability score and feel less robotic

### Word Choice
- Prefer common words over obscure synonyms (use "use" not "utilize", "help" not "facilitate")
- Technical terms are acceptable when necessary — always define on first use
- Avoid jargon that readers outside the field would not understand

### Readability Target
- **Flesch-Kincaid Grade Level: 8–10**
- Use a readability checker if available; aim for Grade 9 as the sweet spot
- Grade 8: "The cat sat on the mat" — very accessible
- Grade 10: Standard newspaper editorial — educated general audience

### Paragraph Rules
- 2–4 sentences per paragraph
- One idea per paragraph
- Start each paragraph with a topic sentence

---

## Vietnamese (VI) Rules

### Register by Content Type

| Content Type | Register | Notes |
|---|---|---|
| Business / B2B / Finance / Legal | Formal | Use "quý vị", avoid contractions, full sentences |
| Lifestyle / Health / Beauty / Food | Informal-friendly | Use "bạn", conversational tone, shorter sentences |
| Tech / SaaS / Startup | Semi-formal | "bạn" acceptable, technical terms in English |
| E-commerce / Product | Persuasive-formal | Mix "bạn" with formal verbs |

**Rule:** Match the register to the brand's target audience, not the writer's preference. Default to formal when unsure.

### Common SEO Title Patterns in Vietnamese

Vietnamese searchers use question and comparison formats heavily. Use these proven patterns:

| Pattern | Example |
|---|---|
| `[Keyword] là gì?` | "SEO là gì? Hướng dẫn toàn diện cho người mới" |
| `Cách [keyword] hiệu quả` | "Cách tối ưu từ khóa hiệu quả năm 2024" |
| `Top N [keyword] tốt nhất` | "Top 10 công cụ SEO tốt nhất cho doanh nghiệp nhỏ" |
| `[Keyword]: Hướng dẫn A-Z` | "Content Marketing: Hướng dẫn A-Z từ cơ bản đến nâng cao" |
| `So sánh [A] và [B]` | "So sánh WordPress và Shopify: Nên chọn nền tảng nào?" |
| `[Keyword] cho [audience]` | "SEO cho người mới bắt đầu: Checklist 30 bước" |
| `Tại sao [keyword] quan trọng` | "Tại sao tốc độ trang web quan trọng với SEO?" |
| `Bí quyết [keyword]` | "Bí quyết viết content chuẩn SEO thu hút người đọc" |

**Note:** Include the year (e.g., "2024", "2025") in titles for evergreen content — Vietnamese users filter by recency in search intent.

### Keyword Density for Vietnamese

Vietnamese compound words (từ ghép) require special handling:

- **Single keyword:** Count exact occurrences — "từ khóa" as a two-word unit
- **Compound keyword matching:** "tối ưu hóa công cụ tìm kiếm" contains sub-phrases ("tối ưu hóa", "công cụ tìm kiếm") — each sub-phrase counts as a partial match worth 0.5x
- **Target density:** 1–2% of total word count (same as EN) but count by Vietnamese word tokens, not syllables
- **Diacritics matter:** "tối ưu" ≠ "toi uu" — always preserve full diacritical marks in keyword matching
- **Tokenization:** Split on spaces; Vietnamese words are space-separated like English at the written level

### Tone
- **Formal and respectful** — Vietnamese readers expect polished, professional writing
- Use third-person or impersonal constructions where natural
- Avoid colloquialisms or slang unless the brand voice explicitly allows it
- See "Register by Content Type" table above for context-specific guidance

### Sentence Length
- Average sentence length: **under 25 words**
- Vietnamese sentences can become unwieldy — break compound sentences at conjunctions
- Use commas and clause breaks generously

### Loan Word Policy

Prefer native Vietnamese terms over loan words when a clear equivalent exists:

| Avoid (loan word) | Prefer (Vietnamese) |
|-------------------|---------------------|
| software | phần mềm |
| download | tải xuống |
| online | trực tuyến |
| website | trang web |
| email | thư điện tử (formal) / email (acceptable in tech context) |
| marketing | tiếp thị |
| content | nội dung |
| keyword | từ khóa |
| traffic | lưu lượng truy cập |
| backlink | liên kết ngược |
| SEO | tối ưu hóa công cụ tìm kiếm (first use); SEO acceptable thereafter |
| AI | trí tuệ nhân tạo (first use); AI acceptable thereafter |
| blog | blog (widely accepted, no replacement needed) |
| app | ứng dụng |
| server | máy chủ |
| database | cơ sở dữ liệu |

**Exception:** Technical proper nouns (Google, Python, WordPress) are kept as-is.

**Rule:** If the Vietnamese term would confuse the reader or is longer than twice the loan word without adding clarity, the loan word is acceptable.

### Contractions
- Vietnamese does not use contractions in formal writing
- Do not attempt to simulate contraction-like structures

### Honorifics and Address
- Use "bạn" (you — informal/friendly) for blog content aimed at general audiences
- Use "quý vị" or "bạn đọc" for more formal publications
- Be consistent throughout the article — do not mix address forms

### Number Formatting
- Use Vietnamese conventions: period as thousands separator, comma as decimal
  - Example: 1.000.000 (one million), 3,14 (pi)
- Exception: When displaying code, URLs, or technical values, use international format

### Heading Style
- Vietnamese headings: capitalize only the first word and proper nouns
  - Correct: "Cách tối ưu hóa từ khóa hiệu quả"
  - Incorrect: "Cách Tối Ưu Hóa Từ Khóa Hiệu Quả"

### Punctuation
- Use curly/smart quotes where possible: "..." not "..."
- Ellipsis: use "…" (single character) not "..."
- Em dash: use "—" for parenthetical asides (same as EN)

---

## Mixed-Language Content

If a section references English-language tools, brand names, or technical terms:

- Introduce the English term with Vietnamese explanation on first use
- Example: "Google Search Console (Bảng điều khiển tìm kiếm Google) là công cụ..."
- Do not italicize or quote foreign terms — treat them as part of the sentence

---

## FAQ Section Language Rules

| Language | Question format | Answer format |
|----------|----------------|---------------|
| EN | Natural question phrasing, end with "?" | Conversational, 2–4 sentences |
| VI | Formal question phrasing, end with "?" | Formal, 2–3 sentences, avoid loan words |

---

## content-formatter.py Language Behavior

The `content-formatter.py` script reads the `language` field from YAML frontmatter to:
- Set the `lang` attribute in output metadata
- Report density stats labeled in the correct language context
- Apply the correct date format in frontmatter (`YYYY-MM-DD` for both, but display format differs)
