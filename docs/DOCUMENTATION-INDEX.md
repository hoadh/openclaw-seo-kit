# Documentation Index & Quick Reference

**Last Updated:** 2026-03-25
**Total Docs:** 6 comprehensive markdown files (2,596 lines)
**Total Size:** 76 KB

---

## Files at a Glance

| # | File | Lines | Purpose | Audience |
|---|------|-------|---------|----------|
| 1 | **README.md** | 451 | Central navigation hub | Everyone |
| 2 | **seo-getting-started.md** | 380 | Setup & first run | New users, DevOps |
| 3 | **seo-workflow.md** | 183 | Pipeline overview | All users |
| 4 | **seo-skills-reference.md** | 536 | Input/output reference | Developers |
| 5 | **seo-architecture.md** | 343 | System design | Architects |
| 6 | **seo-troubleshooting.md** | 703 | Issue resolution | Support |

---

## Start Here Based on Your Role

### 👤 I'm New to SEO Skills
**Path:** README.md → seo-getting-started.md → seo-workflow.md
- Read overview in README
- Follow setup in getting-started
- See examples in workflow overview

### 👨‍💼 I Want to Create Content Now
**Path:** seo-workflow.md → seo-getting-started.md (env setup section)
- Learn the 6-step pipeline
- Setup environment variables
- Run your first keyword

### 👨‍💻 I'm Integrating into Code
**Path:** seo-skills-reference.md → seo-architecture.md
- Review input/output contracts
- Understand dependencies
- Check integration patterns

### 🔧 Something's Not Working
**Path:** seo-troubleshooting.md
- Find your step (1-6)
- Follow diagnosis steps
- Apply solution

### 🏗️ I'm Building a New Skill
**Path:** seo-architecture.md → individual skill SKILL.md files
- Review system design
- Check integration points
- Follow patterns from existing skills

---

## What Each File Contains

### README.md (451 lines)
**Navigation hub for all documentation**

Contains:
- Quick start in 3 steps
- All 16 components overview table
- Environment variables summary
- Common workflows (5 scenarios)
- Data flow diagram
- Feature checklist
- Statistics and version info

**Use when:** You need an overview or quick navigation

---

### seo-getting-started.md (380 lines)
**Complete setup and first-run guide**

Contains:
- Prerequisites checklist
- Step-by-step environment setup
  - WordPress configuration
  - Image API setup
  - SEMrush optional setup
- First run walkthrough (6-step pipeline)
- Expected outputs
- Verification in WordPress
- Quick workflows (EN/VI/Shopify examples)
- Common issues & fixes
- Performance tips
- Next steps

**Use when:** Setting up the suite for first time

---

### seo-workflow.md (183 lines)
**High-level pipeline overview and examples**

Contains:
- 6-step content pipeline table with timings
- How to run full pipeline
- Resume from any step
- Multilingual examples (EN/VI)
- Multi-CMS examples (WordPress/Shopify/Haravan)
- Additional workflows (audit, batch)
- Data flow diagram
- Key features summary
- Output files reference
- Troubleshooting reference
- Links to detailed docs

**Use when:** Understanding the workflows or seeing examples

---

### seo-skills-reference.md (536 lines)
**Complete reference for all 16 skills**

Contains:
- Utility services (4) overview table
- Core skills (9) detailed specs
  - Input/output contracts
  - Environment variables
  - Dependencies
  - Execution times
  - Quality gates
  - Error handling
- Workflows (3) specs
- Quick-start scenarios (5 examples)
- Output file locations
- Error recovery table
- Dependency graph
- Multilingual support matrix
- Integration checklist

**Use when:** Building integrations or need exact input/output format

---

### seo-architecture.md (343 lines)
**System design and architectural patterns**

Contains:
- Overview of 3-layer architecture
- Architecture diagram (visual)
- Complete data flow chain
- Layer 1 (Utility) detailed descriptions
- Layer 2 (Core Skills) detailed descriptions
- Layer 3 (Orchestration) detailed descriptions
- Environment variables per layer
- File structure for each skill
- Language support summary
- Error handling strategy
- Integration points
- How to add new skills
- How to add new workflows
- How to add CMS support

**Use when:** Extending the system or understanding design decisions

---

### seo-troubleshooting.md (703 lines)
**Comprehensive issue diagnosis and resolution**

Contains:
- Step-by-step issues (Steps 1-6)
  - Symptoms
  - Causes
  - Solutions with code examples
- Workflow-level issues (resume, batch)
- Environment/config issues
- Performance optimization tips
- Quick diagnostic checklist
- Support resources

**Coverage:**
- 60+ specific issue scenarios
- Per-step procedures
- CMS-specific troubleshooting
- Resume procedures
- Error recovery strategies

**Use when:** Something fails or behaves unexpectedly

---

## Quick Reference Tables

### 16 Components at a Glance

| Layer | Component | Type | Input | Output |
|-------|-----------|------|-------|--------|
| 1 | seo-serp-scraper | Utility | Query | Results array |
| 1 | seo-cms-adapter | Utility | CMS_TARGET | Adapter instance |
| 1 | seo-scorer | Utility | article.md | Score report |
| 1 | seo-shared-utils | Utility | Various | Various |
| 2 | seo-keyword-research | Skill | Keyword | keyword_map.json |
| 2 | seo-outline-generate | Skill | keyword_map | outline.json |
| 2 | seo-content-write | Skill | outline | article.md |
| 2 | seo-image-generate | Skill | article.md | image_map.json |
| 2 | seo-optimize-score | Skill | article.md | optimized_article.md |
| 2 | seo-publish-cms | Skill | article.md | post_url, post_id |
| 2 | seo-technical-audit | Skill | website_url | audit_report.json |
| 2 | seo-competitor-analyze | Skill | keyword | report.json |
| 2 | seo-aeo-optimize | Skill | article.md | enhanced_content |
| 3 | seo-content-flow | Workflow | Keyword | Published URL |
| 3 | seo-audit-flow | Workflow | Site URL | Audit report |
| 3 | seo-batch-flow | Workflow | Keywords.json | Batch results |

### Essential Environment Variables

**Required:**
```bash
WORDPRESS_URL              # WordPress site URL
WORDPRESS_TOKEN            # username:app_password
IMAGE_GEN_API_KEY         # AI image generation API key
```

**Optional:**
```bash
SEMRUSH_API_KEY           # For enhanced keyword research
CONTENT_LANG              # "en" (default) or "vi"
CMS_TARGET                # "wordpress" (default), "shopify", "haravan"
```

**CMS-Specific (if using Shopify/Haravan):**
```bash
SHOPIFY_STORE_URL
SHOPIFY_ACCESS_TOKEN
SHOPIFY_BLOG_ID
HARAVAN_STORE_URL
HARAVAN_ACCESS_TOKEN
HARAVAN_BLOG_ID
```

### 6-Step Content Pipeline

| Step | Skill | Input | Output | Time |
|------|-------|-------|--------|------|
| 1 | seo-keyword-research | Keyword | keyword_map.json | 2-3 min |
| 2 | seo-outline-generate | keyword_map | outline.json | 1 min |
| 3 | seo-content-write | outline | article.md | 3-4 min |
| 4 | seo-image-generate | article | image_map.json | 5-8 min |
| 5 | seo-optimize-score | article | optimized_article | 2-3 min |
| 6 | seo-publish-cms | article | post_url | 1-2 min |
| **Total** | — | — | **Published Draft** | **~25 min** |

---

## Common Commands

### Setup
```bash
export WORDPRESS_URL="https://your-site.com"
export WORDPRESS_TOKEN="user:password"
export IMAGE_GEN_API_KEY="key"
```

### Generate Article
```bash
openclaw run seo-content-flow "keyword"
```

### Generate Vietnamese
```bash
export CONTENT_LANG=vi
openclaw run seo-content-flow "từ khóa"
```

### Publish to Shopify
```bash
export CMS_TARGET=shopify
export SHOPIFY_STORE_URL="https://store.myshopify.com"
export SHOPIFY_ACCESS_TOKEN="token"
openclaw run seo-content-flow "keyword"
```

### Audit Website
```bash
openclaw run seo-audit-flow "https://your-site.com"
```

### Resume from Step 5
```bash
openclaw run seo-content-flow --from optimize --input article.md
```

---

## Troubleshooting Quick Flowchart

```
Something failed?
├─ Which step?
│  ├─ Step 1-6? → See seo-troubleshooting.md [Step 1-6]
│  └─ Workflow? → See seo-troubleshooting.md [Workflow Issues]
│
├─ Environment problem?
│  └─ See seo-troubleshooting.md [Env & Config]
│
├─ Need help again?
│  └─ See seo-troubleshooting.md [Support Resources]
│
└─ Use diagnostic checklist at end of seo-troubleshooting.md
```

---

## Documentation Organization

```
/workspace/docs/
│
├── README.md ◄────────────── START HERE (navigation hub)
│
├── seo-getting-started.md ◄─── For setup
├── seo-workflow.md ◄─────────── For pipeline overview
├── seo-skills-reference.md ◄── For API/integration details
├── seo-architecture.md ◄────── For system design
├── seo-troubleshooting.md ◄──── For problem-solving
│
└── DOCUMENTATION-INDEX.md ◄── This file (quick reference)

Individual Skills (external):
├── /workspace/seo-keyword-research/SKILL.md
├── /workspace/seo-content-flow/SKILL.md
└── ... (14 more in /workspace/seo-*/SKILL.md)
```

---

## Learning Paths

### Path 1: Quick Start (15 minutes)
1. README.md (overview section) — 2 min
2. seo-getting-started.md (setup section) — 5 min
3. seo-workflow.md (6-step pipeline) — 3 min
4. Run first example — 5 min

### Path 2: Full Understanding (1 hour)
1. README.md (full) — 15 min
2. seo-getting-started.md (full) — 20 min
3. seo-workflow.md (full) — 10 min
4. seo-troubleshooting.md (diagnostic checklist) — 15 min

### Path 3: Deep Dive (3 hours)
1. README.md (full) — 15 min
2. seo-architecture.md (full) — 30 min
3. seo-skills-reference.md (full) — 45 min
4. Individual skill SKILL.md files — 60 min
5. seo-troubleshooting.md (full) — 30 min

### Path 4: Support & Troubleshooting (variable)
1. seo-troubleshooting.md (find your issue) — 5-10 min
2. Follow issue-specific solution — 5-30 min
3. Check diagnostic checklist — 5 min

---

## Features Covered in Docs

### Content Generation ✓
- Automatic keyword research
- LSI keyword discovery
- Search intent classification
- Article writing with natural keyword placement
- Image generation (featured + sections)
- SEO scoring (0-100)
- Quality gates (score ≥ 70)
- Internal link optimization

### Platforms ✓
- WordPress (primary)
- Shopify (e-commerce)
- Haravan (Vietnam e-commerce)
- Extensible adapter pattern

### Languages ✓
- English (en)
- Vietnamese (vi)
- Auto-detection
- Language-aware validation

### Workflows ✓
- Full 6-step content pipeline
- Site audit workflow
- Batch multi-keyword processing
- Resume from any step

### Error Handling ✓
- Graceful degradation
- Clear error messages
- Recovery procedures
- Quality gates
- Troubleshooting guide (60+ scenarios)

---

## How to Use This Index

**Bookmark this file** — It's your map to all other documentation

**When you need...**
- **Orientation:** Start with README.md
- **Setup help:** Go to seo-getting-started.md
- **API details:** Consult seo-skills-reference.md
- **System design:** Review seo-architecture.md
- **Problem solving:** Check seo-troubleshooting.md
- **Pipeline overview:** Read seo-workflow.md
- **This reference:** You're reading it now!

---

## Version & Status

- **Documentation Version:** 1.0 Complete
- **SKU Suite Version:** 1.0 Complete
- **Total Components:** 16 (12 skills + 3 workflows + 1 utility)
- **Documentation Lines:** 2,596
- **Last Updated:** 2026-03-25
- **Status:** Production Ready

---

## Quick Links

- [Central Hub](./README.md)
- [Getting Started](./seo-getting-started.md)
- [Workflow Overview](./seo-workflow.md)
- [Skills Reference](./seo-skills-reference.md)
- [Architecture](./seo-architecture.md)
- [Troubleshooting](./seo-troubleshooting.md)

---

**Questions?** Check [Troubleshooting](./seo-troubleshooting.md) → Support Resources section
