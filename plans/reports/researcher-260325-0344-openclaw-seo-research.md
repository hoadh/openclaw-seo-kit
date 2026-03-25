# OpenClaw Platform Research Report
**Date:** 2026-03-25
**Researcher:** Agent
**Focus:** OpenClaw architecture, skill structure, workflows, and SEO capabilities

---

## Executive Summary

OpenClaw is a self-hosted AI agent gateway connecting messaging apps to AI models (Claude, GPT-4o, etc.), enabling autonomous task execution. The platform uses a two-tier system:
- **Tools** = low-level capabilities (read, write, exec, web_fetch)
- **Skills** = high-level workflows combining tools (Markdown files with YAML metadata + instructions)

For SEO/content work, OpenClaw offers mature community skills including AEO (Answer Engine Optimization) capabilities, competitive intelligence, and content gap analysis. The platform supports distributing skills via ClawHub (public registry) or privately.

---

## What is OpenClaw?

### Platform Overview
OpenClaw is an **open-source AI automation framework** that provides:
- **Gateway layer**: Routes messaging channels (WhatsApp, Telegram, Discord, iMessage) to AI agents
- **Multi-interface access**: Web UI, CLI, macOS app, mobile nodes (iOS/Android)
- **Self-hosted architecture**: Full data control—runs on your infrastructure
- **Session management**: Isolated sessions per agent, workspace, or sender
- **Multi-agent routing**: Support for multiple AI agents with specialized capabilities

Target users: Developers and power users seeking personal AI assistants without vendor lock-in or data sharing constraints.

### Architecture Layers

```
Input Layer → Gateway (Session/Routing) → Output Layer → Auxiliary
  ↓              ↓                           ↓              ↓
Messaging    Gateway Core            AI Agents        Mobile Nodes
(WhatsApp,   Process                 Web UI            (iOS/Android)
Telegram,    ~.openclaw/             CLI
Discord)     openclaw.json            macOS App
```

### Configuration
- **Location**: `~/.openclaw/openclaw.json`
- **Approach**: Bundled defaults + JSON overrides
- **Customization**: Channel allowlists, group mention rules, routing policies
- **No required setup**: Works out-of-the-box with defaults

---

## Tools vs Skills: Critical Distinction

### Tools (Low-Level Capabilities)
Tools = **permissions** granted to the agent. They provide actual access to system resources.

**Built-in Tools:**
- **High-risk** (enable selectively): `exec`, `database`, `email`
- **Medium-risk** (enable as needed): `write`, `github`, `slack`
- **Low-risk** (safe by default): `read`, `list`, `search`, `web_search`, `web_fetch`, `memory`

**Key insight**: Installing a skill does NOT grant new permissions. The skill teaches workflows, but the tool must be enabled separately.

Example: Obsidian skill teaches note organization, but without the `write` tool enabled, it cannot write files.

### Skills (High-Level Workflows)
Skills = **textbooks** teaching agents how to combine tools to accomplish tasks.

**Characteristics:**
- Markdown files containing instructions + YAML metadata
- Direct agent interaction (agent reads and follows instructions)
- Reusable, composable, versioned
- Can trigger other skills or tools
- Range from simple (slash command) to complex (multi-step workflows with approval gates)

**Examples:**
- Format/reformat code slash command
- Multi-step PR review + Jira comment workflow
- Jupyter notebook → Word doc converter with image/table handling

---

## Skill Structure & Format

### Directory Layout
```
my-skill/
├── SKILL.md                 # Required: instructions + metadata
├── scripts/                 # Optional: executable code
│   ├── init_skill.py
│   └── process_data.py
├── references/              # Optional: domain knowledge
│   ├── schema.json
│   └── best-practices.md
└── assets/                  # Optional: templates, icons (not loaded into context)
    ├── output-template.html
    └── icon.svg
```

### SKILL.md Format

#### Structure
```markdown
---
name: skill-name
description: One-line summary for triggering (agent reads this to decide relevance)
metadata:
  openclaw:
    requires:
      env:
        - ENV_VAR_1
        - ENV_VAR_2
      bins:
        - cli-tool-name
      anyBins:
        - alternative-tool-1
        - alternative-tool-2
      config:
        - ~/.config/myapp/config.yaml
    primaryEnv: ENV_VAR_1
version: "1.0.0"
author: username
license: MIT-0
---

# Instructions

## Context
[Who the agent is, what constraints apply]

## Numbered Steps
1. [Specific, deterministic action]
2. [Action with error handling]
3. [Clear stop condition]

## Error Handling
[What to do when X fails]

## Rules
[What never to do]

## Output Format
[Expected structure of response]
```

#### YAML Metadata Fields

| Field | Type | Purpose | Example |
|-------|------|---------|---------|
| `name` | string | Unique identifier (lowercase, hyphens only) | `analyze-content-gaps` |
| `description` | string | Triggering signal (agent uses this to decide if skill applies) | "Identify content gaps vs competitors for target keywords" |
| `version` | string | Semver versioning | `1.0.0` |
| `author` | string | Creator identity | `username` |
| `license` | string | Always MIT-0 for ClawHub | `MIT-0` |
| `metadata.openclaw.requires.env` | string[] | Environment variables needed | `["SEMRUSH_API_KEY"]` |
| `metadata.openclaw.requires.bins` | string[] | All required CLI binaries | `["curl", "jq"]` |
| `metadata.openclaw.requires.anyBins` | string[] | At least one must exist | `["python", "python3"]` |
| `metadata.openclaw.requires.config` | string[] | Config files the skill reads | `["~/.aws/config"]` |
| `metadata.openclaw.primaryEnv` | string | Main credential env var (maps to `skills.entries.<name>.apiKey`) | `SEMRUSH_API_KEY` |

### Critical Design Principles

**1. Description Quality is Load-Bearing**
- OpenClaw loads only name + description to decide skill relevance
- Full instructions load AFTER triggering
- Weak descriptions = skill never selected for relevant tasks
- Should include "when to use" signals

**2. Conciseness Matters**
- Context window is a shared resource
- Challenge every paragraph's token cost
- Keep SKILL.md under 500 lines

**3. Appropriate Freedom Levels**
- **High freedom**: Text guidance when multiple approaches valid
- **Medium freedom**: Pseudocode with configurable parameters
- **Low freedom**: Specific scripts for fragile operations

**4. Instruction Format**
- Use **numbered steps**, not prose
- Agents follow numbered steps reliably
- Separate concerns into sections:
  - Context (agent role)
  - Instructions (deterministic steps)
  - Error Handling (failure modes)
  - Rules (hard constraints)
  - Output Format (response structure)

**5. No Duplication**
- Information in SKILL.md OR references, never both
- SKILL.md = essential procedures
- References = detailed schemas, examples, knowledge

### Skill Creation Workflow

**Step 1: Understand Requirements**
- Gather concrete use cases
- Clarify functionality, triggers, workflows
- Identify reusable patterns

**Step 2: Plan Reusable Resources**
- Identify scripts for repetitive tasks
- Plan reference files for domain knowledge
- Design asset templates

**Step 3: Initialize Structure**
```bash
python3 scripts/init_skill.py <skill-name> --path <directory>
```

**Step 4: Develop & Test**
- Implement scripts with error handling
- Create reference documentation
- Write SKILL.md with clear triggers
- Test in real scenarios

**Step 5: Package**
```bash
python3 scripts/package_skill.py <path/to/skill-folder>
```
Creates `.skill` file (compressed format)

**Step 6: Iterate**
- Test with users
- Refine instructions
- Improve error handling
- Repeat

### Naming Conventions
- Lowercase, hyphens only
- Under 64 characters
- Imperative phrasing: `rotate-pdf`, `edit-docx`, `analyze-sentiment`
- Avoid: README.md, changelogs, installation guides

### What NOT to Include
- Markdown READMEs (agent doesn't read these)
- Installation guides
- Changelogs
- Auxiliary documentation
- Attribution requirements (MIT-0 = no attribution needed)

---

## Workflows & Automation

### ClawFlows: Multi-Step Automation

ClawFlows enable chaining skills into multi-step workflows with dependencies and conditional execution.

#### YAML Workflow Structure
```yaml
name: content-analysis-pipeline
description: Analyze content gaps and generate brief

workflows:
  - name: analyze-competitors
    skill: analyze-serp-rankings
    env:
      SEMRUSH_API_KEY: ${SEMRUSH_API_KEY}
    delay: 0

  - name: extract-gaps
    skill: extract-content-gaps
    dependsOn: analyze-competitors
    env:
      INPUT: ${analyze-competitors.output}
    delay: 5

  - name: generate-brief
    skill: create-content-brief
    dependsOn: extract-gaps
```

#### Workflow Features
- **Sequential execution**: Steps run in order with optional delays
- **Artifact passing**: `${workflow-name.output}` passes outputs to next step
- **Environment variables**: Accessible via `CLAWFLOW_INPUT` and workflow env
- **Output storage**: `~/.openclaw/output/<workflow-name>-<date>.<format>`
- **Conditional steps**: `condition` field for branching
- **Approval gates**: `approval` field for manual review between steps

#### Natural Language Workflow Creation
- Tell ClawFlows agent what to automate in English
- Agent generates YAML workflow definition
- Creates pull request for review
- Deploy after approval

### Lobster: Declarative Pipeline Definition

YAML-based pipeline runner with fields:
- `name`: Pipeline identifier
- `args`: Input parameters
- `steps`: Task definitions
- `env`: Environment variables
- `condition`: Execution conditions
- `approval`: Manual approval requirement

---

## OpenClaw SEO/AEO Ecosystem

### Answer Engine Optimization (AEO) Context
Traditional SEO targets Google blue links. **AEO targets AI-generated answers** from:
- Google AI Overviews
- ChatGPT Search
- Perplexity
- Claude
- Other AI-powered search platforms

AEO strategies differ from SEO: citation patterns, answer quality, topical authority matter more than keyword density.

### Existing Community Skills

#### 1. **aeo-analytics-free**
- **Purpose**: Measure AI visibility for your brand
- **Tracks**: Brand mentions and citations across AI assistants
- **Output**: Competitive position in AI-generated answers
- **API**: Free tier available

#### 2. **aeo-content-free**
- **Purpose**: Optimize content for AI assistants (Gemini, ChatGPT)
- **Approach**: Analyzes what AI assistants are citing
- **Output**: Content optimization recommendations
- **Cost**: Free

#### 3. **aeo-prompt-frequency-analyzer**
- **Purpose**: Analyze Gemini search query patterns
- **Tracks**: Prompts that trigger AI assistant answers
- **Output**: Prompt frequency + opportunity identification
- **Cost**: Free

#### 4. **aeo-prompt-research-free**
- **Purpose**: Discover high-impact prompts and topics
- **Approach**: Community research + prompt mining
- **Output**: Topic prioritization for AEO
- **Cost**: Free

#### 5. **programmatic-seo** (in OpenClaw Directory)
- **Purpose**: Generate content pages programmatically
- **Capabilities**:
  - Generate pages with AI
  - Analyze competitor sitemaps
  - Serve via REST API for any CMS
- **Use case**: Scale SEO with programmatic content generation

#### 6. **OpenClaw SEO/AEO Skill Pack** (jrr996shujin-png/openclaw-seo-aeo-skills)

##### aeo-content-strategy
- **Purpose**: Mine long-tail content opportunities
- **Source**: Reddit + Quora community discussions
- **Process**:
  1. Scan Reddit/Quora for niche discussions
  2. Analyze signals (upvotes, comments, frequency)
  3. Extract 40-50 long-tail questions
  4. Prioritize by opportunity
  5. Generate editorial calendar
- **Config**: No API keys (uses OpenClaw web browsing)
- **Output**: Actionable content roadmap

##### seo-aeo-diagnostics
- **Purpose**: Comprehensive website health audit
- **Modules** (100-point scale):
  1. Technical foundation (crawlability, indexability)
  2. Search accessibility (robots.txt, sitemap, structured data discoverability)
  3. Structured data (schema completeness, validity)
  4. Content structure (heading hierarchy, readability, keyword signals)
  5. Multimedia accessibility (image alt text, video transcripts)
  6. Content quality signals (freshness, uniqueness, authority)
  7. Site architecture (navigation, internal linking, site structure)
- **Config**: No API keys
- **Output**: Scored health report + actionable fixes

##### seo-competitive-intel
- **Purpose**: Ongoing competitive monitoring + reporting
- **Components**:
  - Keyword ranking tracker (4 category types)
  - Content performance monitor
  - Competitor content scanner
- **Config**: Requires SEMrush API key + Google Search Console/Analytics OAuth
- **Output**:
  - React interactive dashboard (5 data tabs)
  - Monthly automation reports
  - Action recommendations with priority scores

### Skill Installation
Two methods:
1. **ClawHub CLI**: `clawhub install <skill-slug>`
2. **Manual**: Copy skill folder to `~/.openclaw/skills/` or project directory

### Community Repository Stats
- **OpenClaw awesome-skills**: 5,211 curated skills (filtered from 13,729 total)
- **OpenClaw Directory**: 3,439 skills across 12 categories
- **ClawHub**: Growing marketplace with versioning + rollback support
- **Automation category**: 579 skills
- **Productivity category**: 535 skills
- **Web Search category**: Major subcategory for research skills

---

## ClawHub: Skill Publishing Platform

### Publishing Requirements

#### Account Prerequisites
- GitHub account at least **1 week old**
- Verified email on GitHub

#### Metadata Requirements
All required fields in SKILL.md frontmatter:
```yaml
name: unique-skill-name
description: One-line description
metadata:
  openclaw:
    requires:
      env: [list of env vars]
      bins: [CLI tools required]
      anyBins: [alternatives—at least one required]
      config: [config files read]
    primaryEnv: ENV_VAR_NAME
version: "X.Y.Z"
author: github-username
license: MIT-0
```

#### Security & Code Analysis

ClawHub performs **security analysis** against declared metadata:

**Hard Fails:**
- Unpinned version dependencies (must pin all versions)
- Pipe-to-interpreter patterns (`curl | bash`, `curl | python`)
- Metadata mismatches (code uses undeclared env vars or bins)

**Best Practices:**
- Store credentials in OpenClaw runtime environment (not hardcoded)
- Declare exact environment variable names
- Include error handling for missing dependencies
- Document required setup steps in SKILL.md

#### File Type Restrictions
Only "text-based" files accepted:
- `text/*` MIME types
- Allowlist: JSON, YAML, TOML, JS, TS, Markdown, SVG
- Binary files must be in `assets/` (not loaded into context)

#### Versioning & Rollback
- Each publish creates new semver SkillVersion
- Tags point to versions (e.g., `latest`)
- Moving tags enables rollback to previous versions
- Changelogs optional (can be empty for sync operations)

### 13-Point ClawHub Publishing Checklist

1. **Name**: Lowercase, hyphens only, under 64 chars, imperative tone
2. **Description**: Include "when to use" signals (agent uses this for triggering)
3. **Metadata.openclaw.requires.env**: List all env vars skill references
4. **Metadata.openclaw.requires.bins**: Exact names of required CLI tools
5. **Metadata.openclaw.requires.anyBins**: Alternative tool names (at least one required)
6. **Version**: Semver format (X.Y.Z)
7. **Author**: GitHub username
8. **License**: Always MIT-0
9. **SKILL.md length**: Keep under 500 lines (resources load separately)
10. **Instructions**: Numbered steps (not prose), clear stop conditions
11. **Error Handling**: Document failure modes and recovery
12. **Dependencies**: Pin every version (no floating versions)
13. **Security**: No pipe-to-interpreter patterns, credentials in env

---

## Best Practices Summary

### Skill Design
- ✅ Keep descriptions focused on triggering signals ("when to use")
- ✅ Use numbered steps for procedural instructions
- ✅ Separate concerns (Context, Instructions, Error Handling, Rules, Output)
- ✅ Move detailed schemas/examples to reference files
- ✅ Design for composability (skills calling other skills)
- ✅ Include error handling and recovery procedures
- ✅ Test with real agents in real scenarios
- ❌ Avoid marketing copy in descriptions
- ❌ Don't duplicate info between SKILL.md and references
- ❌ Don't include installation guides or READMEs

### Publishing & Security
- ✅ Declare all dependencies (env vars, bins, configs)
- ✅ Pin all versions exactly
- ✅ Store credentials in OpenClaw runtime env
- ✅ Use security-hardened scripts
- ✅ Include comprehensive error handling
- ❌ No pipe-to-interpreter patterns
- ❌ No hardcoded secrets
- ❌ No unpinned versions

### Workflow Design
- ✅ Use YAML for multi-step automation
- ✅ Add delays between dependent steps
- ✅ Pass artifacts between workflows via env vars
- ✅ Include approval gates for critical steps
- ✅ Version control workflow definitions
- ❌ Don't create monolithic workflows (compose with skills)

---

## Technology Stack & Ecosystem

### Core Dependencies
- **AI Models**: Claude, GPT-4o, Pi, others
- **Messaging**: WhatsApp, Telegram, Discord, iMessage
- **Package Manager**: npm/pnpm/bun for skill distribution
- **Scripting**: Python (common for utility scripts)
- **Configuration**: JSON/YAML formats

### Community Infrastructure
- **ClawHub**: Official skill registry + marketplace
- **OpenClaw Directory** (openclawdir.com): Alternative skill directory
- **GitHub**: Primary distribution + version control
- **awesome-openclaw-skills**: 5,200+ curated, categorized skills

### Key Integrations
- **Google Search Console**: For ranking monitoring
- **Google Analytics**: For traffic analysis
- **SEMrush API**: For competitive intelligence
- **Reddit/Quora APIs**: For community discussion mining

---

## Limitations & Open Questions

### Unresolved Questions
1. **Skill licensing**: Can non-MIT-0 licenses be used for private skills? ClawHub requires MIT-0 but does this apply to private registries?
2. **Skill versioning**: How does OpenClaw handle version conflicts when multiple skills require different versions of the same tool?
3. **Workflow state**: Do ClawFlows maintain state across interruptions, or do they restart on resume?
4. **Tool permission granularity**: Can tool permissions be scoped (e.g., write to specific directories only)?
5. **Skill composition**: Can nested skill calls exceed reasonable recursion depths? Are there guard rails?
6. **AEO monitoring**: Which AI assistants do the AEO analytics skills actually track? Is coverage changing?
7. **Custom tools**: Can users create custom tools, or are only the built-in tools available?
8. **Team/org support**: Does OpenClaw support team workspaces with shared skills and permissions?

### Known Limitations
- **ClawHub governance**: Limited anti-spam/anti-malware filtering (relies on security analysis)
- **Skill discoverability**: No sophisticated recommendation engine (browse/search only)
- **Workflow debugging**: Limited visibility into workflow execution state
- **Tool granularity**: Some tools (like `exec`) are all-or-nothing permissions
- **Mobile node capabilities**: Limited context on iOS/Android node feature parity with desktop

---

## Recommendations

### For OpenClaw SEO Skill Development
1. **Use existing AEO foundations**: Build on `aeo-content-strategy` and `seo-aeo-diagnostics` patterns
2. **Prioritize descriptions**: Invest in clear "when to use" signals for discoverability
3. **Modularize**: Design skills as composable building blocks, not monoliths
4. **Document APIs**: If creating workflow orchestrators, clearly document skill output contracts
5. **Test with real agents**: Validate skill instructions with actual OpenClaw agents
6. **Plan for evolution**: Design metadata to handle future tool additions (use `anyBins`)
7. **Community first**: Consider publishing to ClawHub early (even 0.1.0 versions) to get feedback

---

## Sources

- [OpenClaw Documentation - Skills](https://docs.openclaw.ai/tools/skills)
- [ClawHub Skill Format Specification](https://github.com/openclaw/clawhub/blob/main/docs/skill-format.md)
- [OpenClaw Skill Creator Guide](https://github.com/openclaw/openclaw/blob/main/skills/skill-creator/SKILL.md)
- [VoltAgent Awesome OpenClaw Skills](https://github.com/VoltAgent/awesome-openclaw-skills)
- [OpenClaw SEO/AEO Skill Pack](https://github.com/jrr996shujin-png/openclaw-seo-aeo-skills)
- [ClawHub Publishing Checklist](https://gist.github.com/adhishthite/0db995ecfe2f23e09d0b2d418491982c)
- [OpenClaw Environment Variables Documentation](https://docs.openclaw.ai/help/environment)
- [Digital Ocean: What are OpenClaw Skills?](https://www.digitalocean.com/resources/articles/what-are-openclaw-skills)
- [DataCamp: Building Custom OpenClaw Skills](https://www.datacamp.com/tutorial/building-open-claw-skills)
- [OpenClaw Directory](https://openclawdir.com)
- [ClawHub Marketplace](https://clawhub.ai/)
