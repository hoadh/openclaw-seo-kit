#!/usr/bin/env python3
"""SEO score calculator for markdown articles.

Reads a markdown file with YAML frontmatter and scores it across
5 SEO dimensions by delegating to seo-scoring-dimensions.py.
Outputs a JSON score report to stdout.

Usage:
    python3 seo-score-calculator.py <article.md>

Scoring dimensions (imported from seo-scoring-dimensions):
    keyword_density   20 pts
    readability       25 pts
    heading_structure 20 pts
    internal_links    15 pts
    meta_quality      20 pts
    ─────────────────────────
    total            100 pts
"""

import json
import os
import re
import sys

# Local import — kebab-case filename requires importlib since Python
# identifiers cannot contain hyphens.
import importlib.util as _ilu


def _load_module(path, module_name):
    """Load a Python module from an absolute file path."""
    spec = _ilu.spec_from_file_location(module_name, path)
    mod = _ilu.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_scripts_dir = os.path.dirname(os.path.abspath(__file__))

# Load scoring dimensions (sibling script)
_dims = _load_module(
    os.path.join(_scripts_dir, 'seo-scoring-dimensions.py'),
    'seo_scoring_dimensions'
)
score_keyword_density   = _dims.score_keyword_density
score_readability       = _dims.score_readability
score_heading_structure = _dims.score_heading_structure
score_internal_links    = _dims.score_internal_links
score_meta_quality      = _dims.score_meta_quality

# Load shared frontmatter parser
_fp = _load_module(
    os.path.normpath(os.path.join(
        _scripts_dir, '..', '..', 'seo-shared-utils', 'scripts', 'frontmatter-parser.py'
    )),
    'frontmatter_parser'
)
parse_frontmatter = _fp.parse_frontmatter


# ---------------------------------------------------------------------------
# Text utilities
# ---------------------------------------------------------------------------

def strip_markdown(text):
    """Remove markdown syntax to expose plain word content."""
    text = re.sub(r'```[\s\S]*?```', ' ', text)
    text = re.sub(r'`[^`]+`', ' ', text)
    text = re.sub(r'!\[[^\]]*\]\([^\)]*\)', ' ', text)
    text = re.sub(r'\[([^\]]*)\]\([^\)]*\)', r'\1', text)
    text = re.sub(r'^#+\s+', '', text, flags=re.MULTILINE)
    text = re.sub(r'[\*_]{1,3}([^\*_]+)[\*_]{1,3}', r'\1', text)
    text = re.sub(r'<[^>]+>', ' ', text)
    return text


def tokenize_words(text):
    """Return list of lowercase words from plain text."""
    return re.findall(r"[a-zA-ZÀ-ÿ\u0100-\u024F\u1EA0-\u1EF9]+", text.lower())


# ---------------------------------------------------------------------------
# Suggestions builder
# ---------------------------------------------------------------------------

def build_suggestions(il_details, hs_details, mq_details, rd_details,
                       kd_score, rd_score):
    """Generate ordered actionable suggestions from dimension detail dicts."""
    suggestions = []

    if il_details.get('count', 0) < il_details.get('recommended', 1):
        gap = il_details['recommended'] - il_details['count']
        suggestions.append(
            f"Add {gap} more internal link(s) "
            f"(have {il_details['count']}, target {il_details['recommended']})"
        )

    if rd_score < 18:
        grade = rd_details.get('grade_level')
        avg_sl = rd_details.get('avg_sentence_length')
        if grade is not None:
            suggestions.append(
                f"Improve readability: FK grade {grade} outside 8-10 target; "
                "shorten sentences and use simpler vocabulary"
            )
        elif avg_sl is not None:
            suggestions.append(
                f"Improve readability: avg sentence length {avg_sl} words; "
                "target 15-20 words/sentence for Vietnamese"
            )

    for issue in hs_details.get('issues', []):
        suggestions.append(issue)

    title_len = mq_details.get('title_length', 0)
    desc_len = mq_details.get('desc_length', 0)

    if title_len < 50:
        suggestions.append(
            f"Expand meta_title to 50-60 chars (currently {title_len})"
        )
    elif title_len > 60:
        suggestions.append(
            f"Shorten meta_title to 50-60 chars (currently {title_len})"
        )
    if desc_len < 120:
        suggestions.append(
            f"Expand meta_description to 120-160 chars (currently {desc_len})"
        )
    elif desc_len > 160:
        suggestions.append(
            f"Shorten meta_description to 120-160 chars (currently {desc_len})"
        )
    if not mq_details.get('keyword_in_title'):
        suggestions.append("Include primary keyword in meta_title")
    if not mq_details.get('keyword_in_desc'):
        suggestions.append("Include primary keyword in meta_description")

    if kd_score < 14:
        suggestions.append(
            "Adjust primary keyword density toward 1-2% of total word count"
        )

    return suggestions


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    if len(sys.argv) < 2:
        print("Usage: seo-score-calculator.py <article.md>", file=sys.stderr)
        sys.exit(1)

    article_path = sys.argv[1]
    if not os.path.isfile(article_path):
        print(f"Error: file not found: {article_path}", file=sys.stderr)
        sys.exit(1)

    with open(article_path, 'r', encoding='utf-8') as f:
        raw = f.read()

    meta, body = parse_frontmatter(raw)

    primary_kw = meta.get('primary_keyword', '').lower()
    secondary_kws = meta.get('secondary_keywords', [])
    if isinstance(secondary_kws, str):
        secondary_kws = [s.strip() for s in secondary_kws.split(',')]
    # Support both 'language' and 'lang' frontmatter fields; 'language' takes precedence
    language = (meta.get('language') or meta.get('lang') or 'en').lower()

    if not primary_kw:
        print("Warning: no primary_keyword in frontmatter; keyword scores will be 0",
              file=sys.stderr)

    plain = strip_markdown(body)
    words = tokenize_words(plain)
    word_count = len(words)

    kd_score, kd_details = score_keyword_density(words, primary_kw, secondary_kws)
    rd_score, rd_details = score_readability(plain, language)
    hs_score, hs_details = score_heading_structure(body, primary_kw)
    il_score, il_details = score_internal_links(body, word_count)
    mq_score, mq_details = score_meta_quality(meta, primary_kw)

    overall = kd_score + rd_score + hs_score + il_score + mq_score

    suggestions = build_suggestions(
        il_details, hs_details, mq_details, rd_details, kd_score, rd_score
    )

    report = {
        "overall_score": overall,
        "word_count": word_count,
        "language": language,
        "breakdown": {
            "keyword_density": kd_details,
            "readability": rd_details,
            "heading_structure": hs_details,
            "internal_links": il_details,
            "meta_quality": mq_details,
        },
        "suggestions": suggestions,
    }

    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()
