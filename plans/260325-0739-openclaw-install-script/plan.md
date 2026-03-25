---
name: OpenClaw SEO Skills Install Script
status: pending
created: 2026-03-25
---

# OpenClaw SEO Skills — Install Script

## Overview

Create `install.sh` and `uninstall.sh` to install/remove all SEO skills+workflows from this repo into the OpenClaw environment.

## Analysis

**Install methods (per OpenClaw docs):**
1. `clawhub install <slug>` — ClawHub registry (post-publish)
2. Manual: copy skill folder to `~/.openclaw/skills/` or project directory

**Target:** `${OPENCLAW_SKILLS_DIR:-$HOME/.openclaw/skills}`

**Components (16):**
- 12 skills: seo-keyword-research, seo-outline-generate, seo-content-write, seo-publish-cms, seo-scorer, seo-optimize-score, seo-image-generate, seo-serp-scraper, seo-technical-audit, seo-competitor-analyze, seo-aeo-optimize, seo-cms-adapter
- 3 workflows: seo-content-flow, seo-audit-flow, seo-batch-flow
- 1 shared lib: seo-shared-utils

**Install method:** Symlink by default (repo = source of truth). `--copy` for portable installs.

## Files to Create

| File | Purpose |
|------|---------|
| `install.sh` | Install all skills via symlink to ~/.openclaw/skills/ |
| `uninstall.sh` | Remove installed skills |

## Install Script Requirements

1. Auto-detect repo root (dirname of install.sh)
2. Target: `${OPENCLAW_SKILLS_DIR:-$HOME/.openclaw/skills}`
3. Create target dir if missing
4. For each `seo-*` dir with SKILL.md: symlink to target
5. Skip if already installed (idempotent)
6. `--copy` flag: copy instead of symlink
7. `--dry-run` flag: preview without action
8. Print summary: installed/skipped/errors

## Uninstall Script Requirements

1. Same target dir detection
2. Only remove symlinks pointing to this repo (safety)
3. `--force` flag: also remove copied installs
4. Print summary

## Success Criteria

- `./install.sh` installs all 16 components to OpenClaw
- `./uninstall.sh` cleanly removes them
- Idempotent, Linux + macOS compatible
