#!/usr/bin/env python3
"""
content-formatter.py

Reads article markdown from stdin, parses or injects YAML frontmatter,
calculates keyword density for specified keywords, and outputs formatted
article.md to stdout. Density stats are reported to stderr.

Usage:
    cat article.md | python3 content-formatter.py [--keywords "kw1,kw2"] [--slug "my-slug"]
    cat article.md | python3 content-formatter.py --keywords "SEO,keyword research" --slug "seo-guide"

Options:
    --keywords  Comma-separated list of keywords to measure density for
    --slug      Override or set the slug in frontmatter
    --title     Override or set the title in frontmatter
    --lang      Override or set the language field (en|vi)
"""

import importlib.util as _ilu
import json
import os
import re
import sys
from datetime import datetime, timezone


# ---------------------------------------------------------------------------
# Load shared frontmatter parser (stdlib importlib — no install required)
# ---------------------------------------------------------------------------

def _load_module(path, module_name):
    spec = _ilu.spec_from_file_location(module_name, path)
    mod = _ilu.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_scripts_dir = os.path.dirname(os.path.abspath(__file__))
_fp = _load_module(
    os.path.normpath(os.path.join(
        _scripts_dir, '..', '..', 'seo-shared-utils', 'scripts', 'frontmatter-parser.py'
    )),
    'frontmatter_parser'
)

# parse_frontmatter(text) -> (dict, str)
parse_frontmatter = _fp.parse_frontmatter


def serialize_frontmatter(fm: dict) -> str:
    """Serialize a flat dict to a YAML frontmatter block (--- ... ---)."""
    lines = ["---"]
    for key, value in fm.items():
        if value is None:
            continue
        str_val = str(value)
        # Quote values containing special YAML characters
        if any(c in str_val for c in [":", "#", "[", "]", "{", "}", ","]):
            str_val = f'"{str_val}"'
        lines.append(f"{key}: {str_val}")
    lines.append("---")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Keyword density analysis
# ---------------------------------------------------------------------------

def count_keyword_occurrences(text: str, keyword: str) -> int:
    """Count case-insensitive occurrences of keyword (whole-word for single terms)."""
    pattern = re.escape(keyword.lower())
    # For multi-word phrases, substring match is fine
    if " " in keyword:
        return len(re.findall(pattern, text.lower()))
    # For single words, match whole word
    return len(re.findall(r"\b" + pattern + r"\b", text.lower()))


def count_words(text: str) -> int:
    """Count words in text, stripping markdown syntax."""
    # Remove code blocks
    text = re.sub(r"```[\s\S]*?```", " ", text)
    text = re.sub(r"`[^`]+`", " ", text)
    # Remove HTML tags
    text = re.sub(r"<[^>]+>", " ", text)
    # Remove markdown links/images
    text = re.sub(r"!\[.*?\]\(.*?\)", " ", text)
    text = re.sub(r"\[.*?\]\(.*?\)", " ", text)
    # Remove heading markers, bold, italic
    text = re.sub(r"[#*_~>]", " ", text)
    words = [w for w in text.split() if w.strip()]
    return len(words)


def compute_density_stats(body: str, keywords: list[str]) -> list[dict]:
    """Return density stats for each keyword."""
    total_words = count_words(body)
    stats = []
    for kw in keywords:
        if not kw.strip():
            continue
        count = count_keyword_occurrences(body, kw.strip())
        density = (count / total_words * 100) if total_words > 0 else 0.0
        stats.append({
            "keyword": kw.strip(),
            "occurrences": count,
            "total_words": total_words,
            "density_pct": round(density, 2),
            "status": _density_status(density, keywords.index(kw) == 0),
        })
    return stats


def _density_status(density: float, is_primary: bool) -> str:
    """Return status label based on density thresholds."""
    if is_primary:
        if density < 1.0:
            return "under-optimized"
        if density > 2.5:
            return "over-optimized (stuffing risk)"
        return "optimal"
    else:
        if density < 0.5:
            return "low"
        if density > 1.5:
            return "high"
        return "optimal"


# ---------------------------------------------------------------------------
# Frontmatter enrichment
# ---------------------------------------------------------------------------

def enrich_frontmatter(fm: dict, overrides: dict) -> dict:
    """Merge CLI overrides into frontmatter, filling defaults for missing fields."""
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    # Apply overrides
    for key, val in overrides.items():
        if val:
            fm[key] = val

    # Fill missing required fields with defaults
    if "date" not in fm or not fm["date"]:
        fm["date"] = today
    if "language" not in fm or not fm["language"]:
        fm["language"] = "en"
    if "draft" not in fm:
        fm["draft"] = "false"

    # Normalize language value
    lang = str(fm.get("language", "en")).lower()
    if lang not in ("en", "vi"):
        lang = "en"
    fm["language"] = lang

    return fm


# ---------------------------------------------------------------------------
# Argument parsing (stdlib only)
# ---------------------------------------------------------------------------

def parse_args(argv: list[str]) -> dict:
    """Parse --key value pairs from argv."""
    args = {"keywords": [], "slug": "", "title": "", "lang": ""}
    i = 0
    while i < len(argv):
        arg = argv[i]
        if arg == "--keywords" and i + 1 < len(argv):
            raw = argv[i + 1]
            args["keywords"] = [k.strip() for k in raw.split(",") if k.strip()]
            i += 2
        elif arg == "--slug" and i + 1 < len(argv):
            args["slug"] = argv[i + 1]
            i += 2
        elif arg == "--title" and i + 1 < len(argv):
            args["title"] = argv[i + 1]
            i += 2
        elif arg == "--lang" and i + 1 < len(argv):
            args["lang"] = argv[i + 1]
            i += 2
        else:
            i += 1
    return args


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    args = parse_args(sys.argv[1:])

    # Read markdown from stdin
    raw = sys.stdin.read()
    if not raw.strip():
        sys.stderr.write("Error: no input provided on stdin\n")
        sys.exit(1)

    # Parse existing frontmatter
    fm, body = parse_frontmatter(raw)

    # Enrich frontmatter with CLI overrides and defaults
    overrides = {
        "slug": args["slug"],
        "title": args["title"],
        "language": args["lang"],
    }
    fm = enrich_frontmatter(fm, overrides)

    # Determine keywords from args or frontmatter
    keywords = args["keywords"]
    if not keywords and fm.get("keywords"):
        # Support comma-separated keywords in frontmatter
        keywords = [k.strip() for k in str(fm["keywords"]).split(",") if k.strip()]

    # Compute and report keyword density
    if keywords and body.strip():
        stats = compute_density_stats(body, keywords)
        sys.stderr.write("\n--- Keyword Density Report ---\n")
        sys.stderr.write(f"Total words: {stats[0]['total_words'] if stats else 0}\n")
        for s in stats:
            sys.stderr.write(
                f"  [{s['status']}] \"{s['keyword']}\": "
                f"{s['occurrences']} occurrences, {s['density_pct']}%\n"
            )
        sys.stderr.write("------------------------------\n\n")

    # Reassemble output
    fm_block = serialize_frontmatter(fm)
    output = fm_block + "\n\n" + body.lstrip("\n")
    print(output, end="")


if __name__ == "__main__":
    main()
