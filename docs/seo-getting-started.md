# Getting Started with SEO Skills

Complete setup and first-run guide for the SEO content automation suite.

## Prerequisites

- Python 3.7+ installed
- Internet connection (for web search and API calls)
- OpenClaw framework available (`openclaw` command)

## 1. Environment Setup

### Step 1a: WordPress Configuration

If publishing to WordPress, you need:
1. A WordPress site with REST API enabled
2. An Application Password created in WP Admin

```bash
# Create Application Password:
# 1. Go to WP Admin > Users > Your Profile
# 2. Scroll to "Application Passwords"
# 3. Create new password named "SEO Skills"
# 4. Copy the generated password

# Set environment variables
export WORDPRESS_URL="https://your-wordpress-site.com"
export WORDPRESS_TOKEN="your_username:your_app_password"

# Test connectivity
curl -X POST "${WORDPRESS_URL}/wp-json/wp/v2/posts" \
  -u "${WORDPRESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"title":"Test","status":"draft"}' | grep -q "Test" && echo "✓ WordPress connection OK"
```

### Step 1b: Image Generation API

Configure your AI image generation API:

```bash
# Example with OpenAI DALL-E
export IMAGE_GEN_API_KEY="sk-..."

# Or with other providers, set accordingly
# The skill will use your provider's API format
```

### Step 1c: Optional — SEMrush API

For enhanced keyword research (volume, difficulty data):

```bash
export SEMRUSH_API_KEY="your_semrush_api_key"
# If not set, skill falls back to web search only (slower but free)
```

### Step 1d: Verify Configuration

```bash
# Check all required env vars are set
echo "WORDPRESS_URL: ${WORDPRESS_URL}"
echo "WORDPRESS_TOKEN: ${WORDPRESS_TOKEN:0:10}***"
echo "IMAGE_GEN_API_KEY: ${IMAGE_GEN_API_KEY:0:10}***"
echo "SEMRUSH_API_KEY: ${SEMRUSH_API_KEY:0:10}***"
```

## 2. First Run: Complete Content Pipeline

Create your first article end-to-end:

```bash
cd ~/seo-test
mkdir -p article-001
cd article-001

# Run the full pipeline with a seed keyword
openclaw run seo-content-flow "best practices for remote team management"
```

### What Happens

1. **Keyword Research** (2-3 min)
   - Searches for variations, related terms, PAA questions
   - Classifies search intent
   - Creates `keyword_map.json`

2. **Outline Generation** (1 min)
   - Builds H1, H2, H3 structure
   - Sets meta title/description
   - Creates `outline.json`

3. **Content Writing** (3-4 min)
   - Generates full article in Markdown
   - Natural keyword placement
   - Creates `article.md`

4. **Image Generation** (5-8 min)
   - Creates featured image (1200×630px)
   - Creates section images (800×450px per heading)
   - Creates `image_map.json`

5. **Score Optimization** (2-3 min)
   - Evaluates article quality
   - Suggests improvements
   - Quality gate: halts if score < 70
   - Creates `optimized_article.md` and `score_report.json`

6. **Publishing** (1-2 min)
   - Requires your approval (shows summary)
   - Creates draft in WordPress
   - Returns `post_url` and `post_id`

### Expected Output

```
article-001/
├── keyword_map.json          # Primary keyword + LSI terms
├── outline.json              # Content structure
├── article.md                # Initial article draft
├── image_map.json            # Images with alt text
├── optimized_article.md      # Final optimized version
├── score_report.json         # SEO quality breakdown
└── publish_result.json       # WordPress post details
```

### Verify in WordPress

1. Go to WP Admin > Posts > Drafts
2. Find your new post
3. Review and publish when ready

## 3. Quick Workflows

### Generate English vs Vietnamese Content

```bash
# English (default)
openclaw run seo-content-flow "sustainable fashion brands"

# Vietnamese (auto-detected from diacritics)
openclaw run seo-content-flow "thương hiệu thời trang bền vững"

# Explicit language specification
export CONTENT_LANG=vi
openclaw run seo-content-flow "thương hiệu thời trang bền vững"
```

### Publish to Shopify Instead of WordPress

```bash
export CMS_TARGET=shopify
export SHOPIFY_STORE_URL="https://my-store.myshopify.com"
export SHOPIFY_ACCESS_TOKEN="shpat_1234567890abcdef..."
export SHOPIFY_BLOG_ID=123456789

openclaw run seo-content-flow "winter boots collection"
```

### Audit Your Website

```bash
openclaw run seo-audit-flow "https://your-wordpress-site.com"
# Output: audit_report.json with technical SEO issues
```

### Process Multiple Keywords

```bash
# Create keywords.json
cat > keywords.json << 'EOF'
[
  { "keyword": "best gaming laptop", "lang": "en" },
  { "keyword": "laptop chơi game tốt nhất", "lang": "vi" },
  { "keyword": "productivity laptops 2026", "lang": "en" }
]
EOF

openclaw run seo-batch-flow keywords.json
# Processes all keywords and publishes to WordPress
```

## 4. Resume from Failures

If a step fails, you can resume without re-running earlier steps:

```bash
# If content writing failed but research succeeded
openclaw run seo-content-flow --from write --input outline.json

# If optimization failed
openclaw run seo-content-flow --from optimize --input article.md

# Just publish without re-running everything
openclaw run seo-content-flow --from publish --input optimized_article.md

# After manually editing article
vi article.md  # Make changes
openclaw run seo-content-flow --from optimize --input article.md
```

## 5. Common Issues & Fixes

### Issue: "No search results found"

**Cause:** Seed keyword too specific or niche

**Fix:**
```bash
# Try broader keyword
openclaw run seo-content-flow "laptop"

# Not specific modifiers
openclaw run seo-content-flow "best laptops for students"
```

### Issue: "SEO Score < 70"

**Cause:** Article needs optimization

**Review suggestions:**
```bash
cat score_report.json | grep -A 5 "suggestions"
```

**Fix:**
```bash
# Edit article to address suggestions
vi optimized_article.md

# Re-run optimization
openclaw run seo-content-flow --from optimize --input optimized_article.md
```

### Issue: "IMAGE_GEN_API_KEY invalid or quota exceeded"

**Cause:** API key problem or rate limiting

**Fix:**
```bash
# Regenerate API key and re-set
export IMAGE_GEN_API_KEY="new_key_here"

# Resume without re-running write
openclaw run seo-content-flow --from images --input article.md
```

### Issue: "WordPress REST API not found (404)"

**Cause:** Permalinks not configured correctly

**Fix:**
1. Go to WP Admin > Settings > Permalinks
2. Change from "Plain" to "Post name" (or any non-plain option)
3. Click Save
4. Retry publish step

### Issue: "Cannot authenticate to WordPress (401)"

**Cause:** Invalid credentials

**Fix:**
```bash
# Regenerate Application Password in WP Admin > Users > Your Profile
# Copy the new password
export WORDPRESS_TOKEN="username:new_password_here"

# Retry publish step
openclaw run seo-content-flow --from publish --input optimized_article.md
```

## 6. Best Practices

### Keyword Selection
- Start with 1-2 word keywords (easier to research)
- Avoid extremely niche topics (may return 0 results)
- Use questions for long-tail keywords ("how to X", "best X for Y")

### Content Review
- Always review generated content before publishing
- Check article.md for natural keyword placement
- Verify images are contextually appropriate
- Review score_report.json suggestions before step 6

### Publishing
- Always create as draft first (never auto-published)
- Review in WordPress before final publication
- Test links and internal references
- Check featured image is properly attached

### Multilingual Content
- Use diacritics in Vietnamese keywords (auto-detects)
- Or explicitly set `CONTENT_LANG=vi`
- Output respects language in YAML frontmatter
- All skills maintain language consistency

### Batch Processing
- Start with 2-3 keywords to test
- Monitor disk space (images take storage)
- Spread batch runs during off-peak hours
- Resume failed keyword without re-running entire batch

## 7. Monitoring & Logging

### View Intermediate Outputs

```bash
# Check research results
cat keyword_map.json | jq '.primary_keyword, .search_intent, .lsi_keywords'

# Check outline
cat outline.json | jq '.h1_title, .meta_title, .headings'

# Check scoring
cat score_report.json | jq '.overall_score, .breakdown'
```

### Debug Failed Steps

Each step produces stderr logs:
```bash
# Run with verbose output
openclaw run seo-content-flow "keyword" 2>&1 | tee run.log

# View error details
grep -i error run.log
```

## 8. Performance Tips

### Faster Execution
- Enable SEMrush API (skips slower web search parsing)
- Pre-prepare keywords for batch runs
- Use faster image API (some providers are quicker)

### Parallel Processing
- `seo-image-generate` runs in parallel with `seo-optimize-score`
- You can process multiple keywords simultaneously in separate terminals
- Each run uses separate output directory to avoid conflicts

### Resource Requirements
- CPU: Minimal (mostly API waits)
- Memory: ~200MB per pipeline instance
- Network: Required throughout
- Disk: ~10-50MB per article (including images)

## 9. Next Steps

After your first successful run:

1. **Review output quality** — Check article and images in WordPress
2. **Tweak parameters** — Try different keywords, languages, platforms
3. **Scale up** — Use batch-flow to process 5-10 keywords
4. **Integrate** — Use seo-audit-flow on your site periodically
5. **Extend** — Add custom skills if needed

## 10. Reference Docs

- **Full architecture:** [seo-architecture.md](./seo-architecture.md)
- **Skill details:** [seo-skills-reference.md](./seo-skills-reference.md)
- **Workflow overview:** [seo-workflow.md](./seo-workflow.md)
- **Individual skills:** See SKILL.md in each skill directory

## Support

For issues:
1. Check troubleshooting section above
2. Review skill-specific docs (SKILL.md in each directory)
3. Check score_report.json and audit_report.json for specific issues
4. Review run.log from verbose execution

---

**Ready to create your first SEO article?**

```bash
openclaw run seo-content-flow "your-keyword-here"
```

Good luck!
