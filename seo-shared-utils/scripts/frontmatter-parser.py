#!/usr/bin/env python3
"""frontmatter-parser.py — Shared YAML frontmatter parsing utilities.

Provides two functions used across multiple SEO scripts:
  - parse_frontmatter(text) -> (dict, str)
      Parses leading YAML frontmatter from markdown text.
      Returns (meta_dict, body_text). Handles simple scalars,
      inline lists [a, b, c], block list sequences, and | block scalars.
      Stdlib only — no PyYAML dependency.

  - serialize_frontmatter(meta, body) -> str
      Serializes meta dict back to a YAML frontmatter block and
      concatenates body text, returning complete markdown string.

Usage (importlib pattern for kebab-case filename):
    import importlib.util, os
    def _load(path):
        spec = importlib.util.spec_from_file_location("frontmatter_parser", path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod
    _fp = _load(os.path.join(os.path.dirname(__file__),
                "../../seo-shared-utils/scripts/frontmatter-parser.py"))
    parse_frontmatter = _fp.parse_frontmatter
    serialize_frontmatter = _fp.serialize_frontmatter
"""

import re


def parse_frontmatter(text: str) -> tuple:
    """Extract YAML frontmatter and body from markdown text.

    Returns (meta_dict, body_text). Handles:
      - Simple key: value scalars
      - Inline lists: key: [a, b, c]
      - Block list sequences: key:\n  - item
      - Block scalars: key: |
    """
    meta = {}
    body = text

    if not text.startswith("---"):
        return meta, body

    # Find closing ---
    end_match = re.search(r"\n---\s*\n", text[3:])
    if not end_match:
        return meta, body

    raw_fm = text[3: end_match.start() + 3]
    body = text[end_match.end() + 3:]

    current_key = None
    block_lines = []
    in_block = False

    for line in raw_fm.splitlines():
        # Block scalar continuation
        if in_block:
            if line.startswith("  ") or line.strip() == "":
                block_lines.append(line.strip())
                continue
            else:
                meta[current_key] = "\n".join(block_lines).strip()
                in_block = False
                block_lines = []

        # Block list: key:\n  - item
        bk = re.match(r'^(\w[\w_-]*):\s*$', line.strip())
        if bk:
            current_key = bk.group(1)
            meta[current_key] = []
            continue

        if current_key and isinstance(meta.get(current_key), list):
            item = re.match(r'^\s*-\s+(.+)$', line)
            if item:
                meta[current_key].append(
                    item.group(1).strip().strip('"').strip("'")
                )
                continue
            else:
                current_key = None  # list ended

        # Key: value line
        kv_match = re.match(r'^(\w[\w_-]*):\s*(.*)', line)
        if kv_match:
            current_key = kv_match.group(1)
            value = kv_match.group(2).strip()
            if value == "|":
                in_block = True
                block_lines = []
            elif value.startswith('[') and value.endswith(']'):
                inner = value[1:-1]
                meta[current_key] = [
                    s.strip().strip('"').strip("'")
                    for s in inner.split(',') if s.strip()
                ]
            elif value.startswith('"') and value.endswith('"'):
                meta[current_key] = value[1:-1]
            elif value.startswith("'") and value.endswith("'"):
                meta[current_key] = value[1:-1]
            else:
                meta[current_key] = value

    # Flush remaining block scalar
    if in_block and block_lines:
        meta[current_key] = "\n".join(block_lines).strip()

    return meta, body


def serialize_frontmatter(meta: dict, body: str) -> str:
    """Serialize meta dict to YAML frontmatter block and prepend to body.

    Returns complete markdown string: frontmatter block + body text.
    Values containing special YAML characters are double-quoted.
    """
    lines = ["---"]
    for key, value in meta.items():
        if value is None:
            continue
        if isinstance(value, list):
            str_val = "[" + ", ".join(str(v) for v in value) + "]"
        else:
            str_val = str(value)
        # Quote values containing characters that need escaping in YAML
        if any(c in str_val for c in [":", "#", "[", "]", "{", "}", ","]):
            str_val = f'"{str_val}"'
        lines.append(f"{key}: {str_val}")
    lines.append("---")
    fm_block = "\n".join(lines)
    return fm_block + "\n\n" + body.lstrip("\n")
