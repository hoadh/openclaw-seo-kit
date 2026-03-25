#!/usr/bin/env python3
"""SEO scoring dimension functions.

Contains all per-dimension scoring logic used by seo-score-calculator.py.
Each function returns (score: int, details: dict).

Dimensions and max scores:
    keyword_density   -> 20 pts
    readability       -> 25 pts
    heading_structure -> 20 pts
    internal_links    -> 15 pts
    meta_quality      -> 20 pts
"""

import re


# ---------------------------------------------------------------------------
# Syllable counting (English heuristic)
# ---------------------------------------------------------------------------

VOWELS = set('aeiouy')


def count_syllables_en(word):
    """Approximate English syllable count using vowel-group heuristic."""
    word = word.lower().rstrip('.,;:!?')
    if not word:
        return 1

    count = 0
    prev_vowel = False
    for ch in word:
        is_vowel = ch in VOWELS
        if is_vowel and not prev_vowel:
            count += 1
        prev_vowel = is_vowel

    # Silent trailing 'e'
    if word.endswith('e') and count > 1:
        count -= 1

    return max(1, count)


# ---------------------------------------------------------------------------
# Text splitting utilities
# ---------------------------------------------------------------------------

def split_sentences(text):
    """Split plain text into sentences by punctuation."""
    sentences = re.split(r'[.!?]+', text)
    return [s.strip() for s in sentences if s.strip()]


# ---------------------------------------------------------------------------
# Dimension: Keyword Density (20 pts max)
# ---------------------------------------------------------------------------

def score_keyword_density(words, primary_kw, secondary_kws):
    """Score keyword density across primary and secondary keywords."""
    total = len(words)
    if total == 0:
        return 0, {"score": 0, "details": "No words found", "primary_density": 0,
                   "primary_count": 0}

    plain_text = ' '.join(words)

    def kw_count(kw):
        kw_words = kw.lower().split()
        if len(kw_words) == 1:
            return words.count(kw_words[0])
        pattern = r'\b' + re.escape(' '.join(kw_words)) + r'\b'
        return len(re.findall(pattern, plain_text))

    primary_count = kw_count(primary_kw)
    primary_density = (primary_count / total) * 100 if total else 0

    if 1.0 <= primary_density <= 2.0:
        base = 20
    elif 0.5 <= primary_density < 1.0 or 2.0 < primary_density <= 3.0:
        base = 14
    else:
        base = 6

    sec_details = []
    sec_bonus = 0
    for kw in (secondary_kws or []):
        cnt = kw_count(kw)
        density = (cnt / total) * 100 if total else 0
        if 0.5 <= density <= 1.0:
            sec_bonus += 3
        sec_details.append(f"{kw}: {density:.1f}%")

    final_score = min(20, base + sec_bonus)
    details = (
        f"Primary '{primary_kw}': {primary_density:.1f}% ({primary_count} occurrences, "
        f"target 1-2%)"
    )
    if sec_details:
        details += "; Secondary: " + ", ".join(sec_details)

    return final_score, {
        "score": final_score,
        "details": details,
        "primary_density": round(primary_density, 2),
        "primary_count": primary_count,
    }


# ---------------------------------------------------------------------------
# Dimension: Readability (25 pts max)
# ---------------------------------------------------------------------------

def score_readability(plain_text, language):
    """Score readability using FK grade (EN) or sentence-length heuristic (VI)."""
    sentences = split_sentences(plain_text)
    words = re.findall(r"[a-zA-ZÀ-ÿ\u0100-\u024F\u1EA0-\u1EF9]+", plain_text.lower())

    if not sentences or not words:
        return 0, {"score": 0, "target": "N/A", "method": "none"}

    avg_sentence_len = len(words) / len(sentences)

    if language == 'vi':
        if 15 <= avg_sentence_len <= 20:
            pts = 25
        elif 12 <= avg_sentence_len < 15 or 20 < avg_sentence_len <= 25:
            pts = 18
        elif 10 <= avg_sentence_len < 12 or 25 < avg_sentence_len <= 30:
            pts = 10
        else:
            pts = 4
        return pts, {
            "score": pts,
            "avg_sentence_length": round(avg_sentence_len, 1),
            "target": "15-20 words/sentence",
            "method": "sentence-length-vi",
        }

    # English: Flesch-Kincaid Grade Level
    total_syllables = sum(count_syllables_en(w) for w in words)
    syllables_per_word = total_syllables / len(words)
    fk_grade = round(
        (0.39 * avg_sentence_len) + (11.8 * syllables_per_word) - 15.59, 1
    )

    if 8 <= fk_grade <= 10:
        pts = 25
    elif 7 <= fk_grade < 8 or 10 < fk_grade <= 12:
        pts = 18
    elif 6 <= fk_grade < 7 or 12 < fk_grade <= 14:
        pts = 10
    else:
        pts = 4

    return pts, {
        "score": pts,
        "grade_level": fk_grade,
        "target": "8-10",
        "avg_sentence_length": round(avg_sentence_len, 1),
        "syllables_per_word": round(syllables_per_word, 2),
        "method": "flesch-kincaid-en",
    }


# ---------------------------------------------------------------------------
# Dimension: Heading Structure (20 pts max)
# ---------------------------------------------------------------------------

def score_heading_structure(body, primary_kw):
    """Score H1/H2/H3 presence and keyword placement in headings."""
    h1_matches = re.findall(r'^# (.+)$', body, re.MULTILINE)
    h2_matches = re.findall(r'^## (.+)$', body, re.MULTILINE)
    h3_matches = re.findall(r'^### (.+)$', body, re.MULTILINE)

    pts = 0
    issues = []

    if len(h1_matches) == 1:
        pts += 8
    elif len(h1_matches) > 1:
        pts += 4
        issues.append(f"Multiple H1 headings found ({len(h1_matches)}); use exactly one")
    else:
        issues.append("No H1 heading found")

    if len(h2_matches) >= 2:
        pts += 6
    elif len(h2_matches) == 1:
        pts += 3
        issues.append("Only 1 H2 heading; recommend at least 2")
    else:
        issues.append("No H2 headings found")

    if h3_matches:
        pts += 3
    else:
        issues.append("No H3 headings; consider adding sub-sections")

    all_headings = h1_matches + h2_matches
    kw_lower = primary_kw.lower()
    if any(kw_lower in h.lower() for h in all_headings):
        pts += 3
    else:
        issues.append(f"Primary keyword '{primary_kw}' not found in H1 or H2 headings")

    return pts, {
        "score": pts,
        "h1_count": len(h1_matches),
        "h2_count": len(h2_matches),
        "h3_count": len(h3_matches),
        "issues": issues,
    }


# ---------------------------------------------------------------------------
# Dimension: Internal Links (15 pts max)
# ---------------------------------------------------------------------------

def score_internal_links(body, word_count):
    """Score internal (relative) link count against word-count-based target."""
    all_links = re.findall(r'(?<!!)\[([^\]]+)\]\(([^\)]+)\)', body)
    internal_links = [(txt, url) for txt, url in all_links
                      if not re.match(r'https?://', url)]
    count = len(internal_links)

    target = max(1, round(word_count / 300))
    diff = target - count

    if diff <= 0:
        pts = 15
    elif diff == 1:
        pts = 12
    elif diff == 2:
        pts = 8
    elif diff == 3:
        pts = 4
    else:
        pts = 0

    return pts, {
        "score": pts,
        "count": count,
        "recommended": target,
        "total_links": len(all_links),
    }


# ---------------------------------------------------------------------------
# Dimension: Meta Quality (20 pts max)
# ---------------------------------------------------------------------------

def score_meta_quality(meta, primary_kw):
    """Score meta_title and meta_description length and keyword presence."""
    title = meta.get('meta_title', '')
    desc = meta.get('meta_description', '')
    kw_lower = primary_kw.lower()

    pts = 0
    title_len = len(title)
    desc_len = len(desc)

    if 50 <= title_len <= 60:
        pts += 6
    elif 40 <= title_len < 50 or 60 < title_len <= 70:
        pts += 3

    if 120 <= desc_len <= 160:
        pts += 6
    elif 100 <= desc_len < 120 or 160 < desc_len <= 180:
        pts += 3

    if kw_lower in title.lower():
        pts += 4
    if kw_lower in desc.lower():
        pts += 4

    return pts, {
        "score": pts,
        "title_length": title_len,
        "desc_length": desc_len,
        "keyword_in_title": kw_lower in title.lower(),
        "keyword_in_desc": kw_lower in desc.lower(),
    }
