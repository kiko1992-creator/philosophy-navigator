# validator.py
# M1: Schema validation, normalization helpers, duplicate detection
# All functions are standalone — no external dependencies

import re
from typing import Any


# ── Required schema ──────────────────────────────────────────
REQUIRED_KEYS = {
    "title":    str,
    "author":   str,
    "year":     int,
    "tradition": str,
}

OPTIONAL_KEYS = {
    "short_summary":    str,
    "central_argument": str,
    "key_concepts":     list,
    "related_books":    list,
    "source":           str,
}

VALID_SOURCES = {"curated", "open_library", ""}


# ── Normalization ─────────────────────────────────────────────
def normalize(text: str) -> str:
    """
    Lowercase, strip, collapse internal whitespace.
    Use this everywhere instead of raw .lower().

    Example:
        normalize("  Plato  ") -> "plato"
        normalize("Being and Time") -> "being and time"
    """
    if not isinstance(text, str):
        text = str(text)
    text = text.strip().lower()
    text = re.sub(r"\s+", " ", text)
    return text


# ── Schema validator ──────────────────────────────────────────
def validate_books(books: list[dict[str, Any]]) -> list[str]:
    """
    Validate all books against the schema.
    Returns list of warning strings.
    Prints warnings to console.
    App continues regardless — warnings only, no hard stops.

    Checks:
    - Required keys present
    - Correct types for required keys
    - source field is valid enum value
    - key_concepts and related_books are lists of strings
    """
    warnings = []

    for i, book in enumerate(books):
        title = book.get("title", f"[book #{i}]")
        prefix = f"  [WARN] #{i} {title!r}"

        # Check required keys and types
        for key, expected_type in REQUIRED_KEYS.items():
            if key not in book:
                msg = f"{prefix}: missing required field '{key}'"
                warnings.append(msg)
            elif not isinstance(book[key], expected_type):
                msg = (f"{prefix}: '{key}' should be {expected_type.__name__}, "
                       f"got {type(book[key]).__name__}")
                warnings.append(msg)

        # Check source enum
        source = book.get("source", "")
        if source not in VALID_SOURCES:
            msg = f"{prefix}: 'source' value {source!r} not in {VALID_SOURCES}"
            warnings.append(msg)

        # Check key_concepts is list of strings
        kc = book.get("key_concepts", [])
        if not isinstance(kc, list):
            warnings.append(f"{prefix}: 'key_concepts' must be a list")
        else:
            for j, c in enumerate(kc):
                if not isinstance(c, str):
                    warnings.append(f"{prefix}: key_concepts[{j}] is not a string")

        # Check related_books is list of strings
        rb = book.get("related_books", [])
        if not isinstance(rb, list):
            warnings.append(f"{prefix}: 'related_books' must be a list")
        else:
            for j, r in enumerate(rb):
                if not isinstance(r, str):
                    warnings.append(f"{prefix}: related_books[{j}] is not a string")

    # Print warnings
    if warnings:
        print(f"\n  [Schema] {len(warnings)} warning(s) found:")
        for w in warnings:
            print(w)
        print()

    return warnings


# ── Duplicate detector ────────────────────────────────────────
def find_duplicates(books: list[dict[str, Any]]) -> list[tuple[int, int, str]]:
    """
    Find books with the same normalized title+author.
    Returns list of (index_a, index_b, key) tuples.
    Prints duplicate pairs to console.

    Example output:
        [DUPLICATE] #12 and #47 share key 'republic|plato'
    """
    seen: dict[str, int] = {}
    duplicates: list[tuple[int, int, str]] = []

    for i, book in enumerate(books):
        title  = normalize(book.get("title",  ""))
        author = normalize(book.get("author", ""))
        key    = f"{title}|{author}"

        if key in seen:
            j = seen[key]
            duplicates.append((j, i, key))
            print(f"  [DUPLICATE] #{j} and #{i} share key {key!r}")
        else:
            seen[key] = i

    return duplicates


# ── Normalized search helpers ─────────────────────────────────
def match_author(book: dict[str, Any], query: str) -> bool:
    """Case-insensitive author match using normalize()."""
    return normalize(query) in normalize(book.get("author", ""))


def match_concept(book: dict[str, Any], query: str) -> bool:
    """Case-insensitive concept match across key_concepts list."""
    q = normalize(query)
    return any(q in normalize(c) for c in book.get("key_concepts", []))


def match_tradition(book: dict[str, Any], query: str) -> bool:
    """Case-insensitive tradition match using normalize()."""
    return normalize(query) in normalize(book.get("tradition", ""))


def match_title(book: dict[str, Any], query: str) -> bool:
    """Case-insensitive title match using normalize()."""
    return normalize(query) in normalize(book.get("title", ""))