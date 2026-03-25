# SEO Skills Suite Documentation

Complete documentation for the 16-component SEO automation skill suite (12 OpenClaw skills + 3 ClawFlow workflows + 1 shared utility).

## Quick Navigation

### For First-Time Users
1. **[Getting Started](./seo-getting-started.md)** — Setup, configuration, and first run
2. **[Workflow Overview](./seo-workflow.md)** — High-level pipeline and execution examples

### For Daily Use
- **[Skills Reference](./seo-skills-reference.md)** — Input/output contracts for each skill
- **[Troubleshooting](./seo-troubleshooting.md)** — Common issues and solutions

### For Deep Dives
- **[Architecture](./seo-architecture.md)** — System design, data flow, integration patterns
- **Individual skill docs** — See SKILL.md in each skill directory (/workspace/seo-{skill-name}/)

---

## Documentation Files

| File | Purpose | Audience |
|------|---------|----------|
| **[README.md](./README.md)** | You are here - documentation index | Everyone |
| **[seo-getting-started.md](./seo-getting-started.md)** | Setup, first run, troubleshooting guide | New users, DevOps |
| **[seo-workflow.md](./seo-workflow.md)** | Pipeline overview and execution examples | All users |
| **[seo-skills-reference.md](./seo-skills-reference.md)** | Input/output for all 16 skills | Developers, integrators |
| **[seo-architecture.md](./seo-architecture.md)** | System design, data flow, extension patterns | Architects, developers |
| **[seo-troubleshooting.md](./seo-troubleshooting.md)** | Issue diagnosis and solutions | Support, experienced users |

---

## Component Overview

### Layer 1: Utility Services (4 components)
Core utilities used by other skills

| Component | Purpose | Dependencies |
|-----------|---------|--------------|
| **seo-serp-scraper** | Web search & SERP extraction | None |
| **seo-cms-adapter** | Unified CMS interface (WP/Shopify/Haravan) | None |
| **seo-scorer** | SEO quality scoring engine (0-100) | None |
| **seo-shared-utils** | Validators, helpers, multilingual support | None |

### Layer 2: Core Skills (9 components)
Specialized SEO tools for content creation and analysis

| # | Skill | Input | Output | Time | Depends On |
|---|-------|-------|--------|------|-----------|
| 1 | **seo-keyword-research** | Seed keyword | keyword_map.json | 2-3 min | seo-serp-scraper |
| 2 | **seo-outline-generate** | keyword_map.json | outline.json | 1 min | — |
| 3 | **seo-content-write** | outline.json | article.md | 3-4 min | — |
| 4 | **seo-image-generate** | article.md | image_map.json | 5-8 min | — |
| 5 | **seo-optimize-score** | article.md + images | optimized_article.md | 2-3 min | seo-scorer |
| 6 | **seo-publish-cms** | optimized_article.md | post_url + post_id | 1-2 min | seo-cms-adapter |
| 7 | **seo-technical-audit** | website_url | audit_report.json | 5-10 min | seo-serp-scraper, seo-scorer |
| 8 | **seo-competitor-analyze** | primary_keyword | competitor_report.json | 3-4 min | seo-serp-scraper |
| 9 | **seo-aeo-optimize** | article.md | enhanced_content | 2-3 min | — |

### Layer 3: Orchestration Workflows (3 components)
ClawFlow orchestrations combining multiple skills

| Workflow | Purpose | Steps | Time |
|----------|---------|-------|------|
| **seo-content-flow** | Full automated SEO pipeline | 6 steps (research → outline → write → images → optimize → publish) | ~25 min |
| **seo-audit-flow** | Site audit workflow | 2 steps (technical-audit → generate-report) | ~8-12 min |
| **seo-batch-flow** | Multi-keyword bulk processing | N × seo-content-flow | 25 min × keywords |

---

## Quick Start

### 1. Setup (5 minutes)
```bash
# Set required environment variables
export WORDPRESS_URL="https://your-site.com"
export WORDPRESS_TOKEN="username:app_password"
export GOOGLE_API_KEY="your-api-key"

# Optional
export SEMRUSH_API_KEY="your-semrush-key"
export CONTENT_LANG="en"  # or "vi"
```

### 2. Create First Article (25 minutes)
```bash
openclaw run seo-content-flow "best running shoes for beginners"
```

### 3. Review in WordPress
- Go to WP Admin > Posts > Drafts
- Find your new article
- Review and publish when ready

**See [Getting Started](./seo-getting-started.md) for detailed instructions.**

---

## Common Workflows

### Generate Single Article
```bash
openclaw run seo-content-flow "keyword"
```

### Generate Vietnamese Content
```bash
export CONTENT_LANG=vi
openclaw run seo-content-flow "máy tính xách tay tốt nhất"
```

### Audit Your Website
```bash
openclaw run seo-audit-flow "https://your-site.com"
```

### Analyze Competitors
```bash
openclaw run seo-competitor-analyze "your-keyword"
```

### Batch Process Keywords
```bash
openclaw run seo-batch-flow keywords.json
```

### Publish to Shopify
```bash
export CMS_TARGET=shopify
export SHOPIFY_STORE_URL="https://mystore.myshopify.com"
export SHOPIFY_ACCESS_TOKEN="shpat_..."
openclaw run seo-content-flow "keyword"
```

**See [Workflow Overview](./seo-workflow.md) for more examples.**

---

## Data Flow

```
Input Keyword
    ↓
[1] Keyword Research
    ├─ Web search
    ├─ SEMrush API (optional)
    └─ LSI extraction
    ↓ keyword_map.json
[2] Outline Generation
    ├─ H1/H2/H3 structure
    ├─ Meta tags
    └─ Content strategy
    ↓ outline.json
[3] Content Writing
    ├─ AI article generation
    ├─ Natural keyword placement
    └─ YAML frontmatter
    ↓ article.md
    ├────────────────────────┐
    ↓                        ↓
[4] Image Generation    [5a] Score Analysis
    ├─ Featured image        ├─ Keyword optimization
    ├─ Section images        ├─ Heading structure
    └─ Alt text              ├─ Readability
    ↓                        └─ Link quality
    └────────────────────────┘
                ↓
            [5b] Optimize
                ├─ Apply fixes
                ├─ Inject internal links
                └─ Quality gate: score >= 70
                ↓ optimized_article.md + score_report.json
            [6] Publish (approval required)
                ├─ Create as draft
                ├─ Attach featured image
                └─ Set metadata
                ↓
            Published URL (draft status)
```

**See [Architecture](./seo-architecture.md) for detailed data flow and integration patterns.**

---

## Environment Variables

### Required
```bash
WORDPRESS_URL              # WordPress site URL
WORDPRESS_TOKEN            # username:app_password
GOOGLE_API_KEY         # AI image generation API key
```

### Optional
```bash
SEMRUSH_API_KEY           # For keyword research (gracefully skipped if absent)
CONTENT_LANG              # "en" (default) or "vi"
CMS_TARGET                # "wordpress" (default), "shopify", "haravan"
```

### CMS-Specific (if using non-WordPress)
```bash
# For Shopify
SHOPIFY_STORE_URL
SHOPIFY_ACCESS_TOKEN
SHOPIFY_BLOG_ID

# For Haravan
HARAVAN_STORE_URL
HARAVAN_ACCESS_TOKEN
HARAVAN_BLOG_ID
```

**See [Getting Started](./seo-getting-started.md) for detailed setup.**

---

## Troubleshooting

Quick reference for common issues:

| Issue | First Step | Reference |
|-------|-----------|-----------|
| No search results | Try broader keyword | [Troubleshooting](./seo-troubleshooting.md#step-1) |
| Score < 70 | Review score_report.json suggestions | [Troubleshooting](./seo-troubleshooting.md#step-5) |
| Image generation fails | Check GOOGLE_API_KEY | [Troubleshooting](./seo-troubleshooting.md#step-4) |
| Can't publish to WordPress | Verify REST API enabled | [Troubleshooting](./seo-troubleshooting.md#step-6) |
| Wrong language content | Set CONTENT_LANG env var | [Troubleshooting](./seo-troubleshooting.md#step-3) |

**See [Troubleshooting](./seo-troubleshooting.md) for comprehensive issue resolution.**

---

## Resume from Failures

Each step saves output files. You can resume without re-running earlier steps:

```bash
# If keyword research succeeded but outline failed
openclaw run seo-content-flow --from outline --input keyword_map.json

# If content writing succeeded but images failed
openclaw run seo-content-flow --from images --input article.md

# After manual edits to article
openclaw run seo-content-flow --from optimize --input article.md

# Just publish after review
openclaw run seo-content-flow --from publish --input optimized_article.md
```

---

## Individual Skill Documentation

Each skill has comprehensive documentation in its directory:

```
/workspace/seo-{skill-name}/
├── SKILL.md              # Full skill specification
├── scripts/              # Python implementation
│   ├── main.py
│   └── ...
└── references/           # Schemas, guides, examples
    ├── {schema}.json
    └── ...
```

To view skill-specific details:
```bash
cat /workspace/seo-keyword-research/SKILL.md
cat /workspace/seo-content-flow/SKILL.md
```

---

## Features

### Content Generation
- ✓ Automatic keyword research with LSI discovery
- ✓ Search intent classification (informational/commercial/transactional)
- ✓ AI-powered article writing with natural keyword placement
- ✓ Automatic featured and section image generation
- ✓ SEO scoring (0-100) with actionable suggestions
- ✓ Internal link optimization using site sitemap
- ✓ Quality gates (halts if score < 70)

### CMS Support
- ✓ WordPress (primary platform)
- ✓ Shopify (e-commerce)
- ✓ Haravan (Vietnam e-commerce)
- ✓ Adapter pattern for easy extension

### Multilingual
- ✓ English (en)
- ✓ Vietnamese (vi)
- ✓ Automatic language detection
- ✓ Multilingual content generation

### Analytics & Auditing
- ✓ Technical SEO audit
- ✓ Competitor analysis
- ✓ SEO scoring engine
- ✓ Site crawling and issue detection

### Workflow Automation
- ✓ Full 6-step content pipeline
- ✓ Site audit workflow
- ✓ Batch multi-keyword processing
- ✓ Resume from any step

---

## Architecture Overview

The system follows a **layered, modular architecture**:

1. **Layer 1 (Utility):** Shared services (SERP scraper, CMS adapter, scorer, validators)
2. **Layer 2 (Core):** Specialized SEO skills (keyword research, content writing, optimization)
3. **Layer 3 (Orchestration):** ClawFlow workflows combining skills into end-to-end pipelines

Each component:
- Uses **stdlib-only Python** (no external dependencies)
- Has clear **I/O contracts** (JSON schemas)
- Implements **graceful degradation** (optional services fail without halting)
- Supports **multilingual content** (en/vi)
- Follows **consistent error handling** patterns

**See [Architecture](./seo-architecture.md) for detailed system design.**

---

## Performance Characteristics

| Metric | Value |
|--------|-------|
| **Full pipeline execution** | ~25 minutes |
| **Fastest step** | Outline generation (~1 minute) |
| **Slowest step** | Image generation (5-8 minutes) |
| **Memory per pipeline** | ~200MB |
| **Disk per article** | 10-50MB (including images) |
| **Network dependency** | High (requires APIs) |
| **Parallelizable steps** | Images + scoring initial phase |

---

## Security & Privacy

### Data Handling
- All scripts use **stdlib-only Python** (no third-party code execution)
- API credentials stored in environment variables (not in code)
- Output files contain markdown and JSON only (no binary artifacts except images)
- No data sent to unauthorized services

### API Credentials
- WordPress: Application passwords (not account passwords)
- Shopify: Limited-scope admin API tokens
- Haravan: Vendor API tokens
- Image generation: Provider-specific API keys

### Recommendations
- Use least-privilege API credentials
- Rotate credentials regularly
- Keep .env files out of version control
- Monitor API usage for anomalies

---

## Extension Points

### Adding New Skills
1. Create directory: `/workspace/seo-{skill-name}/`
2. Write SKILL.md specification
3. Implement scripts/ with stdlib-only Python
4. Add references/ with schemas
5. Update this documentation

### Adding CMS Support
1. Implement adapter in seo-cms-adapter/scripts/
2. Follow WordPressAdapter interface
3. Register in factory method
4. Update environment variable docs

### Adding Languages
1. Update language detection in seo-shared-utils
2. Add language-specific prompts in content generation skills
3. Test with multilingual validators
4. Document language code in docs

---

## Getting Help

### Issue Resolution Path
1. Check [Troubleshooting](./seo-troubleshooting.md) guide
2. Review skill-specific SKILL.md in skill directory
3. Check error messages in verbose output (`... 2>&1 | tee debug.log`)
4. Consult API provider documentation (WordPress, Shopify, image API)

### Validation Checklist
- [ ] All required env vars set and exported
- [ ] Internet connectivity verified
- [ ] WordPress REST API enabled (if using WordPress)
- [ ] API credentials valid (test manually)
- [ ] Python 3.7+ installed
- [ ] Sufficient disk space and memory

---

## Statistics

**Complete SEO Suite:**
- 16 total components (12 skills + 3 workflows + 1 utility)
- ~4,000+ lines of skill documentation (SKILL.md files)
- 100% stdlib-only Python (no external dependencies)
- Support for 2 languages (EN, VI)
- Support for 3 CMS platforms (WP, Shopify, Haravan)
- ~15 distinct data file types (JSON schemas)

---

## Recent Updates

**SEO Skills Suite v1.0 Complete:**
- All 12 core skills fully implemented
- 3 ClawFlow orchestration workflows
- Full multilingual support (English + Vietnamese)
- Multi-CMS support (WordPress, Shopify, Haravan)
- Comprehensive documentation and guides
- Quality gates and error handling throughout

---

## Navigation

**Start here based on your role:**

| Role | Start Here |
|------|-----------|
| **New User** | [Getting Started](./seo-getting-started.md) |
| **Content Creator** | [Workflow Overview](./seo-workflow.md) |
| **Developer/Integrator** | [Skills Reference](./seo-skills-reference.md) + [Architecture](./seo-architecture.md) |
| **Support/Troubleshooting** | [Troubleshooting](./seo-troubleshooting.md) |
| **System Design** | [Architecture](./seo-architecture.md) |

---

**Last Updated:** 2026-03-25
**Version:** 1.0 Complete
**Status:** Production Ready
