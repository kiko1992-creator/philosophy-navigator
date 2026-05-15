# enricher.py
# Uses Ollama (local Mistral) to enrich books with missing summaries and arguments
# Reads data/books.json, enriches thin records, writes back

import json
import time
import requests
from pathlib import Path

DATA_FILE   = Path(__file__).parent.parent / "data" / "books.json"
OLLAMA_URL  = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "mistral"


def needs_enrichment(book):
    """Return True if book is missing key analytical fields."""
    missing_summary  = not book.get("short_summary", "").strip() or \
                       book.get("short_summary", "").startswith("A philosophical work by")
    missing_argument = not book.get("central_argument", "").strip()
    missing_concepts = len(book.get("key_concepts", [])) < 2
    return missing_summary or missing_argument or missing_concepts


def enrich_book(book):
    """
    Call local Ollama (Mistral) to generate summary, central argument,
    and key concepts for one book.
    Returns updated book dict and success boolean.
    """
    title     = book.get("title", "")
    author    = book.get("author", "")
    year      = book.get("year", "")
    tradition = book.get("tradition", "")

    prompt = f"""You are a philosophy research assistant.
Provide concise, accurate information about this philosophical work:

Title: {title}
Author: {author}
Year: {year}
Tradition: {tradition}

Respond with ONLY a JSON object in this exact format:
{{
  "short_summary": "2-3 sentence overview of the book",
  "central_argument": "1-2 sentence core thesis or argument",
  "key_concepts": ["concept1", "concept2", "concept3", "concept4", "concept5"]
}}

Requirements:
- short_summary: factual, 40-60 words
- central_argument: the single most important claim the book makes
- key_concepts: 4-6 lowercase philosophical terms central to this work
- If you don't recognize the book, use what you know about the author and tradition
- Respond ONLY with the JSON object, no other text"""

    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model":  OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False
            },
            timeout=120
        )
        response.raise_for_status()

        raw = response.json()["response"].strip()

        # Strip markdown code fences if present
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        raw = raw.strip()

        data = json.loads(raw)

        # Update book with enriched data
        if data.get("short_summary"):
            book["short_summary"]    = data["short_summary"]
        if data.get("central_argument"):
            book["central_argument"] = data["central_argument"]
        if data.get("key_concepts"):
            book["key_concepts"]     = data["key_concepts"]

        return book, True

    except Exception as e:
        print(f"    Error: {e}")
        return book, False


def run_enrichment(max_books=10, dry_run=False):
    """
    Enrich books missing summaries or arguments.

    Parameters:
        max_books : max number of books to enrich per run
        dry_run   : if True, show what would be enriched without calling API
    """
    print(f"Loading books from {DATA_FILE}")
    with open(DATA_FILE, encoding="utf-8") as f:
        books = json.load(f)

    print(f"Total books: {len(books)}")

    # Find books that need enrichment
    thin_books = [(i, b) for i, b in enumerate(books) if needs_enrichment(b)]
    print(f"Books needing enrichment: {len(thin_books)}")
    print(f"Will process: {min(max_books, len(thin_books))} this run")
    print()

    if dry_run:
        print("DRY RUN — showing books that would be enriched:")
        for i, book in thin_books[:max_books]:
            print(f"  [{i}] {book.get('title','')} — {book.get('author','')}")
        return

    enriched = 0
    failed   = 0

    for idx, (book_idx, book) in enumerate(thin_books[:max_books]):
        title  = book.get("title", "unknown")
        author = book.get("author", "")
        print(f"[{idx+1}/{min(max_books, len(thin_books))}] {title} — {author}")

        updated_book, success = enrich_book(book)

        if success:
            books[book_idx] = updated_book
            print(f"  Summary  : {updated_book['short_summary'][:80]}...")
            print(f"  Argument : {updated_book['central_argument'][:80]}...")
            print(f"  Concepts : {', '.join(updated_book['key_concepts'][:4])}")
            enriched += 1
        else:
            failed += 1

        # Save after every book — don't lose progress
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(books, f, indent=2, ensure_ascii=False)

        # Small delay between calls
        if idx < len(thin_books) - 1:
            time.sleep(0.5)

        print()

    print(f"Done: {enriched} enriched, {failed} failed")
    print(f"Saved to {DATA_FILE}")


if __name__ == "__main__":
    import sys

    # Parse simple args
    dry_run   = "--dry-run" in sys.argv
    max_books = 10

    for arg in sys.argv[1:]:
        if arg.startswith("--max="):
            max_books = int(arg.split("=")[1])

    run_enrichment(max_books=max_books, dry_run=dry_run)