# SEO Skills Troubleshooting Guide

Comprehensive troubleshooting for common issues across the SEO skill suite.

## Step-by-Step Issues

### Step 1: Keyword Research (seo-keyword-research)

#### No search results returned

**Symptoms:** keyword_map.json not created; "0 results found" error

**Causes:**
- Seed keyword is too specific/niche
- Search API temporarily unavailable
- Network connectivity issue
- SEMrush API quota exceeded (if enabled)

**Solutions:**
1. **Try broader keyword**
   ```bash
   # Instead of
   openclaw run seo-content-flow "best waterproof vegan leather backpack"

   # Try
   openclaw run seo-content-flow "backpack"
   ```

2. **Check internet connectivity**
   ```bash
   ping google.com
   ```

3. **Test without SEMrush** (if using it)
   ```bash
   unset SEMRUSH_API_KEY
   openclaw run seo-content-flow "your-keyword"
   ```

4. **Try question format** (works well for long-tail)
   ```bash
   openclaw run seo-content-flow "how to choose a backpack"
   ```

---

#### Language detection wrong

**Symptoms:** Keyword marked as Vietnamese when it's English (or vice versa)

**Cause:** Diacritics in keyword confuse auto-detection

**Solution:**
```bash
# Explicitly specify language
export CONTENT_LANG=en
openclaw run seo-content-flow "cảnh tranh" # English keyword with diacritics
```

---

#### SEMrush API returns 401/403

**Symptoms:** "SEMrush API authentication failed" warning in output

**Cause:** Invalid API key or quota exceeded

**Solution:**
```bash
# Verify SEMrush key is valid
echo $SEMRUSH_API_KEY

# Option 1: Regenerate key from SEMrush dashboard
# Option 2: Skip SEMrush and use web search only
unset SEMRUSH_API_KEY
openclaw run seo-content-flow "your-keyword"
```

---

### Step 2: Outline Generation (seo-outline-generate)

#### Generic or low-quality headings

**Symptoms:** outline.json has vague H2 titles like "Introduction", "Overview", "Conclusion"

**Cause:** Keyword research returned insufficient LSI data

**Solution:**
1. **Use more specific seed keyword**
   ```bash
   # Instead of
   openclaw run seo-content-flow "coffee"

   # Try
   openclaw run seo-content-flow "best coffee grinder for espresso"
   ```

2. **Add competitor URLs manually**
   - Edit keyword_map.json
   - Add URLs from top SERP results to `competitor_urls` array
   - Re-run from outline step:
   ```bash
   openclaw run seo-content-flow --from outline --input keyword_map.json
   ```

---

#### Meta description too long/short

**Symptoms:** Meta description in outline.json is 200+ chars or < 50 chars

**Cause:** Automatic generation varies with keyword length

**Solution:**
1. **Manual edit** (before content write step)
   ```bash
   # Edit outline.json
   vi outline.json
   # Update "meta_description" to be 150-160 chars

   # Re-run from write
   openclaw run seo-content-flow --from write --input outline.json
   ```

---

### Step 3: Content Writing (seo-content-write)

#### Content in wrong language

**Symptoms:** Article written in English when Vietnamese requested (or vice versa)

**Cause:** CONTENT_LANG env var not set or not exported

**Solution:**
```bash
# Check current language setting
echo $CONTENT_LANG

# For Vietnamese
export CONTENT_LANG=vi
openclaw run seo-content-flow "máy tính xách tay tốt nhất"

# For English
export CONTENT_LANG=en
openclaw run seo-content-flow "best laptops 2026"
```

---

#### Article too short (< 500 words)

**Symptoms:** article.md has minimal content

**Cause:** Outline sections have low word count targets

**Solution:**
1. **Edit outline.json before write**
   ```bash
   vi outline.json
   # Increase word_count_target in sections from 200 to 500+

   openclaw run seo-content-flow --from write --input outline.json
   ```

2. **Manually expand after write**
   ```bash
   vi article.md
   # Add more details to each section

   # Re-run optimization
   openclaw run seo-content-flow --from optimize --input article.md
   ```

---

#### Keyword placement unnatural

**Symptoms:** Primary keyword appears awkwardly or too many times

**Cause:** Content writer algorithm emphasizes density over readability

**Solution:**
```bash
# Manual editing is best for quality
vi article.md

# Rewrite sections with unnatural keyword use
# Aim for 1-2% keyword density (natural mentions)

# Re-run optimization to verify quality
openclaw run seo-content-flow --from optimize --input article.md
```

---

### Step 4: Image Generation (seo-image-generate)

#### Images fail to generate (401 error)

**Symptoms:** "Unauthorized" or "401" error; no image_map.json created

**Cause:** Invalid or expired GOOGLE_API_KEY

**Solution:**
```bash
# Verify key is set
echo $GOOGLE_API_KEY

# Regenerate key from your image API provider dashboard
# Update environment variable
export GOOGLE_API_KEY="new_key_here"

# Resume from images step
openclaw run seo-content-flow --from images --input article.md
```

---

#### Images take too long (timeout)

**Symptoms:** Step 4 running > 15 minutes or timeout error

**Cause:** API rate limiting or very slow image provider

**Solution:**
1. **Skip image generation if not needed**
   ```bash
   # Resume from optimize without images
   openclaw run seo-content-flow --from optimize --input article.md
   ```

2. **Use faster image provider**
   - Check your image API provider's response times
   - Consider providers with faster SLAs

3. **Reduce number of images**
   - Fewer H2 headings = fewer section images
   - Edit article.md to consolidate sections

---

#### Wrong image dimensions

**Symptoms:** Images are 640×480, not 1200×630 (featured) or 800×450 (sections)

**Cause:** Image API uses different dimension parameters

**Solution:**
1. **Check your API provider's parameter names**
   - Some use `width`/`height`
   - Some use `size`/`aspect_ratio`
   - Some use `dimensions`

2. **Manual image replacement**
   - Generate images manually at correct dimensions
   - Edit image_map.json with correct paths
   - Continue from optimize step

---

#### No alt text or wrong alt text

**Symptoms:** image_map.json missing `alt` fields or alt text is generic

**Cause:** Alt text generation failed or used placeholder

**Solution:**
```bash
# Edit image_map.json manually
vi image_map.json

# Update alt text for each image
# Good alt text: descriptive, includes keywords naturally
# Bad alt text: "image", "photo", "picture"

# Example good alt text:
# "Best running shoes for beginners - top view of Nike and Adidas"

# Continue from optimize
openclaw run seo-content-flow --from optimize --input article.md
```

---

### Step 5: Score Optimization (seo-optimize-score)

#### Score stuck below 70

**Symptoms:** score_report.json shows overall_score: 65-69; pipeline halts

**Cause:** Article quality needs improvement in specific areas

**Solution:**
1. **Review suggestions in score_report.json**
   ```bash
   cat score_report.json | jq '.suggestions[] | {issue, impact, fix}'
   ```

2. **Address high-impact issues first**
   - "Add 2-3 internal links" (usually easy, high impact)
   - "Reduce keyword density from 5% to 2.5%" (edit article)
   - "Add meta schema markup" (skill adds automatically)

3. **Common quick wins**
   ```bash
   vi optimized_article.md

   # Fix 1: Adjust meta_title length (should be 50-60 chars)
   # Fix 2: Add internal links to related articles
   # Fix 3: Improve paragraph transitions
   # Fix 4: Add more specific examples

   # Re-run optimize
   openclaw run seo-content-flow --from optimize --input optimized_article.md
   ```

4. **If still low after fixes**
   - Article topic may be too thin for high score
   - Try different keyword with more content potential
   - Use aeo-optimize skill for AI-enhanced suggestions

---

#### Cannot find sitemap for internal links

**Symptoms:** "Sitemap not found at ${WORDPRESS_URL}/sitemap.xml"

**Cause:** WordPress sitemap disabled or at non-standard location

**Solution:**
1. **Enable XML sitemap in WordPress**
   - Install Yoast SEO or Rank Math (includes sitemap)
   - Or manually create sitemap.xml

2. **Verify sitemap location**
   ```bash
   curl -s "${WORDPRESS_URL}/sitemap.xml" | head
   ```

3. **Provide local sitemap file**
   - Create JSON file with site URLs
   - Pass as input to optimize step

---

#### Score calculation seems wrong

**Symptoms:** Very high or very low score that doesn't match quality

**Cause:** Scoring algorithm weights may not match expectations

**Solution:**
1. **Review breakdown in score_report.json**
   ```bash
   cat score_report.json | jq '.breakdown'
   ```

2. **Check specific category scores**
   - If heading_structure is 0/15, verify H2/H3 tags in article
   - If keyword_optimization is low, check keyword density
   - If images is 0/10, verify image_map.json exists

---

### Step 6: CMS Publishing (seo-publish-cms)

#### Cannot authenticate to WordPress (401)

**Symptoms:** "Unauthorized" error; "invalid username or password"

**Cause:** Invalid WORDPRESS_TOKEN format or expired credentials

**Solution:**
1. **Verify token format**
   ```bash
   # Should be exactly: username:app_password (no spaces)
   echo "WORDPRESS_TOKEN=$WORDPRESS_TOKEN"
   ```

2. **Regenerate Application Password**
   - Go to WP Admin > Users > Your Profile
   - Scroll to "Application Passwords"
   - Delete old "SEO Skills" password
   - Create new one and copy entire password string
   ```bash
   export WORDPRESS_TOKEN="your_username:entire_new_password"
   ```

3. **Test authentication**
   ```bash
   curl -X GET "${WORDPRESS_URL}/wp-json/wp/v2/users/me" \
     -u "${WORDPRESS_TOKEN}" \
     -H "Content-Type: application/json"
   ```

4. **Retry publish step**
   ```bash
   openclaw run seo-content-flow --from publish --input optimized_article.md
   ```

---

#### REST API endpoint not found (404)

**Symptoms:** "404 not found" on /wp-json/wp/v2/posts

**Cause:** WordPress Permalinks set to "Plain" or REST API disabled

**Solution:**
1. **Enable Pretty Permalinks**
   - Go to WP Admin > Settings > Permalinks
   - Change from "Plain" to "Post name" or another option
   - Click "Save Changes"
   - Wait 10 seconds

2. **Verify REST API is accessible**
   ```bash
   curl -X GET "${WORDPRESS_URL}/wp-json/" \
     -H "Content-Type: application/json"
   ```

3. **Check security plugins**
   - Some security plugins block REST API
   - Whitelist your IP in plugin settings
   - Or temporarily disable plugin during testing

4. **Retry publish step**
   ```bash
   openclaw run seo-content-flow --from publish --input optimized_article.md
   ```

---

#### Featured image not attached

**Symptoms:** Post published but no featured image; image_map.json exists

**Cause:** image_map.json missing or in wrong location

**Solution:**
1. **Verify image_map.json exists**
   ```bash
   ls -la image_map.json
   ```

2. **Verify format**
   ```bash
   cat image_map.json | jq '.featured_image'
   # Should show: { "path": "...", "alt": "...", "size": "1200x630" }
   ```

3. **Ensure both files in same directory**
   ```bash
   # Run from directory containing both files
   pwd
   ls -la optimized_article.md image_map.json
   ```

4. **Retry publish step**
   ```bash
   openclaw run seo-content-flow --from publish --input optimized_article.md
   ```

---

#### Post created but not visible in drafts

**Symptoms:** "Post published successfully" but can't find it in WP Admin > Posts > Drafts

**Cause:** Post exists but with different status or author

**Solution:**
1. **Check publish output for post_id**
   ```bash
   cat publish_result.json | jq '.post_id'
   ```

2. **Access post directly**
   ```bash
   # If post_id is 123
   firefox "${WORDPRESS_URL}/?p=123"
   ```

3. **Search in WP Admin**
   - Go to WP Admin > Posts
   - Search for article title
   - Filter by author (created by your API user)

4. **Check post status**
   ```bash
   curl -X GET "${WORDPRESS_URL}/wp-json/wp/v2/posts/123" \
     -u "${WORDPRESS_TOKEN}" \
     -H "Content-Type: application/json" | jq '.status'
   ```

---

#### Publishing to Shopify/Haravan fails

**Symptoms:** "Authentication failed" or "Store not found"

**Cause:** Incorrect store URL or access token

**Solution:**

**For Shopify:**
```bash
# Verify format
export SHOPIFY_STORE_URL="https://mystore.myshopify.com"  # Include https://
export SHOPIFY_ACCESS_TOKEN="shpat_..."                   # From Shopify Admin

# Test API access
curl -X GET "${SHOPIFY_STORE_URL}/admin/api/2024-01/blogs.json" \
  -H "X-Shopify-Access-Token: ${SHOPIFY_ACCESS_TOKEN}"
```

**For Haravan:**
```bash
# Verify format
export HARAVAN_STORE_URL="https://mystore.haravan.com"    # Include https://
export HARAVAN_ACCESS_TOKEN="token..."                    # From Haravan Admin

# Test API access
curl -X GET "${HARAVAN_STORE_URL}/admin/articles.json" \
  -H "Authorization: Bearer ${HARAVAN_ACCESS_TOKEN}"
```

---

## Workflow-Level Issues

### Resume from step doesn't work

**Symptoms:** "File not found" when using --from flag

**Cause:** Output file from previous step missing or wrong path

**Solution:**
1. **Verify output file exists**
   ```bash
   ls -la keyword_map.json outline.json article.md
   ```

2. **Use full path if in different directory**
   ```bash
   openclaw run seo-content-flow --from outline --input /full/path/keyword_map.json
   ```

3. **Check file format is JSON/Markdown**
   ```bash
   file keyword_map.json
   # Should output: "JSON data" or "ASCII text"
   ```

---

### Batch processing fails on one keyword

**Symptoms:** seo-batch-flow stops after first or second keyword

**Cause:** One keyword fails; entire batch halts

**Solution:**
1. **Process keywords individually**
   ```bash
   for kw in "keyword1" "keyword2" "keyword3"; do
     openclaw run seo-content-flow "$kw"
     # Check for errors before continuing
   done
   ```

2. **Resume batch from specific keyword**
   - Remove failed keyword from keywords.json
   - Run batch again with remaining keywords
   - Manually re-run failed keyword

---

### Memory/performance issues

**Symptoms:** Process crashes, slow execution, high CPU/memory usage

**Cause:** Large site audit or many images being generated

**Solution:**
1. **Reduce batch size**
   ```bash
   # Instead of 100 keywords at once
   # Process 10 keywords at a time
   ```

2. **Reduce image count**
   - Edit article to have fewer H2 sections
   - Fewer headings = fewer images generated

3. **Run during off-peak**
   - Batch processing during low traffic times
   - Easier on server and API quotas

---

## Environment & Configuration Issues

### env vars not being read

**Symptoms:** "Variable not set" error despite export command

**Cause:** Variable not exported or export in different shell session

**Solution:**
```bash
# Export before running (same terminal session)
export WORDPRESS_URL="..."
export WORDPRESS_TOKEN="..."
export GOOGLE_API_KEY="..."

# Verify they're set
env | grep WORDPRESS

# Then run
openclaw run seo-content-flow "keyword"
```

---

### OpenClaw command not found

**Symptoms:** "openclaw: command not found"

**Cause:** OpenClaw not installed or not in PATH

**Solution:**
```bash
# Check if installed
which openclaw

# If not found, install via package manager or source
# Then add to PATH if needed
export PATH="/opt/openclaw/bin:$PATH"
```

---

## Performance Optimization

### Slow keyword research step

**Cause:** Web search parsing takes time

**Solution:**
1. Enable SEMrush API (faster than parsing web results)
2. Use simpler keywords (fewer variations)
3. Reduce SEMrush result count if using API

---

### Slow content writing step

**Cause:** LLM API latency

**Solution:**
1. Check API provider status
2. Use faster model if available
3. Reduce word count target (edit outline.json)

---

### Slow image generation step

**Cause:** Image API latency or rate limiting

**Solution:**
1. Use faster image provider
2. Reduce number of section images (consolidate headings)
3. Generate images in off-peak hours

---

## Support Resources

For issues not covered here:
1. Check individual skill SKILL.md documents
2. Review skill script error messages (verbose output)
3. Check API provider documentation (WordPress, Shopify, Haravan)
4. Enable debug logging: `openclaw run ... 2>&1 | tee debug.log`

---

## Quick Diagnostic Checklist

Before reporting issues, verify:

- [ ] Python 3.7+ installed (`python3 --version`)
- [ ] Internet connectivity (`ping google.com`)
- [ ] All env vars set and exported (`env | grep -E "WORDPRESS|IMAGE_GEN"`)
- [ ] WordPress REST API enabled (test with curl)
- [ ] Image API key valid (test directly with provider)
- [ ] Output files from previous steps exist (ls *.json)
- [ ] File permissions allow read/write (ls -la)
- [ ] Sufficient disk space (df -h)
- [ ] Sufficient memory (free -m)
