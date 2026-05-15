# main.py
# Philosophy Navigator — CLI research companion
# Explore philosophical books, thinkers, and concepts

import json
import argparse
from pathlib import Path

# ── Path to the data file ──────────────────────────────────────────────────
DATA_FILE = Path(__file__).parent.parent / "data" / "books.json"


# ── Data loading ───────────────────────────────────────────────────────────

def load_books():
    """
    Load all books from data/books.json.
    Returns a list of book dicts.
    Exits with a clear message if the file is missing.
    """
    if not DATA_FILE.exists():
        print(f"Error: data file not found at {DATA_FILE}")
        raise SystemExit(1)

    with open(DATA_FILE, encoding="utf-8") as f:
        return json.load(f)


# ── Core functions ─────────────────────────────────────────────────────────

def list_books(books):
    """
    Print a numbered list of all books with author and year.
    """
    print(f"\n{'='*55}")
    print(f"  Philosophy Navigator — {len(books)} Books")
    print(f"{'='*55}")
    print(f"  {'#':<4} {'Title':<35} {'Author':<22} {'Year'}")
    print(f"  {'-'*52}")

    for i, book in enumerate(books, 1):
        year  = str(book["year"]) if book["year"] > 0 else f"{abs(book['year'])} BC"
        print(f"  {i:<4} {book['title']:<35} {book['author']:<22} {year}")

    print(f"{'='*55}\n")


def search_by_author(books, author_query):
    """
    Search books by author name (case-insensitive partial match).
    Returns list of matching books.
    """
    query   = author_query.lower()
    matches = [b for b in books if query in b["author"].lower()]
    return matches


def search_by_concept(books, concept_query):
    """
    Search books by key concept (case-insensitive partial match).
    Checks against each book's key_concepts list.
    Returns list of matching books.
    """
    query   = concept_query.lower()
    matches = [
        b for b in books
        if any(query in concept.lower() for concept in b["key_concepts"])
    ]
    return matches


def search_by_tradition(books, tradition_query):
    """
    Search books by philosophical tradition (case-insensitive).
    Returns list of matching books.
    """
    query   = tradition_query.lower()
    matches = [b for b in books if query in b["tradition"].lower()]
    return matches


def find_book(books, title_query):
    """
    Find a single book by title (case-insensitive partial match).
    Returns the first match or None.
    """
    query = title_query.lower()
    for book in books:
        if query in book["title"].lower():
            return book
    return None


def print_book_profile(book):
    """
    Print a detailed, readable profile for a single book.
    """
    year = str(book["year"]) if book["year"] > 0 else f"{abs(book['year'])} BC"

    print(f"\n{'='*55}")
    print(f"  {book['title']}")
    print(f"{'='*55}")
    print(f"  Author    : {book['author']}")
    print(f"  Year      : {year}")
    print(f"  Tradition : {book['tradition']}")
    print()
    print(f"  SUMMARY")
    print(f"  {book['short_summary']}")
    print()
    print(f"  CENTRAL ARGUMENT")
    print(f"  {book['central_argument']}")
    print()
    print(f"  KEY CONCEPTS")
    concepts = ", ".join(book["key_concepts"])
    print(f"  {concepts}")
    print()
    print(f"  RELATED BOOKS")
    for related in book["related_books"]:
        print(f"    - {related}")
    print(f"{'='*55}\n")


def print_search_results(matches, query_type, query):
    """
    Print search results in a compact list format.
    """
    if not matches:
        print(f"\n  No books found for {query_type}: '{query}'\n")
        return

    print(f"\n{'='*55}")
    print(f"  Results for {query_type}: '{query}' — {len(matches)} found")
    print(f"{'='*55}")

    for book in matches:
        year = str(book["year"]) if book["year"] > 0 else f"{abs(book['year'])} BC"
        concepts = ", ".join(book["key_concepts"][:3])
        print(f"\n  {book['title']} ({year})")
        print(f"  Author    : {book['author']}")
        print(f"  Tradition : {book['tradition']}")
        print(f"  Concepts  : {concepts}...")

    print(f"\n{'='*55}\n")


# ── CLI ────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Philosophy Navigator — explore books, thinkers, and concepts",
        epilog=(
            "Examples:\n"
            "  py src/main.py list\n"
            "  py src/main.py search-author Plato\n"
            "  py src/main.py search-concept justice\n"
            "  py src/main.py search-tradition Stoicism\n"
            "  py src/main.py show Republic\n"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    subparsers = parser.add_subparsers(dest="command")

    # list command
    subparsers.add_parser(
        "list",
        help="List all books in the collection",
    )

    # search-author command
    p_author = subparsers.add_parser(
        "search-author",
        help="Search books by author name",
    )
    p_author.add_argument("author", help="Author name to search for")

    # search-concept command
    p_concept = subparsers.add_parser(
        "search-concept",
        help="Search books by philosophical concept",
    )
    p_concept.add_argument("concept", help="Concept to search for")

    # search-tradition command
    p_tradition = subparsers.add_parser(
        "search-tradition",
        help="Search books by philosophical tradition",
    )
    p_tradition.add_argument("tradition", help="Tradition to search for")

    # show command
    p_show = subparsers.add_parser(
        "show",
        help="Show full profile for a book",
    )
    p_show.add_argument("title", help="Title of the book to display")

    args = parser.parse_args()

    # Show help if no command given
    if not args.command:
        parser.print_help()
        raise SystemExit(0)

    # Load books
    books = load_books()

    # Route to correct function
    if args.command == "list":
        list_books(books)

    elif args.command == "search-author":
        matches = search_by_author(books, args.author)
        print_search_results(matches, "author", args.author)

    elif args.command == "search-concept":
        matches = search_by_concept(books, args.concept)
        print_search_results(matches, "concept", args.concept)

    elif args.command == "search-tradition":
        matches = search_by_tradition(books, args.tradition)
        print_search_results(matches, "tradition", args.tradition)

    elif args.command == "show":
        book = find_book(books, args.title)
        if book:
            print_book_profile(book)
        else:
            print(f"\n  Book not found: '{args.title}'\n")


if __name__ == "__main__":
    main()
    