#!/usr/bin/env bash
set -uo pipefail
# Don't set -e; we track pass/fail manually

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"
FIXTURES="$SCRIPT_DIR/fixtures"
PASS=0
FAIL=0
SKIP=0

run_test() {
  local name="$1"
  local cmd="$2"
  local expect_exit="${3:-0}"

  printf "%-50s " "$name"
  output=$(eval "$cmd" 2>&1)
  actual_exit=$?

  if [ "$actual_exit" -eq "$expect_exit" ]; then
    echo "PASS"
    PASS=$((PASS + 1))
  else
    echo "FAIL (exit $actual_exit, expected $expect_exit)"
    echo "  Output: $(echo "$output" | head -3)"
    FAIL=$((FAIL + 1))
  fi
}

echo "OpenClaw SEO Skills — Smoke Tests"
echo "=================================="
echo ""

# 1. keyword-analyzer
run_test "keyword-analyzer (with search results)" \
  "cat $FIXTURES/sample-search-results.json | python3 $REPO_ROOT/seo-keyword-research/scripts/keyword-analyzer.py --keyword 'running shoes for beginners'"

# 2. outline-validator (valid input)
run_test "outline-validator (valid outline)" \
  "cat $FIXTURES/sample-outline.json | python3 $REPO_ROOT/seo-outline-generate/scripts/outline-validator.py"

# 3. outline-validator (invalid — should exit 1)
run_test "outline-validator (invalid meta_title)" \
  "echo '{\"title\":\"T\",\"meta_title\":\"This title is way too long and exceeds the sixty character limit for SEO meta titles absolutely\",\"meta_description\":\"D\",\"slug\":\"t\",\"schema_type\":\"Article\",\"sections\":[],\"faq\":[]}' | python3 $REPO_ROOT/seo-outline-generate/scripts/outline-validator.py" 1

# 4. content-formatter
run_test "content-formatter (article formatting)" \
  "cat $FIXTURES/sample-article.md | python3 $REPO_ROOT/seo-content-write/scripts/content-formatter.py --keywords 'running shoes for beginners,best running shoes'"

# 5. seo-score-calculator
run_test "seo-score-calculator (score article)" \
  "python3 $REPO_ROOT/seo-scorer/scripts/seo-score-calculator.py $FIXTURES/sample-article.md"

# 6. image-prompt-builder
run_test "image-prompt-builder (generate prompts)" \
  "python3 $REPO_ROOT/seo-image-generate/scripts/image-prompt-builder.py $FIXTURES/sample-article.md"

# 7. alt-text-generator
run_test "alt-text-generator (generate alt text)" \
  "echo '{\"heading\":\"How to Choose Running Shoes\",\"keywords\":[\"running shoes for beginners\"],\"context\":\"Choosing the right pair of shoes is essential for comfort.\"}' | python3 $REPO_ROOT/seo-image-generate/scripts/alt-text-generator.py"

# 8. serp-parser
run_test "serp-parser (parse SERP results)" \
  "cat $FIXTURES/sample-serp-results.json | python3 $REPO_ROOT/seo-serp-scraper/scripts/serp-parser.py --query 'running shoes for beginners'"

# 9. robots-sitemap-checker
run_test "robots-sitemap-checker (check robots+sitemap)" \
  "cat $FIXTURES/sample-robots-sitemap.json | python3 $REPO_ROOT/seo-technical-audit/scripts/robots-sitemap-checker.py"

# 10. structured-data-checker
run_test "structured-data-checker (validate JSON-LD)" \
  "cat $FIXTURES/sample-html-with-jsonld.html | python3 $REPO_ROOT/seo-technical-audit/scripts/structured-data-checker.py"

# 11. content-gap-finder
run_test "content-gap-finder (find gaps)" \
  "cat $FIXTURES/sample-competitor-data.json | python3 $REPO_ROOT/seo-competitor-analyze/scripts/content-gap-finder.py"

# 12. keyword-gap-analyzer
run_test "keyword-gap-analyzer (find keyword gaps)" \
  "echo '{\"target_keywords\":[\"running shoes\",\"trail running\"],\"competitor_keywords\":[\"running shoes\",\"marathon training\",\"recovery tips\",\"runner nutrition\"]}' | python3 $REPO_ROOT/seo-competitor-analyze/scripts/keyword-gap-analyzer.py"

# 13. aeo-formatter
run_test "aeo-formatter (add answer blocks)" \
  "cat $FIXTURES/sample-article.md | python3 $REPO_ROOT/seo-aeo-optimize/scripts/aeo-formatter.py"

# 14. internal-link-suggester (with JSON sitemap)
run_test "internal-link-suggester (suggest links)" \
  "python3 $REPO_ROOT/seo-optimize-score/scripts/internal-link-suggester.py $FIXTURES/sample-article.md $FIXTURES/sample-sitemap-urls.json"

# 15. batch-runner (keyword dedup)
run_test "batch-runner (dedup keywords)" \
  "printf 'running shoes\ntrail running\nrunning shoes\nmarathon tips\n' | python3 $REPO_ROOT/seo-batch-flow/scripts/batch-runner.py"

# 16. adapter-interface (factory test)
run_test "cms-adapter-interface (factory import)" \
  "python3 -c \"import sys; sys.path.insert(0,'$REPO_ROOT/seo-cms-adapter/scripts'); from importlib import util; spec=util.spec_from_file_location('adapter_interface','$REPO_ROOT/seo-cms-adapter/scripts/adapter-interface.py'); mod=util.module_from_spec(spec); sys.modules['adapter_interface']=mod; spec.loader.exec_module(mod); a=mod.get_adapter('wordpress'); print('OK:', type(a).__name__)\""

# Summary
echo ""
echo "=================================="
echo "Results: $PASS passed, $FAIL failed, $SKIP skipped"
echo ""

if [ "$FAIL" -gt 0 ]; then
  exit 1
fi
exit 0
