#!/usr/bin/env python3
"""
robots-sitemap-checker.py — Parse robots.txt and sitemap.xml for SEO issues.

Input (stdin): JSON object:
  {"robots_txt": "str content", "sitemap_xml": "str content"}

Output (stdout): JSON with parsed rules, issues, and score 0-100.

Stdlib: json, re, sys, xml.etree.ElementTree
"""

import json
import re
import sys
import xml.etree.ElementTree as ET
from datetime import datetime, timezone


# Paths that should generally not be disallowed
IMPORTANT_PATHS = [
    '/', '/blog', '/products', '/services', '/about', '/contact',
    '/css/', '/js/', '/images/', '/static/', '/assets/'
]

# Sitemap XML namespaces
SITEMAP_NS = {
    'sm': 'http://www.sitemaps.org/schemas/sitemap/0.9',
    'image': 'http://www.google.com/schemas/sitemap-image/1.1',
    'news': 'http://www.google.com/schemas/sitemap-news/0.9',
}


def parse_robots_txt(content: str) -> dict:
    """Parse robots.txt into structured rules dict."""
    rules = []
    issues = []
    current_agents = []
    current_rules = []
    sitemaps = []
    crawl_delay = None

    lines = content.splitlines()
    for raw_line in lines:
        line = raw_line.strip()
        if not line or line.startswith('#'):
            continue

        if ':' not in line:
            continue

        directive, _, value = line.partition(':')
        directive = directive.strip().lower()
        value = value.strip()

        if directive == 'user-agent':
            if current_agents and current_rules:
                rules.append({'agents': current_agents[:], 'rules': current_rules[:]})
                current_rules = []
            if not current_agents or current_rules:
                current_agents = [value]
            else:
                current_agents.append(value)

        elif directive == 'disallow':
            current_rules.append({'type': 'disallow', 'path': value})

        elif directive == 'allow':
            current_rules.append({'type': 'allow', 'path': value})

        elif directive == 'sitemap':
            sitemaps.append(value)

        elif directive == 'crawl-delay':
            try:
                crawl_delay = float(value)
            except ValueError:
                issues.append(f'Invalid crawl-delay value: {value}')

    # Flush last group
    if current_agents and current_rules:
        rules.append({'agents': current_agents, 'rules': current_rules})

    # Check for issues
    all_disallowed = []
    for group in rules:
        agents = group['agents']
        is_all = '*' in agents or 'Googlebot' in agents
        for rule in group['rules']:
            if rule['type'] == 'disallow' and is_all:
                all_disallowed.append(rule['path'])

    # Flag blocking everything
    if '/' in all_disallowed:
        issues.append('CRITICAL: Disallow: / blocks all crawlers from entire site')

    # Flag blocking important resource paths
    for path in IMPORTANT_PATHS:
        for disallowed in all_disallowed:
            if disallowed and path.startswith(disallowed):
                issues.append(f'Potentially blocking important path: {disallowed} covers {path}')
                break

    # Flag missing sitemap reference
    if not sitemaps:
        issues.append('No Sitemap directive found in robots.txt')

    # Flag high crawl delay
    if crawl_delay and crawl_delay > 10:
        issues.append(f'Crawl-delay of {crawl_delay}s may slow Googlebot indexing')

    return {
        'rules': rules,
        'sitemaps': sitemaps,
        'crawl_delay': crawl_delay,
        'issues': issues
    }


def parse_sitemap_xml(content: str) -> dict:
    """Parse XML sitemap and extract URL data."""
    issues = []
    urls = []
    url_count = 0
    lastmod_dates = []
    is_sitemap_index = False

    if not content or not content.strip():
        return {
            'url_count': 0,
            'lastmod_dates': [],
            'issues': ['Sitemap XML is empty or not provided'],
            'is_index': False
        }

    try:
        root = ET.fromstring(content)
    except ET.ParseError as e:
        return {
            'url_count': 0,
            'lastmod_dates': [],
            'issues': [f'XML parse error: {e}'],
            'is_index': False
        }

    tag = root.tag.lower()
    if 'sitemapindex' in tag:
        is_sitemap_index = True
        # Count child sitemaps
        for child in root:
            child_tag = child.tag.split('}')[-1].lower() if '}' in child.tag else child.tag.lower()
            if child_tag == 'sitemap':
                url_count += 1
                loc = child.find('.//{http://www.sitemaps.org/schemas/sitemap/0.9}loc')
                if loc is not None and loc.text:
                    urls.append(loc.text.strip())
    else:
        # Standard urlset
        for url_elem in root:
            url_tag = url_elem.tag.split('}')[-1].lower() if '}' in url_elem.tag else url_elem.tag.lower()
            if url_tag != 'url':
                continue
            url_count += 1
            loc = url_elem.find('.//{http://www.sitemaps.org/schemas/sitemap/0.9}loc')
            lastmod = url_elem.find('.//{http://www.sitemaps.org/schemas/sitemap/0.9}lastmod')
            if loc is not None and loc.text:
                urls.append(loc.text.strip())
            if lastmod is not None and lastmod.text:
                lastmod_dates.append(lastmod.text.strip())

    # Check URL count limits
    if url_count > 50000:
        issues.append(f'Sitemap exceeds 50,000 URL limit ({url_count} found)')
    if url_count == 0:
        issues.append('No URLs found in sitemap')
    elif url_count < 5:
        issues.append(f'Very few URLs in sitemap ({url_count}) — may be incomplete')

    # Check for stale lastmod dates
    stale_count = 0
    now_year = datetime.now(timezone.utc).year
    for date_str in lastmod_dates:
        year_match = re.match(r'(\d{4})', date_str)
        if year_match:
            year = int(year_match.group(1))
            if now_year - year > 2:
                stale_count += 1

    if stale_count > 0 and lastmod_dates:
        pct = int(stale_count / len(lastmod_dates) * 100)
        if pct > 30:
            issues.append(f'{pct}% of sitemap URLs have lastmod older than 2 years')

    return {
        'url_count': url_count,
        'sample_urls': urls[:10],
        'lastmod_dates': lastmod_dates[:10],
        'is_index': is_sitemap_index,
        'issues': issues
    }


def compute_score(robots_data: dict, sitemap_data: dict) -> int:
    """Score robots + sitemap health from 0-100."""
    score = 100
    critical_issues = [i for i in robots_data['issues'] if 'CRITICAL' in i]
    score -= len(critical_issues) * 40
    score -= len([i for i in robots_data['issues'] if 'CRITICAL' not in i]) * 10
    score -= len(sitemap_data['issues']) * 10
    return max(0, min(100, score))


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

    robots_txt = data.get('robots_txt', '')
    sitemap_xml = data.get('sitemap_xml', '')

    robots_data = parse_robots_txt(robots_txt) if robots_txt else {
        'rules': [], 'sitemaps': [], 'crawl_delay': None,
        'issues': ['robots.txt not provided']
    }
    sitemap_data = parse_sitemap_xml(sitemap_xml)
    score = compute_score(robots_data, sitemap_data)

    print(json.dumps({
        'robots': robots_data,
        'sitemap': sitemap_data,
        'score': score
    }, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()
