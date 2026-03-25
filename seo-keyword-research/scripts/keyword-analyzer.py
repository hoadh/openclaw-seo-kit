#!/usr/bin/env python3
"""
keyword-analyzer.py

Reads raw search results as JSON from stdin (list of objects with "title",
"snippet", "url" fields), performs TF-IDF-like keyword analysis, clusters
keywords, classifies search intent, and outputs keyword_map.json to stdout.

Usage:
    cat search_results.json | python3 keyword-analyzer.py [--keyword "primary kw"] [--lang en|vi]
"""

import json
import re
import sys
import math
import collections

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

STOPWORDS = {
    "a", "an", "the", "and", "or", "but", "in", "on", "at", "to", "for",
    "of", "with", "by", "from", "up", "about", "into", "through", "is",
    "are", "was", "were", "be", "been", "being", "have", "has", "had",
    "do", "does", "did", "will", "would", "could", "should", "may", "might",
    "it", "its", "this", "that", "these", "those", "i", "we", "you", "he",
    "she", "they", "what", "which", "who", "how", "when", "where", "why",
    "not", "no", "can", "if", "as", "so", "than", "then", "there", "their",
    "our", "your", "my", "his", "her", "all", "also", "just", "more", "any",
}

INTENT_SIGNALS = {
    "informational": [
        "how", "what", "why", "who", "when", "where", "guide", "tutorial",
        "tips", "examples", "explained", "definition", "learn", "understand",
    ],
    "commercial": [
        "best", "top", "review", "reviews", "compare", "comparison", "vs",
        "versus", "alternatives", "recommended", "rated", "ranked", "worth",
        "pros", "cons",
    ],
    "transactional": [
        "buy", "order", "purchase", "shop", "deal", "discount", "coupon",
        "price", "cost", "sale", "cheap", "free", "download", "sign up",
        "subscribe", "get",
    ],
    "navigational": [
        "login", "sign in", "official", "homepage", "website", "site",
        "contact", "support",
    ],
}


# ---------------------------------------------------------------------------
# Text helpers
# ---------------------------------------------------------------------------

def tokenize(text: str) -> list[str]:
    """Lowercase, strip punctuation, split into tokens."""
    text = text.lower()
    text = re.sub(r"[^\w\s]", " ", text)
    tokens = [t for t in text.split() if t and t not in STOPWORDS and len(t) > 2]
    return tokens


def extract_ngrams(tokens: list[str], n: int) -> list[str]:
    """Return n-gram strings from token list."""
    return [" ".join(tokens[i:i + n]) for i in range(len(tokens) - n + 1)]


def extract_questions(snippets: list[str]) -> list[str]:
    """Extract PAA-style questions from snippets."""
    questions = []
    for snippet in snippets:
        sentences = re.split(r"[.!]", snippet)
        for sentence in sentences:
            sentence = sentence.strip()
            if "?" in sentence and len(sentence) > 10:
                # Clean and normalise
                q = re.sub(r"\s+", " ", sentence).strip(" ?") + "?"
                if q not in questions:
                    questions.append(q)
    return questions[:10]


# ---------------------------------------------------------------------------
# TF-IDF-like term frequency analysis
# ---------------------------------------------------------------------------

def compute_tfidf(docs: list[list[str]]) -> dict[str, float]:
    """
    Compute a simple TF-IDF score per term across all documents.
    Returns {term: score} sorted descending.
    """
    n_docs = len(docs)
    if n_docs == 0:
        return {}

    tf_total: dict[str, int] = collections.Counter()
    df: dict[str, int] = collections.Counter()

    for doc in docs:
        tf_total.update(doc)
        for term in set(doc):
            df[term] += 1

    scores: dict[str, float] = {}
    for term, tf in tf_total.items():
        idf = math.log((n_docs + 1) / (df[term] + 1)) + 1.0
        scores[term] = tf * idf

    return scores


# ---------------------------------------------------------------------------
# Intent classification
# ---------------------------------------------------------------------------

def classify_intent(keyword: str, snippets: list[str]) -> str:
    """Classify search intent based on signal word matching."""
    text = (keyword + " " + " ".join(snippets)).lower()

    scores: dict[str, int] = {intent: 0 for intent in INTENT_SIGNALS}
    for intent, signals in INTENT_SIGNALS.items():
        for signal in signals:
            if signal in text:
                scores[intent] += 1

    # Priority: navigational > transactional > commercial > informational
    priority = ["navigational", "transactional", "commercial", "informational"]
    for intent in priority:
        if scores[intent] > 0:
            return intent
    return "informational"


# ---------------------------------------------------------------------------
# Volume heuristic
# ---------------------------------------------------------------------------

def estimate_volume(keyword: str, lsi_count: int, question_count: int) -> str:
    """Rough volume estimate based on keyword length and data richness."""
    word_count = len(keyword.split())
    if word_count <= 2 and lsi_count >= 10:
        return "high"
    if word_count <= 3 and lsi_count >= 5:
        return "medium"
    return "low"


# ---------------------------------------------------------------------------
# Clustering
# ---------------------------------------------------------------------------

def cluster_keywords(primary: str, keywords: list[str]) -> list[dict]:
    """
    Group keywords into clusters by word overlap with primary keyword tokens.
    Returns list of {name, keywords} dicts.
    """
    primary_tokens = set(tokenize(primary))
    clusters: dict[str, list[str]] = collections.defaultdict(list)

    for kw in keywords:
        kw_tokens = set(tokenize(kw))
        overlap = primary_tokens & kw_tokens
        if overlap:
            cluster_name = sorted(overlap, key=len, reverse=True)[0]
        else:
            # Fall back: use the first meaningful word
            kw_toks = [t for t in kw.split() if t not in STOPWORDS]
            cluster_name = kw_toks[0] if kw_toks else "general"
        clusters[cluster_name].append(kw)

    return [{"name": name, "keywords": kws} for name, kws in clusters.items()]


# ---------------------------------------------------------------------------
# Language detection
# ---------------------------------------------------------------------------

def detect_language(texts: list[str]) -> str:
    """Simple heuristic: Vietnamese if common VI chars found."""
    combined = " ".join(texts)
    vi_chars = re.findall(r"[àáâãèéêìíòóôõùúýăđơưạảấầẩẫậắặẵ]", combined, re.IGNORECASE)
    return "vi" if len(vi_chars) > 3 else "en"


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    # Parse optional CLI args
    args = sys.argv[1:]
    primary_keyword = ""
    lang_override = None

    i = 0
    while i < len(args):
        if args[i] == "--keyword" and i + 1 < len(args):
            primary_keyword = args[i + 1]
            i += 2
        elif args[i] == "--lang" and i + 1 < len(args):
            lang_override = args[i + 1]
            i += 2
        else:
            i += 1

    # Read search results from stdin
    raw = sys.stdin.read().strip()
    if not raw:
        sys.stderr.write("Error: no input provided on stdin\n")
        sys.exit(1)

    try:
        results = json.loads(raw)
    except json.JSONDecodeError as exc:
        sys.stderr.write(f"Error: invalid JSON input — {exc}\n")
        sys.exit(1)

    if not isinstance(results, list):
        sys.stderr.write("Error: input must be a JSON array of search result objects\n")
        sys.exit(1)

    # Extract text fields
    titles = [r.get("title", "") for r in results if isinstance(r, dict)]
    snippets = [r.get("snippet", "") for r in results if isinstance(r, dict)]
    urls = [r.get("url", "") for r in results if isinstance(r, dict)]

    all_texts = titles + snippets

    # Infer primary keyword from most frequent bigram if not provided
    if not primary_keyword:
        all_tokens = tokenize(" ".join(all_texts))
        bigrams = extract_ngrams(all_tokens, 2)
        if bigrams:
            freq = collections.Counter(bigrams)
            primary_keyword = freq.most_common(1)[0][0]
        elif all_tokens:
            primary_keyword = collections.Counter(all_tokens).most_common(1)[0][0]
        else:
            primary_keyword = "unknown"

    # Detect language
    language = lang_override if lang_override in ("en", "vi") else detect_language(all_texts)

    # TF-IDF scoring across documents (each result = one doc)
    docs = [tokenize(t + " " + s) for t, s in zip(titles, snippets)]
    scores = compute_tfidf(docs)

    # Exclude tokens that are part of primary keyword itself
    primary_tokens = set(tokenize(primary_keyword))
    filtered_scores = {
        term: score for term, score in scores.items()
        if term not in primary_tokens and len(term) > 2
    }

    # Top LSI keywords (single terms)
    top_terms = sorted(filtered_scores, key=lambda t: filtered_scores[t], reverse=True)
    lsi_keywords = top_terms[:20]

    # Long-tail: bigrams and trigrams not containing stopwords
    all_tokens_flat = tokenize(" ".join(all_texts))
    bigrams = extract_ngrams(all_tokens_flat, 2)
    trigrams = extract_ngrams(all_tokens_flat, 3)

    bigram_freq = collections.Counter(bigrams)
    trigram_freq = collections.Counter(trigrams)

    long_tail_candidates = (
        [bg for bg, c in bigram_freq.most_common(15) if c >= 2] +
        [tg for tg, c in trigram_freq.most_common(10) if c >= 2]
    )
    # Exclude duplicates and primary keyword itself
    long_tail = [lt for lt in long_tail_candidates if lt != primary_keyword][:15]

    # PAA questions
    paa_questions = extract_questions(snippets)

    # Merge long_tail with PAA questions
    for q in paa_questions:
        if q not in long_tail:
            long_tail.append(q)
    long_tail = long_tail[:20]

    # Classify intent
    search_intent = classify_intent(primary_keyword, snippets)

    # Volume estimate
    volume_estimate = estimate_volume(primary_keyword, len(lsi_keywords), len(paa_questions))

    # Cluster keywords
    all_kws = lsi_keywords + [lt for lt in long_tail if "?" not in lt]
    clusters = cluster_keywords(primary_keyword, all_kws)

    # Build output
    keyword_map = {
        "primary_keyword": primary_keyword,
        "search_intent": search_intent,
        "lsi_keywords": lsi_keywords,
        "long_tail": long_tail,
        "clusters": clusters,
        "volume_estimate": volume_estimate,
        "language": language,
    }

    print(json.dumps(keyword_map, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
