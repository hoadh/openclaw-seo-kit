#!/usr/bin/env python3
"""
structured-data-checker.py — Extract and validate JSON-LD structured data from HTML.

Input (stdin): Raw HTML content as a string.
Output (stdout): JSON with found types, validation issues, and score 0-100.

Stdlib: json, re, sys, html.parser
"""

import json
import re
import sys
from html.parser import HTMLParser


# Required fields per Schema.org type
SCHEMA_REQUIRED_FIELDS = {
    'Article': ['headline', 'author', 'datePublished'],
    'NewsArticle': ['headline', 'author', 'datePublished'],
    'BlogPosting': ['headline', 'author', 'datePublished'],
    'HowTo': ['name', 'step'],
    'FAQPage': ['mainEntity'],
    'Product': ['name', 'offers'],
    'Recipe': ['name', 'recipeIngredient', 'recipeInstructions'],
    'Event': ['name', 'startDate', 'location'],
    'Organization': ['name', 'url'],
    'Person': ['name'],
    'BreadcrumbList': ['itemListElement'],
    'WebPage': ['name', 'url'],
    'LocalBusiness': ['name', 'address'],
    'VideoObject': ['name', 'description', 'uploadDate'],
}

# Recommended fields (not required but boost score)
SCHEMA_RECOMMENDED_FIELDS = {
    'Article': ['image', 'description', 'publisher'],
    'Product': ['description', 'image', 'brand'],
    'HowTo': ['description', 'totalTime', 'image'],
    'FAQPage': [],
    'VideoObject': ['thumbnailUrl', 'duration'],
}


class JsonLdExtractor(HTMLParser):
    """Extract all application/ld+json script blocks from HTML."""

    def __init__(self):
        super().__init__()
        self.blocks = []
        self._in_ld_json = False
        self._current = ''

    def handle_starttag(self, tag, attrs):
        if tag == 'script':
            attr_dict = dict(attrs)
            if attr_dict.get('type', '').lower() == 'application/ld+json':
                self._in_ld_json = True
                self._current = ''

    def handle_endtag(self, tag):
        if tag == 'script' and self._in_ld_json:
            self.blocks.append(self._current.strip())
            self._in_ld_json = False
            self._current = ''

    def handle_data(self, data):
        if self._in_ld_json:
            self._current += data


def get_schema_type(obj: dict) -> str:
    """Extract @type from schema object, normalizing to short name."""
    raw_type = obj.get('@type', '')
    if isinstance(raw_type, list):
        raw_type = raw_type[0] if raw_type else ''
    # Strip full URL prefix if present
    if '/' in raw_type:
        raw_type = raw_type.split('/')[-1]
    return raw_type


def validate_schema_object(obj: dict) -> dict:
    """Validate a single JSON-LD object. Returns issues list and score."""
    issues = []
    schema_type = get_schema_type(obj)

    if not schema_type:
        return {'type': 'Unknown', 'issues': ['Missing @type field'], 'score': 0}

    required = SCHEMA_REQUIRED_FIELDS.get(schema_type, [])
    recommended = SCHEMA_RECOMMENDED_FIELDS.get(schema_type, [])

    missing_required = [f for f in required if not obj.get(f)]
    missing_recommended = [f for f in recommended if not obj.get(f)]

    for field in missing_required:
        issues.append(f'Missing required field: {field}')

    for field in missing_recommended:
        issues.append(f'Missing recommended field: {field}')

    # Score: required fields 70%, recommended 30%
    req_score = 70 if not missing_required else max(0, 70 - len(missing_required) * 15)
    rec_score = 30 if not missing_recommended else max(0, 30 - len(missing_recommended) * 10)
    score = req_score + rec_score

    return {
        'type': schema_type,
        'issues': issues,
        'score': min(100, score)
    }


def parse_json_ld_block(block: str) -> list:
    """Parse a JSON-LD block, returning list of schema objects."""
    try:
        data = json.loads(block)
    except json.JSONDecodeError as e:
        return [{'_parse_error': str(e)}]

    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        # Handle @graph pattern
        if '@graph' in data:
            return data['@graph']
        return [data]
    return []


def check_html(html: str) -> dict:
    """Main function: extract and validate all JSON-LD from HTML."""
    extractor = JsonLdExtractor()
    try:
        extractor.feed(html)
    except Exception:
        pass

    blocks = extractor.blocks
    found = len(blocks) > 0
    all_types = []
    all_issues = []
    block_results = []

    for block in blocks:
        objects = parse_json_ld_block(block)
        for obj in objects:
            if '_parse_error' in obj:
                all_issues.append(f"JSON parse error: {obj['_parse_error']}")
                continue
            result = validate_schema_object(obj)
            all_types.append(result['type'])
            all_issues.extend(result['issues'])
            block_results.append(result)

    # Compute overall score
    if not found:
        overall_score = 0
        all_issues.append('No JSON-LD structured data found')
    elif not block_results:
        overall_score = 10
    else:
        scores = [r['score'] for r in block_results]
        overall_score = int(sum(scores) / len(scores))

    return {
        'found': found,
        'types': list(set(all_types)),
        'block_count': len(blocks),
        'schema_objects': block_results,
        'issues': all_issues,
        'score': overall_score
    }


def main():
    html = sys.stdin.read()
    if not html.strip():
        result = {'found': False, 'types': [], 'issues': ['Empty input'], 'score': 0}
        print(json.dumps(result, indent=2))
        return

    result = check_html(html)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()
