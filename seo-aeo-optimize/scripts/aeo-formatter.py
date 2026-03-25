#!/usr/bin/env python3
"""
aeo-formatter.py — Format markdown articles for AI engine citation optimization.

Transformations applied:
  - Insert TL;DR summary block after first H1
  - Insert concise answer blocks (2-3 sentence summaries) after each H2
  - Enhance FAQ sections by wrapping Q&A pairs under H3 headings
  - Add Key Takeaways block if not already present
  - Preserve all existing content unchanged

Input (stdin): Markdown article text
Output (stdout): AEO-optimized markdown article

Stdlib: json, re, sys
"""

import re
import sys
import json


# Regex patterns
H1_PATTERN = re.compile(r'^(#\s+.+)$', re.MULTILINE)
H2_PATTERN = re.compile(r'^(##\s+.+)$', re.MULTILINE)
H3_PATTERN = re.compile(r'^(###\s+.+)$', re.MULTILINE)
FAQ_HEADING_PATTERN = re.compile(r'^##\s+.*(faq|frequently asked|question)', re.IGNORECASE)
TLDR_PATTERN = re.compile(r'\*\*TL;DR', re.IGNORECASE)
TAKEAWAYS_PATTERN = re.compile(r'^##\s+.*(key takeaway|takeaway|summary|conclusion)',
                                re.IGNORECASE | re.MULTILINE)
ANSWER_BLOCK_MARKER = '<!-- aeo:answer -->'
BARE_QUESTION_PATTERN = re.compile(r'^(\*\*)?([A-Z][^?]{10,80}\?)\*?\*?\s*$', re.MULTILINE)


def split_into_sections(text: str) -> list:
    """Split markdown into list of (heading_line, body_text) tuples."""
    lines = text.splitlines(keepends=True)
    sections = []
    current_heading = None
    current_body = []

    for line in lines:
        stripped = line.rstrip('\n')
        if re.match(r'^#{1,3}\s+', stripped):
            if current_heading is not None or current_body:
                sections.append((current_heading, ''.join(current_body)))
            current_heading = stripped
            current_body = []
        else:
            current_body.append(line)

    if current_heading is not None or current_body:
        sections.append((current_heading, ''.join(current_body)))

    return sections


def extract_first_sentence(text: str) -> str:
    """Extract up to first 2 sentences from a text block."""
    clean = text.strip()
    # Remove markdown formatting for sentence extraction
    clean = re.sub(r'\*\*(.+?)\*\*', r'\1', clean)
    clean = re.sub(r'\*(.+?)\*', r'\1', clean)
    clean = re.sub(r'`(.+?)`', r'\1', clean)
    clean = re.sub(r'\[(.+?)\]\(.+?\)', r'\1', clean)
    # Split on sentence boundaries
    sentences = re.split(r'(?<=[.!?])\s+', clean)
    # Return first 2 sentences, max 80 words total
    result_sentences = []
    word_count = 0
    for sent in sentences[:3]:
        words = sent.split()
        if word_count + len(words) > 80:
            break
        result_sentences.append(sent)
        word_count += len(words)
        if word_count >= 30:
            break
    return ' '.join(result_sentences) if result_sentences else ''


def make_tldr_block(first_section_body: str) -> str:
    """Generate a TL;DR block from the article's opening content."""
    summary = extract_first_sentence(first_section_body)
    if not summary:
        summary = 'See article sections below for key information.'
    return f'\n**TL;DR:** {summary}\n'


def make_answer_block(section_body: str, heading_text: str) -> str:
    """Generate a short direct-answer block for a section."""
    summary = extract_first_sentence(section_body)
    if not summary:
        return ''
    # Clean heading text for context
    clean_heading = re.sub(r'^#+\s+', '', heading_text).strip()
    return f'> **In brief:** {summary}\n'


def enhance_faq_section(body: str) -> str:
    """
    Convert plain Q&A patterns inside a FAQ section into H3+answer format.
    Detects: bold questions, lines ending in '?', and Q:/A: patterns.
    """
    lines = body.splitlines(keepends=True)
    result = []
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # Pattern 1: **Question?** bold question
        bold_q = re.match(r'^\*\*([^*]{10,120}\?)\*\*\s*$', stripped)
        # Pattern 2: Q: Question?
        q_prefix = re.match(r'^Q:\s*(.+\?)$', stripped, re.IGNORECASE)
        # Pattern 3: plain line ending in ? with capital start
        plain_q = (stripped.endswith('?') and len(stripped) > 15
                   and stripped[0].isupper() and not stripped.startswith('#'))

        if bold_q:
            question_text = bold_q.group(1).strip()
            result.append(f'### {question_text}\n')
            i += 1
            # Collect answer lines (until next question or blank-then-question)
            while i < len(lines):
                next_stripped = lines[i].strip()
                if (re.match(r'^\*\*[^*]{10,120}\?\*\*', next_stripped) or
                        re.match(r'^Q:\s*.+\?', next_stripped, re.IGNORECASE) or
                        re.match(r'^#{1,3}\s+', next_stripped)):
                    break
                # Strip A: prefix from answer lines
                clean_answer = re.sub(r'^A:\s*', '', lines[i], flags=re.IGNORECASE)
                result.append(clean_answer)
                i += 1
        elif q_prefix:
            question_text = q_prefix.group(1).strip()
            result.append(f'### {question_text}\n')
            i += 1
        elif plain_q and not stripped.startswith('-') and not stripped.startswith('*'):
            result.append(f'### {stripped}\n')
            i += 1
        else:
            result.append(line)
            i += 1

    return ''.join(result)


def has_key_takeaways(text: str) -> bool:
    """Return True if article already has a key takeaways or summary section."""
    return bool(TAKEAWAYS_PATTERN.search(text))


def generate_key_takeaways(sections: list) -> str:
    """Generate key takeaways bullets from H2 section summaries."""
    bullets = []
    for heading, body in sections:
        if heading and re.match(r'^##\s+', heading):
            summary = extract_first_sentence(body)
            if summary and len(summary) > 20:
                # Truncate to ~15 words
                words = summary.split()[:15]
                bullet = ' '.join(words)
                if not bullet.endswith('.'):
                    bullet += '.'
                bullets.append(f'- {bullet}')
            if len(bullets) >= 5:
                break

    if not bullets:
        return ''

    return '\n## Key Takeaways\n\n' + '\n'.join(bullets) + '\n'


def format_article(text: str) -> str:
    """Apply all AEO transformations to markdown article text."""
    sections = split_into_sections(text)
    if not sections:
        return text

    result_parts = []
    h1_processed = False
    tldr_added = False

    for idx, (heading, body) in enumerate(sections):
        is_h1 = heading and re.match(r'^#\s+', heading)
        is_h2 = heading and re.match(r'^##\s+', heading)
        is_faq = heading and FAQ_HEADING_PATTERN.match(heading)

        # Write heading
        if heading:
            result_parts.append(heading + '\n')

        # After H1: insert TL;DR if not already present
        if is_h1 and not tldr_added and not TLDR_PATTERN.search(text):
            tldr = make_tldr_block(body)
            if tldr:
                result_parts.append(tldr)
                tldr_added = True
            h1_processed = True

        # For FAQ sections: enhance Q&A formatting
        if is_faq:
            result_parts.append(enhance_faq_section(body))
            continue

        # For H2 sections: insert answer block before body if body has content
        if is_h2 and body.strip() and ANSWER_BLOCK_MARKER not in body:
            answer = make_answer_block(body, heading or '')
            if answer:
                result_parts.append(answer)

        result_parts.append(body)

    output = ''.join(result_parts)

    # Append key takeaways if not already present
    if not has_key_takeaways(output):
        takeaways = generate_key_takeaways(sections)
        if takeaways:
            output = output.rstrip() + '\n' + takeaways

    return output


def main():
    article = sys.stdin.read()
    if not article.strip():
        print('Error: No article content provided on stdin', file=sys.stderr)
        sys.exit(1)

    formatted = format_article(article)
    sys.stdout.write(formatted)


if __name__ == '__main__':
    main()
