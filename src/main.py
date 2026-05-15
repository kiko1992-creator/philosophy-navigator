# main.py
# Philosophy Navigator — CLI research companion

import json
import argparse
import sys
from pathlib import Path

# Ensure src/ siblings are importable
sys.path.insert(0, str(Path(__file__).parent))

from compare  import compare_thinkers, print_comparison
from timeline import build_timeline, print_timeline, timeline_summary

DATA_FILE = Path(__file__).parent.parent / "data" / "books.json"


def load_books():
    """Load all books from data/books.json."""
    if not DATA_FILE.exists():
        print(f"Error: data file not found at {DATA_FILE}")
        raise SystemExit(1)
    with open(DATA_FILE, encoding="utf-8") as f:
        return json.load(f)


def list_books(books):
    """Print numbered list of all books."""
    print(f"\n{'='*60}")
    print(f"  Philosophy Navigator — {len(books)} Books")
    print(f"{'='*60}")
    print(f"  {'#':<4} {'Title':<35} {'Author':<22} {'Year'}")
    print(f"  {'-'*56}")
    for i, book in enumerate(books, 1):
        year = str(book.get("year", "?")) if book.get("year", 0) > 0 \
               else f"{abs(book.get('year', 0))} BC"
        print(
            f"  {i:<4} {str(book.get('title',''))[:34]:<35} "
            f"{str(book.get('author',''))[:21]:<22} {year}"
        )
    print(f"{'='*60}\n")


def search_by_author(books, query):
    """Search books by author (case-insensitive partial match)."""
    q = query.lower()
    return [b for b in books if q in b.get("author", "").lower()]


def search_by_concept(books, query):
    """Search books by key concept."""
    q = query.lower()
    return [
        b for b in books
        if any(q in c.lower() for c in b.get("key_concepts", []))
    ]


def search_by_tradition(books, query):
    """Search books by philosophical tradition."""
    q = query.lower()
    return [b for b in books if q in b.get("tradition", "").lower()]


def find_book(books, query):
    """Find one book by title (case-insensitive partial match)."""
    q = query.lower()
    for book in books:
        if q in book.get("title", "").lower():
            return book
    return None


def print_book_profile(book):
    """Print full readable profile for one book."""
    year = str(book.get("year", "?")) if book.get("year", 0) > 0 \
           else f"{abs(book.get('year', 0))} BC"

    print(f"\n{'='*60}")
    print(f"  {book.get('title', '')}")
    print(f"{'='*60}")
    print(f"  Author    : {book.get('author', '')}")
    print(f"  Year      : {year}")
    print(f"  Tradition : {book.get('tradition', '')}")

    if book.get("short_summary"):
        print(f"\n  SUMMARY")
        print(f"  {book['short_summary']}")

    if book.get("central_argument"):
        print(f"\n  CENTRAL ARGUMENT")
        print(f"  {book['central_argument']}")

    concepts = book.get("key_concepts", [])
    if concepts:
        print(f"\n  KEY CONCEPTS")
        print(f"  {', '.join(concepts)}")

    related = book.get("related_books", [])
    if related:
        print(f"\n  RELATED BOOKS")
        for r in related:
            print(f"    - {r}")

    print(f"{'='*60}\n")


def print_results(matches, query_type, query):
    """Print search results in compact list format."""
    if not matches:
        print(f"\n  No books found for {query_type}: '{query}'\n")
        return

    print(f"\n{'='*60}")
    print(f"  {query_type.title()}: '{query}' — {len(matches)} found")
    print(f"{'='*60}")

    for book in matches:
        year = str(book.get("year", "?")) if book.get("year", 0) > 0 \
               else f"{abs(book.get('year', 0))} BC"
        concepts = ", ".join(book.get("key_concepts", [])[:3])
        print(f"\n  {book.get('title','')} ({year})")
        print(f"  Author    : {book.get('author','')}")
        print(f"  Tradition : {book.get('tradition','')}")
        if concepts:
            print(f"  Concepts  : {concepts}")

    print(f"\n{'='*60}\n")


def main():
    parser = argparse.ArgumentParser(
        description="Philosophy Navigator — explore books, thinkers, concepts",
        epilog=(
            "Examples:\n"
            "  py src/main.py list\n"
            "  py src/main.py search-author Plato\n"
            "  py src/main.py search-concept justice\n"
            "  py src/main.py search-tradition Stoicism\n"
            "  py src/main.py show Republic\n"
            "  py src/main.py compare Plato Aristotle\n"
            "  py src/main.py similar Republic\n"
            "  py src/main.py timeline\n"
            "  py src/main.py timeline --tradition Stoicism\n"
            "  py src/main.py timeline --start -400 --end 200\n"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    sub = parser.add_subparsers(dest="command")

    # list
    sub.add_parser("list", help="List all books")

    # search-author
    p = sub.add_parser("search-author", help="Search by author name")
    p.add_argument("author", help="Author name")

    # search-concept
    p = sub.add_parser("search-concept", help="Search by concept")
    p.add_argument("concept", help="Concept to search")

    # search-tradition
    p = sub.add_parser("search-tradition", help="Search by tradition")
    p.add_argument("tradition", help="Tradition name")

    # show
    p = sub.add_parser("show", help="Show full book profile")
    p.add_argument("title", help="Book title (partial match)")

    # compare
    p = sub.add_parser("compare", help="Compare two philosophers")
    p.add_argument("author1", help="First philosopher")
    p.add_argument("author2", help="Second philosopher")

    # similar
    p = sub.add_parser("similar", help="Find similar books using TF-IDF")
    p.add_argument("title", help="Book title to find similarities for")
    p.add_argument("--top", type=int, default=5, help="Number of results")

    # timeline
    p = sub.add_parser("timeline", help="Browse philosophy chronologically")
    p.add_argument("--start",     type=int, default=None, help="Start year")
    p.add_argument("--end",       type=int, default=None, help="End year")
    p.add_argument("--tradition", default=None,           help="Filter by tradition")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        raise SystemExit(0)

    books = load_books()

    if args.command == "list":
        list_books(books)

    elif args.command == "search-author":
        matches = search_by_author(books, args.author)
        print_results(matches, "author", args.author)

    elif args.command == "search-concept":
        matches = search_by_concept(books, args.concept)
        print_results(matches, "concept", args.concept)

    elif args.command == "search-tradition":
        matches = search_by_tradition(books, args.tradition)
        print_results(matches, "tradition", args.tradition)

    elif args.command == "show":
        book = find_book(books, args.title)
        if book:
            print_book_profile(book)
        else:
            print(f"\n  Book not found: '{args.title}'\n")

    elif args.command == "compare":
        result = compare_thinkers(args.author1, args.author2, books)
        print_comparison(result)

    elif args.command == "similar":
        from similarity import build_tfidf_matrix, find_similar, print_similar
        print("Building TF-IDF matrix...")
        vectorizer, matrix = build_tfidf_matrix(books)
        target, similar    = find_similar(args.title, books, matrix, args.top)
        print_similar(target, similar)

    elif args.command == "timeline":
        timeline_summary(books)
        tl = build_timeline(books, args.start, args.end)
        print_timeline(tl, args.tradition)


if __name__ == "__main__":
    main()
    