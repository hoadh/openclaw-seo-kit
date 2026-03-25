#!/usr/bin/env python3
"""
outline-validator.py

Validates an SEO article outline JSON against structural and content rules.

Usage:
    python3 outline-validator.py [path/to/outline.json]
    cat outline.json | python3 outline-validator.py

Exit codes:
    0 — valid
    1 — validation errors found (JSON error list printed to stdout)
    2 — input error (file not found, invalid JSON)
"""

import json
import sys

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

META_TITLE_MAX = 60
META_DESC_MAX = 160
ALLOWED_SCHEMA_TYPES = {"Article", "HowTo", "FAQ", "Product"}
REQUIRED_FIELDS = {"title", "meta_title", "meta_description", "slug", "schema_type", "sections", "faq"}


# ---------------------------------------------------------------------------
# Validators
# ---------------------------------------------------------------------------

def validate_required_fields(outline: dict, errors: list) -> None:
    """Check all top-level required fields exist and are non-empty."""
    for field in REQUIRED_FIELDS:
        if field not in outline:
            errors.append({
                "field": field,
                "error": f"Required field '{field}' is missing",
            })
        elif outline[field] is None or outline[field] == "" or outline[field] == [] or outline[field] == {}:
            errors.append({
                "field": field,
                "error": f"Required field '{field}' must not be empty",
            })


def validate_meta_lengths(outline: dict, errors: list) -> None:
    """Validate meta_title and meta_description character limits."""
    meta_title = outline.get("meta_title", "")
    if isinstance(meta_title, str) and len(meta_title) > META_TITLE_MAX:
        errors.append({
            "field": "meta_title",
            "error": f"meta_title is {len(meta_title)} chars — must be {META_TITLE_MAX} or fewer",
            "value": meta_title,
        })

    meta_desc = outline.get("meta_description", "")
    if isinstance(meta_desc, str) and len(meta_desc) > META_DESC_MAX:
        errors.append({
            "field": "meta_description",
            "error": f"meta_description is {len(meta_desc)} chars — must be {META_DESC_MAX} or fewer",
            "value": meta_desc,
        })


def validate_schema_type(outline: dict, errors: list) -> None:
    """Validate schema_type is one of the allowed values."""
    schema_type = outline.get("schema_type")
    if schema_type and schema_type not in ALLOWED_SCHEMA_TYPES:
        errors.append({
            "field": "schema_type",
            "error": f"schema_type '{schema_type}' is not allowed. Must be one of: {sorted(ALLOWED_SCHEMA_TYPES)}",
            "value": schema_type,
        })


def validate_heading_hierarchy(outline: dict, errors: list) -> None:
    """
    Validate H2/H3 hierarchy:
    - Every section must have level == 2
    - Every subsection must have level == 3
    - No H3 may exist without a parent H2 (enforced by structure)
    - Each section must have a non-empty heading
    """
    sections = outline.get("sections")
    if not isinstance(sections, list):
        return  # Already caught by required field check

    for i, section in enumerate(sections):
        if not isinstance(section, dict):
            errors.append({
                "field": f"sections[{i}]",
                "error": "Section must be a JSON object",
            })
            continue

        # Check H2 level
        level = section.get("level")
        if level != 2:
            errors.append({
                "field": f"sections[{i}].level",
                "error": f"Section level must be 2, got {level!r}",
            })

        # Check heading present
        heading = section.get("heading", "")
        if not isinstance(heading, str) or not heading.strip():
            errors.append({
                "field": f"sections[{i}].heading",
                "error": "Section heading must be a non-empty string",
            })

        # Check target_keywords
        target_kws = section.get("target_keywords")
        if not isinstance(target_kws, list) or len(target_kws) == 0:
            errors.append({
                "field": f"sections[{i}].target_keywords",
                "error": "target_keywords must be a non-empty array",
            })

        # Validate subsections (H3s)
        subsections = section.get("subsections", [])
        if not isinstance(subsections, list):
            errors.append({
                "field": f"sections[{i}].subsections",
                "error": "subsections must be an array",
            })
            continue

        for j, sub in enumerate(subsections):
            if not isinstance(sub, dict):
                errors.append({
                    "field": f"sections[{i}].subsections[{j}]",
                    "error": "Subsection must be a JSON object",
                })
                continue

            sub_level = sub.get("level")
            if sub_level != 3:
                errors.append({
                    "field": f"sections[{i}].subsections[{j}].level",
                    "error": f"Subsection level must be 3, got {sub_level!r}",
                })

            sub_heading = sub.get("heading", "")
            if not isinstance(sub_heading, str) or not sub_heading.strip():
                errors.append({
                    "field": f"sections[{i}].subsections[{j}].heading",
                    "error": "Subsection heading must be a non-empty string",
                })


def validate_faq(outline: dict, errors: list) -> None:
    """Validate faq is an array; each item has question and answer_hint."""
    faq = outline.get("faq")
    if not isinstance(faq, list):
        return  # Already caught by required field check

    for i, item in enumerate(faq):
        if not isinstance(item, dict):
            errors.append({
                "field": f"faq[{i}]",
                "error": "FAQ item must be a JSON object",
            })
            continue

        if not item.get("question", "").strip():
            errors.append({
                "field": f"faq[{i}].question",
                "error": "FAQ question must be a non-empty string",
            })

        if not item.get("answer_hint", "").strip():
            errors.append({
                "field": f"faq[{i}].answer_hint",
                "error": "FAQ answer_hint must be a non-empty string",
            })


def validate_slug(outline: dict, errors: list) -> None:
    """Validate slug is URL-safe (lowercase, hyphens, numbers only)."""
    import re
    slug = outline.get("slug", "")
    if isinstance(slug, str) and slug:
        if not re.match(r"^[a-z0-9]+(?:-[a-z0-9]+)*$", slug):
            errors.append({
                "field": "slug",
                "error": "slug must contain only lowercase letters, numbers, and hyphens (no leading/trailing hyphens)",
                "value": slug,
            })


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def load_outline() -> dict:
    """Load outline JSON from file path arg or stdin."""
    if len(sys.argv) > 1:
        path = sys.argv[1]
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            sys.stderr.write(f"Error: file not found — {path}\n")
            sys.exit(2)
        except json.JSONDecodeError as exc:
            sys.stderr.write(f"Error: invalid JSON in {path} — {exc}\n")
            sys.exit(2)
    else:
        raw = sys.stdin.read().strip()
        if not raw:
            sys.stderr.write("Error: no input provided (pipe outline.json or pass file path)\n")
            sys.exit(2)
        try:
            return json.loads(raw)
        except json.JSONDecodeError as exc:
            sys.stderr.write(f"Error: invalid JSON from stdin — {exc}\n")
            sys.exit(2)


def main() -> None:
    outline = load_outline()

    if not isinstance(outline, dict):
        sys.stderr.write("Error: outline must be a JSON object\n")
        sys.exit(2)

    errors: list = []

    validate_required_fields(outline, errors)
    validate_meta_lengths(outline, errors)
    validate_schema_type(outline, errors)
    validate_heading_hierarchy(outline, errors)
    validate_faq(outline, errors)
    validate_slug(outline, errors)

    if errors:
        print(json.dumps({"valid": False, "error_count": len(errors), "errors": errors}, indent=2))
        sys.exit(1)
    else:
        print(json.dumps({"valid": True, "error_count": 0, "errors": []}, indent=2))
        sys.exit(0)


if __name__ == "__main__":
    main()
