#!/usr/bin/env python3
"""Alt text generator for SEO-optimized image descriptions.

Reads image context from stdin as JSON and generates an SEO-friendly
alt text under 125 characters that includes the primary keyword naturally.

Usage:
    echo '{"heading": "Best Running Shoes", "keywords": ["running shoes for beginners"], "context": "Lightweight shoes on a track"}' | python3 alt-text-generator.py

Input (stdin or --input arg): JSON object with fields:
    heading   str        Section heading or image subject
    keywords  list[str]  Keywords to include naturally (first = primary)
    context   str        Additional context from the section body (optional)

Output (stdout): JSON object:
    {"alt_text": "str"}
"""

import json
import re
import sys


# ---------------------------------------------------------------------------
# Text utilities
# ---------------------------------------------------------------------------

def clean_heading(heading):
    """Strip markdown formatting from heading text."""
    text = re.sub(r'[`*_\[\]#]', '', heading)
    return text.strip()


def truncate_to_limit(text, limit=125):
    """Truncate text to character limit at a word boundary."""
    if len(text) <= limit:
        return text
    truncated = text[:limit]
    # Cut at last space to avoid breaking a word
    last_space = truncated.rfind(' ')
    if last_space > limit // 2:
        truncated = truncated[:last_space]
    return truncated.rstrip('.,;:')


def keyword_in_text(keyword, text):
    """Check if keyword (or its words) appear in text (case-insensitive)."""
    kw_lower = keyword.lower()
    text_lower = text.lower()
    if kw_lower in text_lower:
        return True
    # Check if all words of a multi-word keyword are present
    kw_words = kw_lower.split()
    if len(kw_words) > 1:
        return all(w in text_lower for w in kw_words)
    return False


def extract_visual_context(context, max_chars=80):
    """Extract a short visual description from section context text."""
    if not context:
        return ''
    # Strip markdown
    text = re.sub(r'\[([^\]]*)\]\([^\)]*\)', r'\1', context)
    text = re.sub(r'[`*_]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    # Use first sentence only
    first = re.split(r'(?<=[.!?])\s+', text)[0].strip()
    if len(first) > max_chars:
        words = first.split()
        first = ' '.join(words[:12]) + '...'
    return first


# ---------------------------------------------------------------------------
# Alt text templates
# ---------------------------------------------------------------------------

# Patterns for building natural alt text variants.
# Each template takes: subject, keyword, visual_detail
TEMPLATES = [
    "{subject} — {visual_detail}",
    "{keyword} shown as {subject}",
    "{subject} demonstrating {keyword}",
    "{visual_detail} featuring {keyword}",
    "{subject} with {keyword} highlighted",
]


def select_template(heading, primary_kw, visual_detail):
    """Pick the best template based on available data and keyword fit."""
    subject = clean_heading(heading)
    # Strip trailing punctuation from visual detail to avoid awkward joins
    detail = visual_detail.rstrip('.,;:') if visual_detail else ''

    # If heading already contains keyword, use a detail-forward template
    if keyword_in_text(primary_kw, subject):
        if detail:
            candidate = f"{subject} — {detail}"
        else:
            candidate = subject
        return candidate

    # Keyword not in heading — build subject + keyword combination
    if detail:
        candidate = f"{subject} — {detail} for {primary_kw}"
    else:
        candidate = f"{subject} related to {primary_kw}"

    return candidate


def build_alt_text(heading, keywords, context):
    """Generate SEO-friendly alt text under 125 chars.

    Strategy:
    1. Start with cleaned heading as subject
    2. Add visual context from section body
    3. Ensure primary keyword appears naturally
    4. Trim to 125 chars at word boundary
    5. Validate: no leading "image of", no keyword stuffing
    """
    primary_kw = keywords[0].lower() if keywords else ''
    subject = clean_heading(heading)
    visual_detail = extract_visual_context(context)

    # Build candidate alt text
    if primary_kw:
        candidate = select_template(subject, primary_kw, visual_detail)
    elif visual_detail:
        candidate = f"{subject} — {visual_detail}"
    else:
        candidate = subject

    # Remove any leading "image of / photo of / picture of"
    candidate = re.sub(
        r'^(image|photo|picture|screenshot|illustration)\s+(of|showing|depicting)\s+',
        '',
        candidate,
        flags=re.IGNORECASE
    ).strip()

    # Capitalize first letter
    if candidate:
        candidate = candidate[0].upper() + candidate[1:]

    # Ensure primary keyword is present — append lightly if missing
    if primary_kw and not keyword_in_text(primary_kw, candidate):
        suffix = f" for {primary_kw}"
        if len(candidate) + len(suffix) <= 125:
            candidate += suffix

    # Final length trim
    candidate = truncate_to_limit(candidate, 125)

    return candidate


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    # Read JSON from stdin
    try:
        raw = sys.stdin.read().strip()
        if not raw:
            print("Error: empty input on stdin", file=sys.stderr)
            sys.exit(1)
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"Error: invalid JSON input: {e}", file=sys.stderr)
        sys.exit(1)

    heading = data.get('heading', '')
    keywords = data.get('keywords', [])
    context = data.get('context', '')

    if isinstance(keywords, str):
        keywords = [k.strip() for k in keywords.split(',') if k.strip()]

    if not heading:
        print("Error: 'heading' field is required", file=sys.stderr)
        sys.exit(1)

    alt_text = build_alt_text(heading, keywords, context)

    # Warn if still over limit (shouldn't happen, but be safe)
    if len(alt_text) > 125:
        print(
            f"Warning: alt text is {len(alt_text)} chars, exceeds 125 limit",
            file=sys.stderr
        )

    print(json.dumps({"alt_text": alt_text}, ensure_ascii=False))


if __name__ == '__main__':
    main()
