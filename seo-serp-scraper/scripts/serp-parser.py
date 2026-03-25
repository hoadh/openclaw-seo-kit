#!/usr/bin/env python3
"""
serp-parser.py — Parse SERP result objects into structured SEO data.

Input (stdin): JSON array of search result objects with fields:
  title, snippet, url, type (optional), position (optional)

Output (stdout): serp_results.json matching references/serp-results-schema.json
"""

import json
import re
import sys
from urllib.parse import urlparse
from datetime import datetime, timezone


QUESTION_STARTERS = ('what', 'how', 'why', 'when', 'where', 'who', 'which',
                     'can', 'does', 'is', 'are', 'will', 'should', 'do')
PAA_PATTERN = re.compile(r'.+\?$', re.IGNORECASE)


def extract_domain(url: str) -> str:
    """Extract domain from URL string."""
    try:
        parsed = urlparse(url)
        return parsed.netloc.lower().lstrip('www.')
    except Exception:
        return ''


def is_question(text: str) -> bool:
    """Return True if text looks like a PAA question."""
    text = text.strip()
    if PAA_PATTERN.match(text):
        lower = text.lower()
        return any(lower.startswith(w) for w in QUESTION_STARTERS)
    return False


def detect_featured_snippet(item: dict) -> bool:
    """Return True if item appears to be a featured snippet."""
    if str(item.get('type', '')).lower() in ('featured', 'featured_snippet'):
        return True
    if item.get('position') == 0:
        return True
    snippet = item.get('snippet', '')
    title = item.get('title', '')
    markers = ('featured snippet', 'answer box', 'direct answer')
    combined = (snippet + ' ' + title).lower()
    return any(m in combined for m in markers)


def classify_type(item: dict) -> str:
    """Map raw type string to canonical type value."""
    raw = str(item.get('type', '')).lower().strip()
    mapping = {
        'organic': 'organic',
        'featured': 'featured',
        'featured_snippet': 'featured',
        'video': 'video',
        'video_carousel': 'video',
        'image': 'image',
        'image_pack': 'image',
        'local': 'local',
        'local_pack': 'local',
        'local_results': 'local',
        'knowledge_panel': 'knowledge_panel',
        'knowledge': 'knowledge_panel',
        'paa': 'organic',
        'people_also_ask': 'organic',
        'related': 'organic',
        'related_searches': 'organic',
    }
    return mapping.get(raw, 'organic')


def parse_serp(raw_items: list) -> dict:
    """Parse list of raw SERP items into structured output."""
    results = []
    paa = []
    related_searches = []
    featured_snippet = None
    position_counter = 1

    for item in raw_items:
        if not isinstance(item, dict):
            continue

        title = str(item.get('title', '')).strip()
        snippet = str(item.get('snippet', '')).strip()
        url = str(item.get('url', '')).strip()
        raw_type = str(item.get('type', '')).lower()

        # Collect related searches separately
        if raw_type in ('related_searches', 'related'):
            if title:
                related_searches.append(title)
            continue

        # Detect PAA items
        if raw_type in ('paa', 'people_also_ask') or is_question(title):
            paa.append({'question': title, 'snippet': snippet, 'url': url})
            continue

        canonical_type = classify_type(item)
        is_featured = detect_featured_snippet(item)

        if is_featured and featured_snippet is None:
            featured_snippet = {
                'text': snippet,
                'url': url,
                'title': title,
                'format': 'paragraph'
            }
            position = 0
        else:
            position = item.get('position', position_counter)
            if not isinstance(position, int):
                position = position_counter
            position_counter += 1

        results.append({
            'position': position,
            'url': url,
            'title': title,
            'snippet': snippet,
            'type': canonical_type,
            'domain': extract_domain(url)
        })

    # Sort organic results by position
    organic = [r for r in results if r['type'] == 'organic']
    other = [r for r in results if r['type'] != 'organic']
    organic.sort(key=lambda x: x['position'])

    all_results = other + organic

    return {
        'query': '',
        'results': all_results,
        'paa': paa,
        'related_searches': related_searches,
        'featured_snippet': featured_snippet,
        'meta': {
            'total_results': len(all_results),
            'parsed_at': datetime.now(timezone.utc).isoformat(),
            'has_featured_snippet': featured_snippet is not None,
            'has_paa': len(paa) > 0,
            'has_video_carousel': any(r['type'] == 'video' for r in all_results),
            'has_local_pack': any(r['type'] == 'local' for r in all_results)
        }
    }


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

    # Support both array input and object with query + results
    if isinstance(data, dict):
        query = data.get('query', '')
        items = data.get('results', [])
    elif isinstance(data, list):
        query = ''
        items = data
    else:
        print(json.dumps({'error': 'Input must be JSON array or object'}), file=sys.stderr)
        sys.exit(1)

    output = parse_serp(items)
    output['query'] = query

    print(json.dumps(output, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()
