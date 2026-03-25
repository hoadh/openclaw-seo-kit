#!/usr/bin/env python3
"""
keyword-gap-analyzer.py — Find keywords competitors target that the target site misses.

Input (stdin): JSON object:
  {"target_keywords": ["str"], "competitor_keywords": ["str"]}

Output (stdout): JSON array sorted by priority:
  [{"keyword": "str", "priority": "high|medium|low", "competitor_count": int}]

Stdlib: json, re, sys, collections
"""

import json
import re
import sys
from collections import Counter


STOPWORDS = frozenset({
    'the', 'a', 'an', 'and', 'or', 'in', 'on', 'at', 'to', 'for', 'of',
    'with', 'by', 'is', 'are', 'was', 'be', 'it', 'this', 'that', 'how',
    'what', 'why', 'when', 'where', 'we', 'you', 'i', 'my', 'your', 'our',
})

# Suffixes to strip for simple normalization (poor-man's stemming)
STRIP_SUFFIXES = ('ing', 'tion', 'tions', 'ed', 'ly', 'er', 'ers', 'ies', 'es')


def normalize(kw: str) -> str:
    """Lowercase, remove punctuation, collapse whitespace."""
    kw = kw.lower().strip()
    kw = re.sub(r'[^\w\s]', ' ', kw)
    kw = re.sub(r'\s+', ' ', kw).strip()
    return kw


def stem(word: str) -> str:
    """Very simple suffix stripping for deduplication purposes."""
    for suffix in STRIP_SUFFIXES:
        if word.endswith(suffix) and len(word) - len(suffix) > 3:
            return word[:-len(suffix)]
    return word


def tokenize(kw: str) -> list:
    """Return meaningful tokens from a keyword phrase."""
    tokens = normalize(kw).split()
    return [t for t in tokens if t not in STOPWORDS and len(t) > 2]


def keyword_signature(kw: str) -> frozenset:
    """Create a canonical frozenset of stemmed tokens for fuzzy matching."""
    return frozenset(stem(t) for t in tokenize(kw))


def deduplicate_keywords(keywords: list) -> list:
    """Remove near-duplicate keywords based on stemmed token overlap."""
    seen_sigs = []
    result = []
    for kw in keywords:
        sig = keyword_signature(kw)
        if not sig:
            continue
        is_dup = any(
            len(sig & existing) / max(len(sig), len(existing)) >= 0.8
            for existing in seen_sigs
        )
        if not is_dup:
            seen_sigs.append(sig)
            result.append(kw)
    return result


def compute_priority(competitor_count: int, total_competitors: int) -> str:
    """Assign priority based on how many competitor sources include this keyword."""
    if total_competitors == 0:
        return 'low'
    ratio = competitor_count / max(1, total_competitors)
    if ratio >= 0.6 or competitor_count >= 3:
        return 'high'
    elif ratio >= 0.3 or competitor_count >= 2:
        return 'medium'
    return 'low'


def build_keyword_frequency_map(keywords: list) -> Counter:
    """Count how many times each normalized keyword appears."""
    counter = Counter()
    for kw in keywords:
        norm = normalize(kw)
        if norm:
            counter[norm] += 1
    return counter


def find_keyword_gaps(target_kws: list, competitor_kws: list) -> list:
    """
    Compare target and competitor keyword lists to find gaps.
    Returns sorted list of gap keywords with priority and count.
    """
    # Build target coverage as stemmed signatures
    target_sigs = {keyword_signature(kw) for kw in target_kws if normalize(kw)}

    def is_covered_by_target(kw: str) -> bool:
        """Return True if keyword overlaps significantly with target coverage."""
        sig = keyword_signature(kw)
        if not sig:
            return True
        for target_sig in target_sigs:
            if not target_sig:
                continue
            overlap = len(sig & target_sig) / max(len(sig), len(target_sig))
            if overlap >= 0.7:
                return True
        return False

    # Count competitor keyword occurrences
    competitor_freq = build_keyword_frequency_map(competitor_kws)

    # Collect unique competitor keywords not covered by target
    gaps = {}
    for kw_norm, count in competitor_freq.items():
        if not is_covered_by_target(kw_norm):
            gaps[kw_norm] = count

    # Estimate total "competitor sources" from max frequency for priority calibration
    max_count = max(gaps.values()) if gaps else 1
    total_competitors = max(max_count, 3)  # normalize scale

    # Deduplicate gap keywords
    gap_list = list(gaps.keys())
    gap_list_deduped = deduplicate_keywords(gap_list)

    # Build results
    results = []
    for kw in gap_list_deduped:
        count = gaps.get(kw, 1)
        priority = compute_priority(count, total_competitors)
        results.append({
            'keyword': kw,
            'priority': priority,
            'competitor_count': count
        })

    # Sort: high priority first, then by count descending
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

    target_keywords = data.get('target_keywords', [])
    competitor_keywords = data.get('competitor_keywords', [])

    if not isinstance(target_keywords, list) or not isinstance(competitor_keywords, list):
        print(json.dumps({'error': 'target_keywords and competitor_keywords must be arrays'}),
              file=sys.stderr)
        sys.exit(1)

    results = find_keyword_gaps(target_keywords, competitor_keywords)
    print(json.dumps(results, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()
