#!/usr/bin/env python3
"""Image prompt builder for SEO article images.

Reads a markdown article (from file path arg or stdin), parses H2 sections,
and generates descriptive image prompts for a featured image and one image
per H2 section.

Usage:
    python3 image-prompt-builder.py <article.md>
    cat article.md | python3 image-prompt-builder.py

Output (stdout):
    JSON array of image prompt objects:
    [
      {
        "type": "featured",
        "heading": "Article Title",
        "prompt": "...",
        "filename": "featured-article-slug.webp"
      },
      {
        "type": "section",
        "heading": "H2 Section Heading",
        "prompt": "...",
        "filename": "h2-section-heading.webp"
      }
    ]
"""

import json
import os
import re
import sys


# ---------------------------------------------------------------------------
# Frontmatter parsing
# ---------------------------------------------------------------------------

def parse_frontmatter(text):
    """Extract YAML frontmatter and body from markdown."""
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
                meta[block_key].append(
                    item.group(1).strip().strip('"').strip("'"))
            else:
                block_key = None

    return meta, body


# ---------------------------------------------------------------------------
# Filename utilities
# ---------------------------------------------------------------------------

def heading_to_filename(heading, prefix=''):
    """Convert heading text to a kebab-case webp filename."""
    name = heading.lower()
    # Remove markdown formatting
    name = re.sub(r'[`*_\[\]#]', '', name)
    # Replace non-alphanumeric (except spaces) with space
    name = re.sub(r'[^a-z0-9\s]', ' ', name)
    # Collapse whitespace and replace with hyphens
    name = re.sub(r'\s+', '-', name.strip())
    # Remove consecutive hyphens
    name = re.sub(r'-+', '-', name).strip('-')

    if prefix:
        return f"{prefix}-{name}.webp"
    return f"{name}.webp"


def article_slug(meta, h1_title):
    """Derive article slug from frontmatter slug field or H1 title."""
    slug = meta.get('slug', '')
    if slug:
        return slug.lower().replace(' ', '-')
    return heading_to_filename(h1_title).replace('.webp', '')


# ---------------------------------------------------------------------------
# Section parsing
# ---------------------------------------------------------------------------

def parse_sections(body):
    """Parse H2 sections from article body.

    Returns list of (heading_text, section_body) tuples.
    Stops at H2 boundaries.
    """
    sections = []
    # Split on H2 boundaries, keeping the delimiter
    parts = re.split(r'^(## .+)$', body, flags=re.MULTILINE)

    # parts alternates: [pre-h2-content, h2-heading, section-body, h2-heading, ...]
    i = 1
    while i < len(parts) - 1:
        heading = parts[i].lstrip('#').strip()
        section_body = parts[i + 1] if i + 1 < len(parts) else ''
        sections.append((heading, section_body.strip()))
        i += 2

    return sections


def extract_section_context(section_body, max_words=40):
    """Extract first meaningful sentence from a section for prompt context."""
    # Remove sub-headings, code blocks, lists
    text = re.sub(r'```[\s\S]*?```', '', section_body)
    text = re.sub(r'^#{1,6}\s+.+$', '', text, flags=re.MULTILINE)
    text = re.sub(r'^\s*[-*+]\s+', '', text, flags=re.MULTILINE)
    text = re.sub(r'\[([^\]]*)\]\([^\)]*\)', r'\1', text)
    text = re.sub(r'[\*_`]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()

    # Take first sentence
    sentences = re.split(r'(?<=[.!?])\s+', text)
    if not sentences:
        return ''

    first = sentences[0].strip()
    words = first.split()
    if len(words) > max_words:
        first = ' '.join(words[:max_words]) + '...'
    return first


# ---------------------------------------------------------------------------
# Prompt generation
# ---------------------------------------------------------------------------

# Style suffix appended to all prompts for visual consistency
STYLE_SUFFIX = (
    "photorealistic, clean composition, professional photography, "
    "soft natural lighting, no text overlays, no watermarks"
)


def build_featured_prompt(primary_kw, title, meta_description):
    """Generate a featured image prompt from article metadata."""
    # Use meta_description as context if available
    context_hint = ''
    if meta_description:
        # Extract first clause of meta description
        first_clause = re.split(r'[,;.]', meta_description)[0].strip()
        if first_clause and len(first_clause) > 10:
            context_hint = f", {first_clause.lower()}"

    subject = primary_kw if primary_kw else title
    prompt = (
        f"{subject}{context_hint}, "
        f"hero banner composition suitable for a blog article about {title}, "
        f"{STYLE_SUFFIX}"
    )
    return prompt


def build_section_prompt(heading, section_context, primary_kw):
    """Generate a section image prompt from heading and body context."""
    context_part = ''
    if section_context and len(section_context) > 15:
        context_part = f", {section_context[:120]}"

    kw_hint = ''
    if primary_kw and primary_kw.lower() not in heading.lower():
        kw_hint = f" related to {primary_kw}"

    prompt = (
        f"Visual illustration of '{heading}'{kw_hint}{context_part}, "
        f"inline article image, {STYLE_SUFFIX}"
    )
    return prompt


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    # Read article from file arg or stdin
    if len(sys.argv) >= 2:
        article_path = sys.argv[1]
        if not os.path.isfile(article_path):
            print(f"Error: file not found: {article_path}", file=sys.stderr)
            sys.exit(1)
        with open(article_path, 'r', encoding='utf-8') as f:
            raw = f.read()
    else:
        raw = sys.stdin.read()

    if not raw.strip():
        print("Error: empty article input", file=sys.stderr)
        sys.exit(1)

    meta, body = parse_frontmatter(raw)

    primary_kw = meta.get('primary_keyword', '')
    meta_description = meta.get('meta_description', '')
    meta_title = meta.get('meta_title', '')

    # Extract H1 title
    h1_match = re.search(r'^# (.+)$', body, re.MULTILINE)
    h1_title = h1_match.group(1).strip() if h1_match else meta_title or 'Article'
    display_title = meta_title or h1_title

    slug = article_slug(meta, h1_title)

    results = []

    # Featured image
    featured_prompt = build_featured_prompt(primary_kw, display_title, meta_description)
    results.append({
        'type': 'featured',
        'heading': display_title,
        'prompt': featured_prompt,
        'filename': f"featured-{slug}.webp"
    })

    # Section images (one per H2)
    sections = parse_sections(body)
    for heading, section_body in sections:
        # Skip navigation-like sections
        if re.match(r'^(table of contents|toc|references|bibliography)$',
                    heading.lower()):
            continue

        context = extract_section_context(section_body)
        section_prompt = build_section_prompt(heading, context, primary_kw)
        filename = heading_to_filename(heading)

        results.append({
            'type': 'section',
            'heading': heading,
            'prompt': section_prompt,
            'filename': filename
        })

    print(json.dumps(results, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()
