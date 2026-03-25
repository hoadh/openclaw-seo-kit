#!/usr/bin/env python3
"""batch-runner.py — Batch process a keyword list through the SEO content pipeline.

Reads keywords from stdin (one per line) or a file path given as argv[1].
For each keyword: records status, timing, and any error.
Outputs a JSON batch report to stdout.

Single keyword failure does not halt the batch — all keywords are attempted.
Duplicate keywords (case-insensitive) are skipped after the first occurrence.

Usage:
    python3 batch-runner.py                       # reads from stdin
    python3 batch-runner.py keyword_list.txt      # reads from file

Output JSON schema:
    {
      "summary": {
        "total": int,
        "success": int,
        "failed": int,
        "skipped_duplicates": int,
        "avg_time_seconds": float,
        "total_time_seconds": float
      },
      "results": [
        {
          "keyword": str,
          "status": "success" | "failed" | "pending",
          "seo_score": int | null,
          "url": str | null,
          "time_seconds": float,
          "error": str | null
        },
        ...
      ]
    }
"""

import json
import os
import sys
import time


# ---------------------------------------------------------------------------
# Keyword loading
# ---------------------------------------------------------------------------

def load_keywords(source) -> list:
    """Read lines from a file object or path string, return non-empty stripped lines."""
    if isinstance(source, str):
        if not os.path.isfile(source):
            print(f"Error: keyword file not found: {source}", file=sys.stderr)
            sys.exit(1)
        with open(source, "r", encoding="utf-8") as fh:
            lines = fh.readlines()
    else:
        lines = source.readlines()

    return [line.strip() for line in lines if line.strip()]


def deduplicate(keywords: list) -> tuple:
    """Return (unique_keywords, skipped_count) preserving first-occurrence order."""
    seen = set()
    unique = []
    skipped = 0
    for kw in keywords:
        normalized = kw.lower()
        if normalized in seen:
            skipped += 1
        else:
            seen.add(normalized)
            unique.append(kw)
    return unique, skipped


# ---------------------------------------------------------------------------
# Single-keyword processing
# ---------------------------------------------------------------------------

def process_keyword(keyword: str) -> dict:
    """Record a keyword entry for the batch report.

    This script handles keyword list processing (dedup, validation, report
    generation). The actual seo-content-flow invocation per keyword is
    performed by the ClawFlow orchestrator, not by this script directly.
    Each entry is recorded as 'pending' for the orchestrator to fulfill.

    Returns a result dict with: keyword, status, seo_score, url, time_seconds, error.
    """
    start = time.monotonic()
    result = {
        "keyword":      keyword,
        "status":       "pending",
        "seo_score":    None,
        "url":          None,
        "time_seconds": 0.0,
        "error":        None,
    }
    result["time_seconds"] = round(time.monotonic() - start, 2)
    return result


# ---------------------------------------------------------------------------
# Report generation
# ---------------------------------------------------------------------------

def build_report(results: list, skipped_duplicates: int, total_elapsed: float) -> dict:
    """Aggregate per-keyword results into a summary report dict."""
    success = sum(1 for r in results if r["status"] == "success")
    failed  = sum(1 for r in results if r["status"] == "failed")
    times   = [r["time_seconds"] for r in results]
    avg     = round(sum(times) / len(times), 2) if times else 0.0

    return {
        "summary": {
            "total":               len(results),
            "success":             success,
            "failed":              failed,
            "skipped_duplicates":  skipped_duplicates,
            "avg_time_seconds":    avg,
            "total_time_seconds":  round(total_elapsed, 2),
        },
        "results": results,
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    # Determine input source
    if len(sys.argv) >= 2:
        source = sys.argv[1]
    else:
        source = sys.stdin

    raw_keywords = load_keywords(source)

    if not raw_keywords:
        report = build_report([], 0, 0.0)
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return

    keywords, skipped = deduplicate(raw_keywords)

    print(
        f"Batch start: {len(keywords)} unique keyword(s), "
        f"{skipped} duplicate(s) skipped",
        file=sys.stderr,
    )

    results = []
    batch_start = time.monotonic()

    for idx, keyword in enumerate(keywords, start=1):
        print(f"[{idx}/{len(keywords)}] Processing: {keyword}", file=sys.stderr)
        result = process_keyword(keyword)
        results.append(result)
        status_label = result["status"].upper()
        print(
            f"  -> {status_label} in {result['time_seconds']}s"
            + (f" | error: {result['error']}" if result["error"] else ""),
            file=sys.stderr,
        )

    total_elapsed = time.monotonic() - batch_start
    report = build_report(results, skipped, total_elapsed)

    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
