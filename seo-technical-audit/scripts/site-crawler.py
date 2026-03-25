#!/usr/bin/env python3
"""
site-crawler.py — Parse pre-fetched HTML pages for technical SEO signals.

Input (stdin): JSON object or array:
  {"url": "str", "max_pages": 20, "pages": [{"url":"", "html":"", "status":200}]}
  OR array of page objects directly.

Output (stdout): JSON array of page data objects with SEO signals extracted.

Stdlib: json, re, sys, urllib.parse, html.parser
"""

import json
import re
import sys
from html.parser import HTMLParser
from urllib.parse import urljoin, urlparse


class PageHTMLParser(HTMLParser):
    """Extract SEO-relevant elements from HTML."""

    def __init__(self, base_url: str = ''):
        super().__init__()
        self.base_url = base_url
        self.title = ''
        self.meta = {}
        self.headings = []
        self.links = []
        self.images = []
        self.scripts = []
        self.canonical = ''
        self.robots_meta = ''
        self.json_ld_blocks = []
        self._in_title = False
        self._in_script = False
        self._script_type = ''
        self._current_script = ''
        self._text_content = []
        self._in_body = False

    def handle_starttag(self, tag, attrs):
        attr_dict = dict(attrs)

        if tag == 'title':
            self._in_title = True

        elif tag == 'meta':
            name = attr_dict.get('name', '').lower()
            prop = attr_dict.get('property', '').lower()
            content = attr_dict.get('content', '')
            if name in ('description', 'keywords', 'robots', 'viewport'):
                self.meta[name] = content
            if name == 'robots':
                self.robots_meta = content
            if prop in ('og:title', 'og:description'):
                self.meta[prop] = content

        elif tag == 'link':
            rel = attr_dict.get('rel', '').lower()
            href = attr_dict.get('href', '')
            if rel == 'canonical' and href:
                self.canonical = href

        elif tag in ('h1', 'h2', 'h3', 'h4', 'h5', 'h6'):
            self._current_heading_tag = tag
            self._current_heading_text = []
            self._in_heading = True

        elif tag == 'a':
            href = attr_dict.get('href', '')
            anchor = attr_dict.get('title', '')
            if href:
                abs_url = urljoin(self.base_url, href)
                self.links.append({
                    'href': abs_url,
                    'anchor': anchor,
                    'is_internal': self._is_internal(abs_url)
                })

        elif tag == 'img':
            self.images.append({
                'src': attr_dict.get('src', ''),
                'alt': attr_dict.get('alt', ''),
                'width': attr_dict.get('width', ''),
                'height': attr_dict.get('height', ''),
                'loading': attr_dict.get('loading', '')
            })

        elif tag == 'script':
            self._in_script = True
            self._script_type = attr_dict.get('type', '')
            src = attr_dict.get('src', '')
            defer = 'defer' in attr_dict
            async_ = 'async' in attr_dict
            self._current_script = ''
            if src:
                self.scripts.append({
                    'src': src,
                    'type': self._script_type,
                    'defer': defer,
                    'async': async_,
                    'inline': False
                })

        elif tag == 'body':
            self._in_body = True

    def handle_endtag(self, tag):
        if tag == 'title':
            self._in_title = False

        elif tag == 'script':
            if self._in_script and self._script_type == 'application/ld+json':
                self.json_ld_blocks.append(self._current_script.strip())
            elif self._in_script and self._current_script.strip():
                self.scripts.append({
                    'src': None,
                    'type': self._script_type,
                    'inline': True,
                    'size': len(self._current_script)
                })
            self._in_script = False
            self._current_script = ''

        elif tag in ('h1', 'h2', 'h3', 'h4', 'h5', 'h6'):
            if hasattr(self, '_in_heading') and self._in_heading:
                text = ''.join(self._current_heading_text).strip()
                self.headings.append({'tag': self._current_heading_tag, 'text': text})
                self._in_heading = False

    def handle_data(self, data):
        if self._in_title:
            self.title += data
        if self._in_script:
            self._current_script += data
        if hasattr(self, '_in_heading') and self._in_heading:
            self._current_heading_text.append(data)
        if self._in_body and data.strip():
            self._text_content.append(data.strip())

    def _is_internal(self, url: str) -> bool:
        if not self.base_url:
            return False
        base_domain = urlparse(self.base_url).netloc
        link_domain = urlparse(url).netloc
        return base_domain == link_domain or not link_domain

    def get_word_count(self) -> int:
        text = ' '.join(self._text_content)
        return len(text.split())


def analyze_page(page: dict) -> dict:
    """Extract SEO signals from a single page dict."""
    url = page.get('url', '')
    html = page.get('html', '')
    status = page.get('status', 200)

    parser = PageHTMLParser(base_url=url)
    try:
        parser.feed(html)
    except Exception:
        pass

    h1_tags = [h for h in parser.headings if h['tag'] == 'h1']
    internal_links = [l for l in parser.links if l['is_internal']]
    external_scripts = [s for s in parser.scripts if not s.get('inline') and s.get('src')]
    blocking_scripts = [
        s for s in external_scripts
        if not s.get('defer') and not s.get('async')
    ]
    images_missing_alt = [i for i in parser.images if not i.get('alt')]

    return {
        'url': url,
        'status': status,
        'title': parser.title.strip(),
        'title_length': len(parser.title.strip()),
        'meta_description': parser.meta.get('description', ''),
        'meta_description_length': len(parser.meta.get('description', '')),
        'canonical': parser.canonical,
        'robots_meta': parser.robots_meta,
        'h1_count': len(h1_tags),
        'h1_text': h1_tags[0]['text'] if h1_tags else '',
        'headings': parser.headings,
        'word_count': parser.get_word_count(),
        'internal_links_count': len(internal_links),
        'internal_links': internal_links[:20],
        'images_count': len(parser.images),
        'images_missing_alt_count': len(images_missing_alt),
        'json_ld_count': len(parser.json_ld_blocks),
        'external_scripts_count': len(external_scripts),
        'blocking_scripts_count': len(blocking_scripts),
        'has_canonical': bool(parser.canonical),
        'has_meta_description': bool(parser.meta.get('description')),
        'is_noindex': 'noindex' in parser.robots_meta.lower()
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

    if isinstance(data, list):
        pages = data
    elif isinstance(data, dict):
        pages = data.get('pages', [])
    else:
        print(json.dumps({'error': 'Input must be JSON array or object with pages key'}),
              file=sys.stderr)
        sys.exit(1)

    max_pages = data.get('max_pages', 20) if isinstance(data, dict) else 20
    pages = pages[:max_pages]

    results = [analyze_page(p) for p in pages if isinstance(p, dict)]
    print(json.dumps(results, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()
