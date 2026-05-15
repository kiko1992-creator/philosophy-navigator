# fetcher.py
# Fetch philosophical book data from Open Library API
# No API key required — completely free
# Docs: https://openlibrary.org/developers/api

import json
import time
import requests
from pathlib import Path

# ── Paths ──────────────────────────────────────────────────────────────────
DATA_DIR  = Path(__file__).parent.parent / "data"
RAW_DIR   = DATA_DIR / "raw_api"
BOOKS_FILE = DATA_DIR / "books.json"

# ── Philosophical search queries ───────────────────────────────────────────
# Each entry is (search_query, tradition_tag)
# We search Open Library by subject or author and tag results
PHILOSOPHY_SEARCHES = [
    ("plato",                    "Ancient Greek"),
    ("aristotle philosophy",     "Ancient Greek"),
    ("stoicism epictetus",       "Stoicism"),
    ("marcus aurelius",          "Stoicism"),
    ("kant critique",            "German Idealism"),
    ("hegel phenomenology",      "German Idealism"),
    ("nietzsche",                "Existentialism"),
    ("heidegger",                "Existentialism"),
    ("sartre existentialism",    "Existentialism"),
    ("john rawls justice",       "Political Philosophy"),
    ("thomas hobbes",            "Political Philosophy"),
    ("john locke",               "Political Philosophy"),
    ("david hume",               "Empiricism"),
    ("descartes",                "Rationalism"),
    ("spinoza ethics",           "Rationalism"),
    ("wittgenstein",             "Analytic Philosophy"),
    ("bertrand russell",         "Analytic Philosophy"),
    ("michel foucault",          "Post-structuralism"),
    ("simone de beauvoir",       "Existentialism"),
    ("confucius analects",       "Eastern Philosophy"),
]

BASE_URL = "https://openlibrary.org/search.json"


def fetch_search(query, limit=10):
    """
    Search Open Library for books matching a query.
    Returns list of raw result dicts from the API.
    """
    params = {
        "q"     : query,
        "fields": "key,title,author_name,first_publish_year,subject,ia",
        "limit" : limit,
    }
    try:
        response = requests.get(BASE_URL, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()
        return data.get("docs", [])
    except requests.RequestException as e:
        print(f"  Warning: fetch failed for '{query}': {e}")
        return []


def clean_book_record(doc, tradition):
    """
    Convert a raw Open Library doc into our books.json format.
    Fills in defaults for missing fields.
    """
    title   = doc.get("title", "Unknown Title")
    authors = doc.get("author_name", ["Unknown Author"])
    author  = authors[0] if authors else "Unknown Author"
    year    = doc.get("first_publish_year", 0) or 0
    subjects = doc.get("subject", [])

    # Extract up to 5 relevant concepts from subjects
    key_concepts = []
    for subj in subjects[:20]:
        subj_lower = subj.lower()
        # Filter for meaningful philosophical subjects
        if any(word in subj_lower for word in [
            "ethics", "mind", "justice", "knowledge", "being",
            "freedom", "truth", "reason", "soul", "god", "nature",
            "politics", "virtue", "consciousness", "language", "logic",
            "metaphysics", "epistemology", "ontology", "morality"
        ]):
            key_concepts.append(subj.lower())
        if len(key_concepts) >= 5:
            break

    # Default concepts if none found
    if not key_concepts:
        key_concepts = ["philosophy"]

    return {
        "title"          : title,
        "author"         : author,
        "year"           : year,
        "tradition"      : tradition,
        "key_concepts"   : key_concepts,
        "short_summary"  : f"A philosophical work by {author} ({year}).",
        "central_argument": "",
        "related_books"  : [],
        "source"         : "open_library",
    }


def deduplicate(books):
    """
    Remove duplicate books by normalizing title + author.
    Keeps the first occurrence of each.
    """
    seen    = set()
    unique  = []
    for book in books:
        key = (book["title"].lower().strip(), book["author"].lower().strip())
        if key not in seen:
            seen.add(key)
            unique.append(book)
    return unique


def load_existing_books():
    """Load existing curated books.json — we preserve these."""
    if BOOKS_FILE.exists():
        with open(BOOKS_FILE, encoding="utf-8") as f:
            return json.load(f)
    return []


def run_fetch(limit_per_query=8, save=True):
    """
    Run all search queries, collect results, merge with
    existing curated books, deduplicate, and save.

    Returns final list of book dicts.
    """
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    print(f"Fetching from Open Library API...")
    print(f"Queries: {len(PHILOSOPHY_SEARCHES)}")
    print(f"Limit per query: {limit_per_query}")
    print("-" * 45)

    # Load existing curated books — these have full analysis
    existing    = load_existing_books()
    api_books   = []

    for i, (query, tradition) in enumerate(PHILOSOPHY_SEARCHES):
        print(f"[{i+1}/{len(PHILOSOPHY_SEARCHES)}] '{query}'...", end=" ")
        docs = fetch_search(query, limit=limit_per_query)

        count = 0
        for doc in docs:
            record = clean_book_record(doc, tradition)
            # Only keep books with a real title and year
            if record["title"] != "Unknown Title" and record["year"] > 0:
                api_books.append(record)
                count += 1

        print(f"{count} books")
        time.sleep(0.5)   # polite delay

    # Merge: curated books first (they have richer data)
    all_books = existing + api_books
    all_books = deduplicate(all_books)

    print(f"\nResults:")
    print(f"  Curated books  : {len(existing)}")
    print(f"  API books      : {len(api_books)}")
    print(f"  After dedup    : {len(all_books)}")

    if save:
        with open(BOOKS_FILE, "w", encoding="utf-8") as f:
            json.dump(all_books, f, indent=2, ensure_ascii=False)
        print(f"  Saved to       : {BOOKS_FILE}")

    return all_books


if __name__ == "__main__":
    books = run_fetch(limit_per_query=8)
    print(f"\nDone. Total books in database: {len(books)}")

    # Show tradition breakdown
    from collections import Counter
    traditions = Counter(b["tradition"] for b in books)
    print("\nBy tradition:")
    for tradition, count in traditions.most_common():
        print(f"  {tradition:<25} {count} books")