#!/usr/bin/env python3
"""
content-gap-finder.py — Find topic gaps between target site and competitors.

Input (stdin): JSON object:
  {
    "target": {"pages": [{"url":"","title":"","meta":""}]},
    "competitors": [{"domain":"", "pages": [{"url":"","title":"","meta":""}]}]
  }

Output (stdout): JSON array of gap topics sorted by priority:
  [{"topic": "str", "competitor_urls": ["str"], "priority": "high|medium|low"}]

Stdlib: json, re, sys, collections
"""

import json
import re
import sys
from collections import Counter, defaultdict


# Common English stopwords to filter from topic extraction
STOPWORDS = frozenset({
    'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
    'of', 'with', 'by', 'from', 'is', 'are', 'was', 'were', 'be', 'been',
    'have', 'has', 'do', 'does', 'did', 'will', 'would', 'can', 'could',
    'should', 'may', 'might', 'it', 'its', 'this', 'that', 'these', 'those',
    'i', 'you', 'we', 'they', 'he', 'she', 'your', 'our', 'their', 'my',
    'how', 'what', 'why', 'when', 'where', 'which', 'who', 'all', 'more',
    'best', 'top', 'new', 'get', 'use', 'using', 'used', 'about', 'page',
    'vs', 'vs.', 'free', 'guide', 'complete', 'ultimate', 'review', 'reviews'
})


def normalize_text(text: str) -> str:
    """Lowercase, remove punctuation, normalize whitespace."""
    text = text.lower()
    text = re.sub(r'[^\w\s-]', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def extract_tokens(text: str) -> list:
    """Tokenize and remove stopwords."""
    tokens = normalize_text(text).split()
    return [t for t in tokens if t not in STOPWORDS and len(t) > 2]


def extract_ngrams(tokens: list, n: int = 2) -> list:
    """Generate n-grams from token list."""
    return [' '.join(tokens[i:i+n]) for i in range(len(tokens) - n + 1)]


def page_to_topic_signals(page: dict) -> list:
    """Extract topic n-grams from a page's title and meta."""
    title = str(page.get('title', '') or page.get('name', ''))
    meta = str(page.get('meta', '') or page.get('description', ''))
    url = str(page.get('url', ''))

    # Extract URL path words as additional signal
    url_words = re.sub(r'[^a-z0-9]', ' ', url.lower())

    combined = f"{title} {meta} {url_words}"
    tokens = extract_tokens(combined)

    # Generate both unigrams and bigrams
    unigrams = [t for t in tokens if len(t) > 4]
    bigrams = extract_ngrams(tokens, 2)
    trigrams = extract_ngrams(tokens, 3)

    return unigrams + bigrams + trigrams


def build_topic_index(pages: list) -> dict:
    """Build mapping of topic -> list of page URLs."""
    topic_urls = defaultdict(list)
    for page in pages:
        url = page.get('url', '')
        signals = page_to_topic_signals(page)
        for signal in signals:
            topic_urls[signal].append(url)
    return topic_urls


def topics_overlap(t1: str, t2: str) -> bool:
    """Return True if two topics share significant word overlap."""
    words1 = set(t1.split())
    words2 = set(t2.split())
    if not words1 or not words2:
        return False
    overlap = len(words1 & words2)
    smaller = min(len(words1), len(words2))
    return overlap / smaller >= 0.5


def cluster_topics(topic_list: list) -> list:
    """Group very similar topics into clusters, return representative topics."""
    if not topic_list:
        return []

    clusters = []
    used = set()

    for topic in topic_list:
        if topic in used:
            continue
        cluster = [topic]
        used.add(topic)
        for other in topic_list:
            if other not in used and topics_overlap(topic, other):
                cluster.append(other)
                used.add(other)
        # Use longest topic as representative (more specific)
        clusters.append(max(cluster, key=len))

    return clusters


def compute_priority(topic: str, competitor_urls: list, competitor_count: int) -> str:
    """Assign priority based on number of competitors covering the topic."""
    if competitor_count >= 2:
        return 'high'
    elif competitor_count == 1 and len(competitor_urls) >= 2:
        return 'medium'
    else:
        return 'low'


def find_content_gaps(data: dict) -> list:
    """Main gap finding logic."""
    target_pages = data.get('target', {}).get('pages', [])
    competitors = data.get('competitors', [])

    if not competitors:
        return []

    # Build target topic set
    target_topics = build_topic_index(target_pages)
    target_topic_set = set(target_topics.keys())

    # Count topics across competitors and track URLs
    competitor_topic_urls = defaultdict(list)   # topic -> [url, ...]
    competitor_topic_domains = defaultdict(set)  # topic -> {domain, ...}

    for comp in competitors:
        domain = comp.get('domain', 'unknown')
        pages = comp.get('pages', [])
        comp_topics = build_topic_index(pages)
        for topic, urls in comp_topics.items():
            # Only keep topics with reasonable specificity (bigrams/trigrams preferred)
            if len(topic.split()) < 2 and len(topic) < 8:
                continue
            competitor_topic_urls[topic].extend(urls[:3])
            competitor_topic_domains[topic].add(domain)

    # Filter: topics in competitor set but not in target
    gap_topics = {
        topic for topic in competitor_topic_urls
        if not any(topics_overlap(topic, t) for t in target_topic_set)
    }

    # Cluster similar gaps to reduce noise
    gap_list = cluster_topics(sorted(gap_topics))

    # Build output with priority
    results = []
    seen_urls = set()
    for topic in gap_list:
        urls = competitor_topic_urls.get(topic, [])
        unique_urls = []
        for u in urls:
            if u not in seen_urls:
                unique_urls.append(u)
                seen_urls.add(u)

        domain_count = len(competitor_topic_domains.get(topic, set()))
        priority = compute_priority(topic, unique_urls, domain_count)

        results.append({
            'topic': topic,
            'competitor_urls': unique_urls[:5],
            'competitor_count': domain_count,
            'priority': priority
        })

    # Sort: high first, then medium, then low; within priority by competitor count
    priority_order = {'high': 0, 'medium': 1, 'low': 2}
    results.sort(key=lambda x: (priority_order[x['priority']], -x['competitor_count']))

    return results


def main():
    raw = sys.stdin.read().strip()
    if not raw:
        print(json.dumps({'error': 'No input provided'}), file=sys.stderr)
        sys.exit(1)

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        print(json.dumps({'error': f'Invalid JSON: {e}'}), file=sys.stderr)
        sys.exit(1)

    results = find_content_gaps(data)
    print(json.dumps(results, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()
