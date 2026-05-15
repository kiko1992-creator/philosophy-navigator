"""Thinker comparison module for Philosophy Navigator."""

from typing import Any


def _normalize_text(value: str) -> str:
    """Normalize text for case-insensitive matching."""
    return str(value).strip().lower()


def _find_books_by_author(books: list[dict[str, Any]], author_query: str) -> list[dict[str, Any]]:
    """Return all books whose author exactly matches author_query (case-insensitive)."""
    query = _normalize_text(author_query)
    matches: list[dict[str, Any]] = []

    for book in books:
        author = _normalize_text(book.get("author", ""))
        if author == query:
            matches.append(book)

    return matches


def _sort_books_by_year(books: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Return books sorted by year ascending; missing/invalid years go last."""
    def sort_key(book: dict[str, Any]) -> tuple[int, int]:
        year = book.get("year")
        if isinstance(year, int):
            return (0, year)
        return (1, 10**9)

    return sorted(books, key=sort_key)


def _books_brief(books: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Convert books into compact display records: title + year."""
    brief: list[dict[str, Any]] = []
    for book in _sort_books_by_year(books):
        brief.append(
            {
                "title": str(book.get("title", "Unknown title")),
                "year": book.get("year"),
            }
        )
    return brief


def _collect_traditions(books: list[dict[str, Any]]) -> list[str]:
    """Collect sorted unique traditions for an author's books."""
    values = {
        str(book.get("tradition", "")).strip()
        for book in books
        if str(book.get("tradition", "")).strip()
    }
    return sorted(values)


def _collect_key_concepts(books: list[dict[str, Any]]) -> set[str]:
    """Collect normalized concept set from books."""
    concepts: set[str] = set()
    for book in books:
        for concept in book.get("key_concepts", []):
            text = _normalize_text(concept)
            if text:
                concepts.add(text)
    return concepts


def _collect_related_books(books: list[dict[str, Any]]) -> set[str]:
    """Collect normalized related_books set from books."""
    related: set[str] = set()
    for book in books:
        for title in book.get("related_books", []):
            text = _normalize_text(title)
            if text:
                related.add(text)
    return related


def _earliest_year(books: list[dict[str, Any]]) -> int | None:
    """Return earliest integer year from books, or None if unavailable."""
    years = [book.get("year") for book in books if isinstance(book.get("year"), int)]
    if not years:
        return None
    return min(years)


def compare_thinkers(author1: str, author2: str, books: list[dict[str, Any]]) -> dict[str, Any]:
    """Compare two thinkers and return structured comparison data."""
    books1_raw = _find_books_by_author(books, author1)
    books2_raw = _find_books_by_author(books, author2)

    found1 = len(books1_raw) > 0
    found2 = len(books2_raw) > 0

    books1_brief = _books_brief(books1_raw)
    books2_brief = _books_brief(books2_raw)

    traditions1 = _collect_traditions(books1_raw)
    traditions2 = _collect_traditions(books2_raw)

    concepts1 = _collect_key_concepts(books1_raw)
    concepts2 = _collect_key_concepts(books2_raw)

    shared_concepts = sorted(concepts1.intersection(concepts2))
    unique_concepts1 = sorted(concepts1.difference(concepts2))
    unique_concepts2 = sorted(concepts2.difference(concepts1))

    related1 = _collect_related_books(books1_raw)
    related2 = _collect_related_books(books2_raw)
    shared_related_books = sorted(related1.intersection(related2))

    year1 = _earliest_year(books1_raw)
    year2 = _earliest_year(books2_raw)

    chronology: dict[str, Any] = {
        "status": "insufficient_data",
        "earliest_year1": year1,
        "earliest_year2": year2,
        "first_author": None,       # "author1" | "author2" | "same_period"
        "years_apart": None,
    }

    if year1 is not None and year2 is not None:
        chronology["status"] = "ok"
        chronology["years_apart"] = abs(year1 - year2)

        if year1 < year2:
            chronology["first_author"] = "author1"
        elif year2 < year1:
            chronology["first_author"] = "author2"
        else:
            chronology["first_author"] = "same_period"

    return {
        "author1": author1,
        "author2": author2,
        "found1": found1,
        "found2": found2,
        "books1": books1_brief,
        "books2": books2_brief,
        "traditions1": traditions1,
        "traditions2": traditions2,
        "shared_concepts": shared_concepts,
        "unique_concepts1": unique_concepts1,
        "unique_concepts2": unique_concepts2,
        "shared_related_books": shared_related_books,
        "chronology": chronology,
    }


def _print_books_section(author: str, books_brief: list[dict[str, Any]], traditions: list[str]) -> None:
    print(f"{author} — Books:")
    if not books_brief:
        print("  - None")
    else:
        for item in books_brief:
            year = item.get("year")
            year_text = str(year) if year is not None else "Unknown year"
            print(f"  - {item.get('title', 'Unknown title')} ({year_text})")

    if traditions:
        print(f"{author} — Traditions: {', '.join(traditions)}")
    else:
        print(f"{author} — Traditions: None")


def _print_list_line(label: str, items: list[str]) -> None:
    if items:
        print(f"{label}: {', '.join(items)}")
    else:
        print(f"{label}: None")


def print_comparison(result: dict[str, Any]) -> None:
    """Print a readable side-by-side thinker comparison."""
    author1 = result.get("author1", "Author 1")
    author2 = result.get("author2", "Author 2")
    found1 = bool(result.get("found1", False))
    found2 = bool(result.get("found2", False))

    print(f"Thinker Comparison: {author1} vs {author2}")
    print("-" * (len("Thinker Comparison: ") + len(author1) + len(author2) + 4))

    if not found1:
        print(f"No books found for: {author1}")
    if not found2:
        print(f"No books found for: {author2}")

    print()
    _print_books_section(author1, result.get("books1", []), result.get("traditions1", []))
    print()
    _print_books_section(author2, result.get("books2", []), result.get("traditions2", []))

    print()
    _print_list_line("Shared concepts", result.get("shared_concepts", []))
    _print_list_line(f"Unique to {author1}", result.get("unique_concepts1", []))
    _print_list_line(f"Unique to {author2}", result.get("unique_concepts2", []))

    print()
    _print_list_line("Shared related_books references", result.get("shared_related_books", []))

    print()
    chronology = result.get("chronology", {})
    if chronology.get("status") != "ok":
        print("Chronology unavailable due to missing year data.")
        return

    first_author = chronology.get("first_author")
    years_apart = chronology.get("years_apart")
    y1 = chronology.get("earliest_year1")
    y2 = chronology.get("earliest_year2")

    if first_author == "author1":
        print(f"{author1} came first by {years_apart} years (earliest: {y1} vs {y2}).")
    elif first_author == "author2":
        print(f"{author2} came first by {years_apart} years (earliest: {y2} vs {y1}).")
    else:
        print(f"Both thinkers begin in the same recorded year ({y1}).")
if __name__ == "__main__":
    import sys
    import json
    from pathlib import Path

    DATA_FILE = Path(__file__).parent.parent / "data" / "books.json"

    if len(sys.argv) < 3:
        print("Usage: py src/compare.py <Author1> <Author2>")
        print('Example: py src/compare.py Plato Aristotle')
        sys.exit(1)

    author1 = sys.argv[1]
    author2 = sys.argv[2]

    with open(DATA_FILE, encoding="utf-8") as f:
        books = json.load(f)

    result = compare_thinkers(author1, author2, books)
    print_comparison(result)