---
phase: 1
title: "Core Pipeline MVP"
status: completed
priority: P1
effort: 12h
---

# Phase 1: Core Pipeline MVP

## Context Links
- [Plan Overview](plan.md)
- [Brainstorm Report](../reports/brainstorm-260325-0344-openclaw-seo-skills.md)
- [Platform Research](../reports/researcher-260325-0344-openclaw-seo-research.md)

## Overview
Build 4 core skills + basic content-flow workflow. Delivers keyword-to-publish pipeline for WordPress. Validates I/O contract chain before optimization layers.

## Key Insights
- OpenClaw description field is load-bearing for skill triggering; invest in precise "when to use" signals
- Numbered steps > prose for agent reliability
- ClawFlow artifact passing uses `${step-name.output}` syntax
- Keep SKILL.md < 500 lines; push schemas/examples to references/

## Requirements

### Functional
- Keyword input -> keyword_map.json with intent, LSI, clusters, volume estimates
- keyword_map -> outline.json with H2/H3, meta title/desc, schema suggestion
- outline -> article.md with natural keyword placement, VI/EN support
- article -> published WordPress post via REST API

### Non-Functional
- Each skill independently testable
- JSON I/O contracts validated between steps
- < 5 min per skill execution
- Graceful degradation when optional APIs (SEMrush/Ahrefs) unavailable

## Architecture

### Data Flow
```
keyword (string)
  -> seo-keyword-research -> keyword_map.json
    -> seo-outline-generate -> outline.json
      -> seo-content-write -> article.md
        -> seo-publish-cms -> published URL
```

### I/O Contracts

**keyword_map.json**
```json
{
  "primary_keyword": "string",
  "search_intent": "informational|commercial|transactional|navigational",
  "lsi_keywords": ["string"],
  "long_tail": ["string"],
  "clusters": [{"name": "string", "keywords": ["string"]}],
  "volume_estimate": "low|medium|high",
  "language": "en|vi"
}
```

**outline.json**
```json
{
  "title": "string",
  "meta_title": "string (< 60 chars)",
  "meta_description": "string (< 160 chars)",
  "slug": "string",
  "schema_type": "Article|HowTo|FAQ|Product",
  "sections": [
    {
      "heading": "string",
      "level": 2,
      "subsections": [{"heading": "string", "level": 3, "notes": "string"}],
      "target_keywords": ["string"]
    }
  ],
  "faq": [{"question": "string", "answer_hint": "string"}]
}
```

**article.md** - Standard markdown with YAML frontmatter containing meta fields

## Related Code Files

### Files to Create

#### seo-keyword-research/
```
seo-keyword-research/
├── SKILL.md
├── scripts/
│   └── keyword-analyzer.py          # Parse web_search results, cluster keywords
├── references/
│   ├── keyword-map-schema.json      # JSON schema for output validation
│   └── search-intent-guide.md       # Intent classification rules
```

#### seo-outline-generate/
```
seo-outline-generate/
├── SKILL.md
├── scripts/
│   └── outline-validator.py         # Validate outline structure, char limits
├── references/
│   ├── outline-schema.json
│   └── schema-markup-guide.md       # Schema.org type selection guide
```

#### seo-content-write/
```
seo-content-write/
├── SKILL.md
├── scripts/
│   └── content-formatter.py         # Format markdown, inject frontmatter
├── references/
│   ├── writing-guidelines.md        # Tone, style, keyword density targets
│   └── multilingual-rules.md        # VI/EN specific rules
```

#### seo-publish-cms/
```
seo-publish-cms/
├── SKILL.md
├── scripts/
│   ├── wp-publisher.py              # WordPress REST API client
│   └── media-uploader.py            # Upload images to WP media library
├── references/
│   └── wp-api-reference.md          # WP REST API endpoints, auth format
```

#### seo-content-flow/
```
seo-content-flow/
├── SKILL.md                         # ClawFlow YAML definition + orchestration instructions
```

## Implementation Steps

### 1. seo-keyword-research (3h)
1. Create directory structure
2. Write `references/keyword-map-schema.json` with full JSON schema
3. Write `references/search-intent-guide.md` with 4-intent classification rules + examples
4. Write `scripts/keyword-analyzer.py`:
   - Accept raw search results as JSON stdin
   - Extract PAA questions, related searches, LSI terms
   - Cluster by semantic similarity (simple TF-IDF, no heavy deps)
   - Output keyword_map.json
   - Pin deps: `json`, `re`, `collections` (stdlib only for v1)
5. Write SKILL.md:
   - Frontmatter: name, description ("Research SEO keywords with search intent analysis, LSI discovery, and clustering when given a keyword or topic"), requires env: [SEMRUSH_API_KEY], anyBins: [python3, python]
   - Context: agent is SEO keyword researcher
   - Steps: (1) validate input keyword, (2) web_search for keyword + variations, (3) web_search for "keyword" + PAA/related, (4) optionally call SEMrush API via exec if key available, (5) run keyword-analyzer.py, (6) validate output against schema, (7) save keyword_map.json
   - Error handling: SEMrush unavailable -> skip, fall back to web_search only
   - Output format: keyword_map.json path

### 2. seo-outline-generate (2h)
1. Create directory structure
2. Write `references/outline-schema.json`
3. Write `references/schema-markup-guide.md` (Article, HowTo, FAQ, Product selection criteria)
4. Write `scripts/outline-validator.py`:
   - Validate meta_title < 60 chars, meta_description < 160 chars
   - Ensure H2/H3 hierarchy valid
   - Check all target_keywords present in keyword_map
   - Exit 0 if valid, exit 1 with errors
5. Write SKILL.md:
   - Description: "Generate SEO-optimized article outline with heading hierarchy, meta tags, and schema markup suggestion from keyword research data"
   - Requires env: none (pure LLM skill)
   - Steps: (1) read keyword_map.json, (2) analyze search intent to pick schema type, (3) generate H2/H3 structure targeting keyword clusters, (4) write meta title/desc, (5) suggest FAQ section from long-tail keywords, (6) validate with outline-validator.py, (7) save outline.json

### 3. seo-content-write (3h)
1. Create directory structure
2. Write `references/writing-guidelines.md`:
   - Target keyword density: 1-2% primary, 0.5-1% secondary
   - Readability: Flesch-Kincaid Grade 8-10 for EN, equivalent for VI
   - Min 1500 words, max 3000 words
   - Natural keyword placement rules
3. Write `references/multilingual-rules.md`:
   - VI: formal tone, avoid loan words where Vietnamese exists
   - EN: conversational, active voice
   - Language detection from outline.json `language` field
4. Write `scripts/content-formatter.py`:
   - Parse article markdown
   - Inject YAML frontmatter (title, meta, date, slug)
   - Validate keyword density
   - Output article.md
5. Write SKILL.md:
   - Description: "Write full SEO article from outline with natural keyword placement, proper heading structure, and multilingual support (Vietnamese/English)"
   - Steps: (1) read outline.json, (2) determine language, (3) write intro targeting primary keyword, (4) write each section per H2/H3 structure, (5) write FAQ section as schema-ready markup, (6) write conclusion with CTA, (7) run content-formatter.py, (8) save article.md

### 4. seo-publish-cms (2h)
1. Create directory structure
2. Write `scripts/wp-publisher.py`:
   ```python
   # Pseudocode
   import requests, json, sys, os

   WP_URL = os.environ["WORDPRESS_URL"]
   WP_TOKEN = os.environ["WORDPRESS_TOKEN"]

   def upload_media(image_path):
       # POST /wp-json/wp/v2/media
       # Return media_id

   def create_post(title, content, slug, meta, categories, tags, featured_media_id):
       # POST /wp-json/wp/v2/posts
       # Set status="draft" (approval gate)
       # Return post URL

   def main():
       article = json.load(sys.stdin)
       # Parse frontmatter, upload images, create post
       print(json.dumps({"url": post_url, "status": "draft"}))
   ```
3. Write `references/wp-api-reference.md` with endpoint docs
4. Write SKILL.md:
   - Description: "Publish SEO article to WordPress via REST API with media upload, categories, tags, and featured image when content is ready for CMS"
   - Requires env: [WORDPRESS_URL, WORDPRESS_TOKEN], primaryEnv: WORDPRESS_TOKEN
   - Requires bins: [python3]
   - Steps: (1) read article.md frontmatter, (2) parse images from article, (3) upload each image via media-uploader.py, (4) replace image paths with WP URLs, (5) create post as draft, (6) return published URL
   - Error handling: auth failure -> clear message, image upload failure -> publish without images + warn

### 5. seo-content-flow (2h)
1. Write SKILL.md with ClawFlow definition:
   ```yaml
   # In SKILL.md instructions section
   name: seo-content-flow
   description: Full-auto SEO content from keyword to WordPress publish
   workflows:
     - name: research
       skill: seo-keyword-research
       env: { KEYWORD: "${INPUT}" }
     - name: outline
       skill: seo-outline-generate
       dependsOn: research
       env: { KEYWORD_MAP: "${research.output}" }
     - name: write
       skill: seo-content-write
       dependsOn: outline
       env: { OUTLINE: "${outline.output}", LANG: "${LANG}" }
     - name: publish
       skill: seo-publish-cms
       dependsOn: write
       approval: true
       env: { CONTENT: "${write.output}", CMS: "wordpress" }
   ```
2. Include manual trigger instructions and env var setup
3. Document expected execution time (~15 min end-to-end)

## Todo List
- [x] Create seo-keyword-research/ directory structure
- [x] Write keyword-map-schema.json
- [x] Write search-intent-guide.md
- [x] Write keyword-analyzer.py
- [x] Write seo-keyword-research/SKILL.md
- [x] Test keyword-research standalone
- [x] Create seo-outline-generate/ directory structure
- [x] Write outline-schema.json
- [x] Write schema-markup-guide.md
- [x] Write outline-validator.py
- [x] Write seo-outline-generate/SKILL.md
- [x] Test outline-generate with sample keyword_map.json
- [x] Create seo-content-write/ directory structure
- [x] Write writing-guidelines.md + multilingual-rules.md
- [x] Write content-formatter.py
- [x] Write seo-content-write/SKILL.md
- [x] Test content-write with sample outline.json
- [x] Create seo-publish-cms/ directory structure
- [x] Write wp-publisher.py + media-uploader.py
- [x] Write wp-api-reference.md
- [x] Write seo-publish-cms/SKILL.md
- [x] Test publish-cms against WP staging instance
- [x] Create seo-content-flow/SKILL.md
- [x] Integration test: full keyword-to-publish pipeline
- [x] Validate all SKILL.md files against 13-point ClawHub checklist

## Success Criteria
- Each skill produces valid output matching its JSON schema
- Pipeline runs keyword -> draft WP post in < 15 min
- Skills degrade gracefully without optional APIs (SEMrush)
- All SKILL.md files pass ClawHub security analysis (no unpinned deps, no pipe-to-interpreter)
- VI and EN articles both produce coherent content

## Risk Assessment

| Risk | Impact | Mitigation |
|------|--------|------------|
| web_search results inconsistent across regions | Medium | Normalize extraction in keyword-analyzer.py; multiple query patterns |
| WP REST API auth complexity | Medium | Document Application Passwords + JWT; test both methods |
| Keyword clustering quality without ML libs | Low | Start with TF-IDF (stdlib); upgrade to sentence-transformers in Phase 2 if needed |
| Article quality below SEO standards | High | seo-scorer (Phase 2) as quality gate; manual review via approval gate |

## Security Considerations
- WORDPRESS_TOKEN stored in env only, never in SKILL.md or scripts
- WP posts created as "draft" by default (approval gate before publish)
- SEMrush API key optional; skill functional without it
- No pipe-to-interpreter patterns in any script
- All Python scripts use stdlib only (no pip install in v1)

## Next Steps
- After Phase 1 validated: Phase 2 adds seo-scorer quality gate + image generation
- Content-flow upgraded from 4-step to 6-step in Phase 2
- Consider: should keyword_map.json include competitor URLs for Phase 3 readiness?
