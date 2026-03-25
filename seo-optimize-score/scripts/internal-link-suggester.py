#!/usr/bin/env python3
"""Internal link suggester for SEO optimization.

Reads an article and a sitemap (URL or JSON file), matches article
keywords against page titles/URLs in the sitemap, and outputs
JSON link suggestions for internal linking.

Usage:
    python3 internal-link-suggester.py <article.md> <sitemap_url_or_json>

Sitemap sources:
    - XML sitemap URL: https://example.com/sitemap.xml
    - JSON file: [{"url": "...", "title": "..."}, ...]

Output (stdout):
    [{"anchor_text": "str", "target_url": "str", "context": "str"}]
"""

import json
import os
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET


# ---------------------------------------------------------------------------
# Frontmatter + article parsing (reuses same logic as seo-score-calculator)
# ---------------------------------------------------------------------------

def parse_frontmatter(text):
    """Extract YAML frontmatter fields and body from markdown."""
    meta = {}
    body = text

    fm_match = re.match(r'^---\s*\n(.*?)\n---\s*\n', text, re.DOTALL)
    if not fm_match:
        return meta, body

    raw_fm = fm_match.group(1)
    body = text[fm_match.end():]

    for line in raw_fm.splitlines():
        kv = re.match(r'^(\w+):\s*(.+)$', line.strip())
        if kv:
            key, val = kv.group(1), kv.group(2).strip()
            if val.startswith('[') and val.endswith(']'):
                inner = val[1:-1]
                items = [s.strip().strip('"').strip("'")
                         for s in inner.split(',') if s.strip()]
                meta[key] = items
            else:
                meta[key] = val.strip('"').strip("'")

    # Block list support
    block_key = None
    for line in raw_fm.splitlines():
        bk = re.match(r'^(\w+):\s*$', line.strip())
        if bk:
            block_key = bk.group(1)
            meta[block_key] = []
            continue
        if block_key:
            item = re.match(r'^\s*-\s+(.+)$', line)
            if item:
                meta[block_key].append(item.group(1).strip().strip('"').strip("'"))
            else:
                block_key = None

    return meta, body


def extract_article_keywords(meta, body):
    """Collect all keywords from frontmatter and prominent body phrases."""
    keywords = []

    primary = meta.get('primary_keyword', '')
    if primary:
        keywords.append(primary.lower())

    secondary = meta.get('secondary_keywords', [])
    if isinstance(secondary, str):
        secondary = [s.strip() for s in secondary.split(',')]
    keywords.extend(k.lower() for k in secondary if k)

    # Extract H2 heading text as implicit keyword phrases
    h2_headings = re.findall(r'^## (.+)$', body, re.MULTILINE)
    for heading in h2_headings:
        # Clean markdown from heading
        clean = re.sub(r'[\*_`\[\]]', '', heading).strip().lower()
        if len(clean.split()) <= 6:  # Only short headings make good keywords
            keywords.append(clean)

    return list(dict.fromkeys(keywords))  # Deduplicate, preserve order


def get_existing_link_urls(body):
    """Return set of URLs already linked in the article."""
    links = re.findall(r'(?<!!)\[([^\]]+)\]\(([^\)]+)\)', body)
    return {url for _, url in links}


def split_into_sentences(text):
    """Split plain text into sentences."""
    # Remove markdown syntax for context extraction
    plain = re.sub(r'```[\s\S]*?```', ' ', text)
    plain = re.sub(r'`[^`]+`', ' ', plain)
    plain = re.sub(r'!\[[^\]]*\]\([^\)]*\)', ' ', plain)
    plain = re.sub(r'\[([^\]]*)\]\([^\)]*\)', r'\1', plain)
    plain = re.sub(r'^#+\s+', '', plain, flags=re.MULTILINE)
    plain = re.sub(r'[\*_]{1,3}', '', plain)
    sentences = re.split(r'(?<=[.!?])\s+', plain)
    return [s.strip() for s in sentences if len(s.strip()) > 20]


# ---------------------------------------------------------------------------
# Sitemap fetching
# ---------------------------------------------------------------------------

def fetch_xml_sitemap(url):
    """Fetch and parse an XML sitemap, returning list of {url, title} dicts."""
    pages = []
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'SEO-LinkSuggester/1.0'})
        with urllib.request.urlopen(req, timeout=10) as resp:
            content = resp.read()
    except Exception as e:
        print(f"Warning: could not fetch sitemap from {url}: {e}", file=sys.stderr)
        return pages

    try:
        root = ET.fromstring(content)
    except ET.ParseError as e:
        print(f"Warning: could not parse sitemap XML: {e}", file=sys.stderr)
        return pages

    # Strip XML namespace for easier querying
    ns_pattern = re.compile(r'\{[^}]+\}')

    def strip_ns(tag):
        return ns_pattern.sub('', tag)

    # Handle standard sitemap and sitemap index
    for elem in root.iter():
        tag = strip_ns(elem.tag)
        if tag == 'url':
            loc = None
            title = None
            for child in elem:
                child_tag = strip_ns(child.tag)
                if child_tag == 'loc':
                    loc = (child.text or '').strip()
                # Some sitemaps include <news:title> or <xhtml:title>
                if 'title' in child_tag.lower():
                    title = (child.text or '').strip()
            if loc:
                pages.append({'url': loc, 'title': title or ''})

    return pages


def load_sitemap_source(source):
    """Load pages from a sitemap URL or a local JSON file."""
    if source.startswith('http://') or source.startswith('https://'):
        return fetch_xml_sitemap(source)

    # Local JSON file
    if not os.path.isfile(source):
        print(f"Error: sitemap source not found: {source}", file=sys.stderr)
        return []

    try:
        with open(source, 'r', encoding='utf-8') as f:
            data = json.load(f)
        if not isinstance(data, list):
            print("Warning: JSON sitemap must be a list of {url, title} objects",
                  file=sys.stderr)
            return []
        return [{'url': p.get('url', ''), 'title': p.get('title', '')}
                for p in data if p.get('url')]
    except (json.JSONDecodeError, OSError) as e:
        print(f"Error reading JSON sitemap: {e}", file=sys.stderr)
        return []


# ---------------------------------------------------------------------------
# Keyword matching
# ---------------------------------------------------------------------------

def url_to_readable(url):
    """Convert a URL slug to readable words for matching."""
    path = url.rstrip('/').split('/')[-1]
    path = re.sub(r'\.(html?|php|aspx?)$', '', path)
    return re.sub(r'[-_]', ' ', path).lower()


def score_page_relevance(page_url, page_title, keywords):
    """Score how relevant a page is to the article keywords.

    Returns (score, best_keyword, match_type).
    match_type: 'title' | 'url' | 'partial'
    """
    title_lower = page_title.lower()
    url_words = url_to_readable(page_url)
    best_score = 0
    best_kw = ''
    best_type = ''

    for kw in keywords:
        kw_words = kw.split()

        # Exact phrase match in title
        if kw in title_lower:
            score = len(kw_words) * 10 + 5
            if score > best_score:
                best_score, best_kw, best_type = score, kw, 'title'
            continue

        # Exact phrase match in URL slug
        if kw in url_words:
            score = len(kw_words) * 8
            if score > best_score:
                best_score, best_kw, best_type = score, kw, 'url'
            continue

        # Partial word overlap with title
        overlap = sum(1 for w in kw_words if w in title_lower.split())
        if overlap >= max(1, len(kw_words) // 2):
            score = overlap * 3
            if score > best_score:
                best_score, best_kw, best_type = score, kw, 'partial'

    return best_score, best_kw, best_type


def find_anchor_context(body, keyword, target_url):
    """Find a sentence in the article body where keyword appears naturally.

    Returns (anchor_text, context_sentence) or (None, None).
    """
    sentences = split_into_sentences(body)
    kw_lower = keyword.lower()
    kw_words = kw_lower.split()

    for sentence in sentences:
        sent_lower = sentence.lower()

        # Skip sentences that already contain a link to target_url
        if target_url in sentence:
            continue

        # Check if keyword appears in sentence
        if kw_lower in sent_lower:
            # Find original-case anchor text
            match = re.search(re.escape(keyword), sentence, re.IGNORECASE)
            if match:
                return match.group(0), sentence.strip()

        # Partial match: all keyword words present
        if all(w in sent_lower for w in kw_words):
            # Reconstruct anchor from sentence
            pattern = r'\b' + r'\s+'.join(re.escape(w) for w in kw_words) + r'\b'
            match = re.search(pattern, sentence, re.IGNORECASE)
            if match:
                return match.group(0), sentence.strip()

    return None, None


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    if len(sys.argv) < 3:
        print("Usage: internal-link-suggester.py <article.md> <sitemap_url_or_json>",
              file=sys.stderr)
        sys.exit(1)

    article_path = sys.argv[1]
    sitemap_source = sys.argv[2]

    if not os.path.isfile(article_path):
        print(f"Error: article not found: {article_path}", file=sys.stderr)
        sys.exit(1)

    with open(article_path, 'r', encoding='utf-8') as f:
        raw = f.read()

    meta, body = parse_frontmatter(raw)
    keywords = extract_article_keywords(meta, body)

    if not keywords:
        print("Warning: no keywords found in article frontmatter", file=sys.stderr)

    existing_urls = get_existing_link_urls(body)
    pages = load_sitemap_source(sitemap_source)

    if not pages:
        print("[]")
        return

    # Score each page for relevance
    candidates = []
    for page in pages:
        page_url = page.get('url', '').strip()
        page_title = page.get('title', '').strip()

        if not page_url:
            continue

        # Skip pages already linked
        if page_url in existing_urls:
            continue

        # Skip the article's own URL if it happens to be in the sitemap
        score, matched_kw, match_type = score_page_relevance(
            page_url, page_title, keywords
        )

        if score > 0:
            candidates.append({
                'score': score,
                'url': page_url,
                'title': page_title,
                'keyword': matched_kw,
                'match_type': match_type
            })

    # Sort by relevance score descending
    candidates.sort(key=lambda x: x['score'], reverse=True)

    # Build suggestions with context
    suggestions = []
    used_keywords = set()
    max_suggestions = 10

    for candidate in candidates:
        if len(suggestions) >= max_suggestions:
            break

        kw = candidate['keyword']
        # Avoid two suggestions with identical anchor keyword
        if kw in used_keywords:
            continue

        anchor, context = find_anchor_context(body, kw, candidate['url'])
        if not anchor:
            # Fall back to page title words as anchor
            title_words = candidate['title'].lower().split()
            kw_words = kw.split()
            if all(w in title_words for w in kw_words):
                anchor = candidate['title']
                context = f"Consider linking '{anchor}' near mentions of '{kw}'"
            else:
                anchor = candidate['title'] or kw
                context = f"Link '{anchor}' where '{kw}' is discussed"

        suggestions.append({
            'anchor_text': anchor,
            'target_url': candidate['url'],
            'context': context[:200]  # Trim long contexts
        })
        used_keywords.add(kw)

    print(json.dumps(suggestions, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()
