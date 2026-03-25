---
phase: 2
title: "Optimization Layer"
status: completed
priority: P1
effort: 10h
depends_on: [phase-01]
---

# Phase 2: Optimization Layer

## Context Links
- [Plan Overview](plan.md)
- [Phase 1: Core Pipeline](phase-01-core-pipeline.md)
- [Platform Research](../reports/researcher-260325-0344-openclaw-seo-research.md)

## Overview
Add quality scoring, content optimization, and image generation. Upgrades seo-content-flow from 4-step to full 6-step pipeline. Enables quality gates before publishing.

## Key Insights
- seo-scorer is utility layer — used by optimize-score AND as standalone quality check
- Image generation is parallel-safe (runs alongside optimization, both depend on write output)
- Flesch-Kincaid readability scoring can use stdlib (syllable counting heuristic); no heavy NLP deps
- Existing community `seo-aeo-diagnostics` uses 100-point scoring — adopt similar scale for consistency

## Requirements

### Functional
- Score any article on: keyword density, readability, heading structure, internal links, meta quality (0-100)
- Auto-fix: inject internal links, adjust readability, add missing schema markup
- Generate thumbnail + per-section images with SEO alt text
- Content-flow enforces minimum score before publish step

### Non-Functional
- Scorer runs in < 10 seconds (no API calls)
- Image generation supports configurable provider (DALL-E, Midjourney API, Stable Diffusion)
- Optimization pass preserves original article structure

## Architecture

### Updated Data Flow
```
keyword_map.json -> outline.json -> article.md
                                       |
                            +-----------+-----------+
                            |                       |
                      seo-optimize-score     seo-image-generate
                       (uses seo-scorer)         |
                            |                    |
                      optimized_article.md   images/ + image_map.json
                            |                    |
                            +----------+---------+
                                       |
                                 seo-publish-cms
```

### I/O Contracts

**score_report.json** (seo-scorer output)
```json
{
  "overall_score": 85,
  "breakdown": {
    "keyword_density": {"score": 90, "details": "Primary 1.5%, target 1-2%"},
    "readability": {"score": 78, "grade_level": 9.2, "target": "8-10"},
    "heading_structure": {"score": 95, "issues": []},
    "internal_links": {"score": 70, "count": 2, "recommended": 5},
    "meta_quality": {"score": 92, "title_length": 55, "desc_length": 148}
  },
  "suggestions": ["Add 3 more internal links", "Simplify paragraph 4"]
}
```

**image_map.json** (seo-image-generate output)
```json
{
  "featured_image": {"path": "images/featured.webp", "alt": "string", "width": 1200, "height": 630},
  "section_images": [
    {"section_heading": "string", "path": "images/section-1.webp", "alt": "string", "width": 800, "height": 450}
  ]
}
```

## Related Code Files

### Files to Create

#### seo-scorer/
```
seo-scorer/
├── SKILL.md
├── scripts/
│   └── seo-score-calculator.py      # Scoring engine (stdlib only)
├── references/
│   ├── score-report-schema.json
│   └── scoring-rubric.md            # Detailed scoring criteria per dimension
```

#### seo-optimize-score/
```
seo-optimize-score/
├── SKILL.md
├── scripts/
│   └── internal-link-suggester.py   # Find internal link opportunities from sitemap
├── references/
│   ├── optimization-rules.md        # Auto-fix rules per score dimension
│   └── schema-injection-guide.md    # JSON-LD schema templates
```

#### seo-image-generate/
```
seo-image-generate/
├── SKILL.md
├── scripts/
│   ├── image-prompt-builder.py      # Generate image prompts from article sections
│   └── alt-text-generator.py        # Generate SEO alt text from image context
├── references/
│   ├── image-map-schema.json
│   └── image-specs.md               # Size requirements per CMS, format rules
```

## Implementation Steps

### 1. seo-scorer (3h)
1. Create directory structure
2. Write `references/scoring-rubric.md`:
   - Keyword density: count primary/secondary occurrences, calculate %, score against 1-2% target
   - Readability: syllable-count Flesch-Kincaid approximation (no NLTK needed)
   - Heading structure: verify H1 exists, H2/H3 hierarchy, keyword presence in headings
   - Internal links: count `[text](url)` patterns, compare against word-count-based target
   - Meta quality: title length 50-60 chars, desc length 120-160 chars, keyword in both
3. Write `scripts/seo-score-calculator.py`:
   ```python
   # Pseudocode
   import json, re, sys

   def count_syllables(word): ...  # English heuristic
   def flesch_kincaid(text): ...   # FK grade level formula
   def keyword_density(text, keywords): ...  # occurrence / total_words
   def heading_score(markdown): ...  # Parse ## and ### structure
   def internal_link_score(markdown, word_count): ...
   def meta_score(frontmatter): ...

   def score_article(article_path):
       # Read markdown, parse frontmatter
       # Run each scorer
       # Return score_report.json
   ```
4. Write `references/score-report-schema.json`
5. Write SKILL.md:
   - Description: "Score SEO quality of any article measuring keyword density, readability, heading structure, internal links, and meta tags on a 0-100 scale"
   - Requires bins: [python3], no env vars needed
   - Steps: (1) read target article.md, (2) run seo-score-calculator.py, (3) output score_report.json, (4) flag if overall < 70

### 2. seo-optimize-score (3h)
1. Create directory structure
2. Write `references/optimization-rules.md`:
   - Low readability -> simplify sentences (agent rewrites)
   - Low keyword density -> suggest keyword insertion points
   - Low internal links -> run internal-link-suggester.py against site sitemap
   - Missing schema -> inject JSON-LD from templates
3. Write `references/schema-injection-guide.md` with JSON-LD templates for Article, HowTo, FAQ
4. Write `scripts/internal-link-suggester.py`:
   - Accept sitemap URL or list of site URLs
   - Match article keywords against existing page titles
   - Return suggested anchor text + target URL pairs
5. Write SKILL.md:
   - Description: "Optimize article SEO score by fixing readability, injecting internal links, improving keyword placement, and adding schema markup when article scores below target"
   - Requires env: [WORDPRESS_URL] (for sitemap access), anyBins: [python3, python]
   - Steps: (1) run seo-scorer on article, (2) if score >= 80 skip optimization, (3) for each low-scoring dimension apply optimization rules, (4) agent rewrites low-readability sections, (5) run internal-link-suggester.py, (6) inject suggested links, (7) add JSON-LD schema block, (8) re-score, (9) save optimized_article.md
   - Error handling: sitemap unavailable -> skip internal link suggestions

### 3. seo-image-generate (2h)
1. Create directory structure
2. Write `references/image-specs.md`:
   - Featured: 1200x630 WebP (OG image standard)
   - Section: 800x450 WebP
   - Alt text: < 125 chars, include primary keyword naturally
   - File naming: kebab-case from section heading
3. Write `scripts/image-prompt-builder.py`:
   - Parse article sections
   - Generate descriptive image prompts per section
   - Output JSON array of prompts
4. Write `scripts/alt-text-generator.py`:
   - Accept image context (section heading, keywords)
   - Generate SEO-friendly alt text
5. Write `references/image-map-schema.json`
6. Write SKILL.md:
   - Description: "Generate SEO-optimized thumbnail and section images with alt text for articles using AI image generation when preparing content for publishing"
   - Requires env: [GOOGLE_API_KEY], primaryEnv: GOOGLE_API_KEY
   - Requires anyBins: [python3, python]
   - Steps: (1) read article.md, (2) run image-prompt-builder.py, (3) for each prompt call image generation API via exec, (4) save images to images/ directory, (5) generate alt text per image, (6) save image_map.json
   - Error handling: API failure -> skip that image, continue; log warnings

### 4. Upgrade seo-content-flow (2h)
1. Update seo-content-flow/SKILL.md to full 6-step:
   ```yaml
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
     - name: images
       skill: seo-image-generate
       dependsOn: write
       env: { ARTICLE: "${write.output}" }
     - name: optimize
       skill: seo-optimize-score
       dependsOn: [write, images]
       env: { ARTICLE: "${write.output}", IMAGES: "${images.output}" }
     - name: publish
       skill: seo-publish-cms
       dependsOn: optimize
       approval: true
       env: { CONTENT: "${optimize.output}", CMS: "${CMS_TARGET}" }
   ```
2. Add quality gate: if optimize step score < 70 -> halt pipeline, notify user
3. Document parallel execution of images + optimize steps

## Todo List
- [x] Create seo-scorer/ directory structure
- [x] Write scoring-rubric.md
- [x] Write seo-score-calculator.py
- [x] Write score-report-schema.json
- [x] Write seo-scorer/SKILL.md
- [x] Test scorer against Phase 1 sample articles
- [x] Create seo-optimize-score/ directory structure
- [x] Write optimization-rules.md + schema-injection-guide.md
- [x] Write internal-link-suggester.py
- [x] Write seo-optimize-score/SKILL.md
- [x] Test optimize-score: article below 70 -> optimized above 80
- [x] Create seo-image-generate/ directory structure
- [x] Write image-specs.md
- [x] Write image-prompt-builder.py + alt-text-generator.py
- [x] Write image-map-schema.json
- [x] Write seo-image-generate/SKILL.md
- [x] Test image-generate with sample article
- [x] Upgrade seo-content-flow to 6-step
- [x] Integration test: full 6-step pipeline
- [x] Validate all new SKILL.md files against ClawHub checklist

## Success Criteria
- seo-scorer produces consistent scores (same input -> same score)
- optimize-score lifts articles from < 70 to > 80 reliably
- Image generation produces correctly sized WebP with meaningful alt text
- Full 6-step content-flow completes in < 20 min
- Quality gate halts pipeline when score threshold not met

## Risk Assessment

| Risk | Impact | Mitigation |
|------|--------|------------|
| Readability scoring inaccurate for Vietnamese | Medium | VI uses sentence-length heuristic instead of syllable-based FK; separate scoring path |
| Image gen API costs add up in batch | Medium | Make image step optional in content-flow; skip if no GOOGLE_API_KEY |
| Internal link suggester needs sitemap access | Low | Fall back to manual suggestions if sitemap unavailable |
| Score inflation from gaming metrics | Low | Multiple dimensions prevent single-metric gaming; human review via approval gate |

## Security Considerations
- GOOGLE_API_KEY in env only
- Image generation scripts validate response before saving (no arbitrary file writes)
- Internal-link-suggester only reads sitemap (GET requests only)
- No user content sent to external services beyond image gen API

## Next Steps
- Phase 3 uses seo-scorer as baseline for technical-audit scoring
- Consider: seo-scorer could be extended with backlink scoring in Phase 3
- Image generation provider abstraction (multiple providers) deferred to Phase 4
