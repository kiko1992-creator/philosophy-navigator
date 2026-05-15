# timeline.py
# Browse philosophy chronologically

import json
from pathlib import Path
from collections import defaultdict

DATA_FILE = Path(__file__).parent.parent / "data" / "books.json"


def load_books():
    with open(DATA_FILE, encoding="utf-8") as f:
        return json.load(f)


def build_timeline(books, start_year=None, end_year=None):
    """
    Group books by century.
    Returns dict: {century_label: [books]}
    Optionally filter by year range.
    """
    timeline = defaultdict(list)

    for book in books:
        year = book.get("year")
        if not isinstance(year, int):
            continue

        # Apply year filter if given
        if start_year is not None and year < start_year:
            continue
        if end_year is not None and year > end_year:
            continue

        # Group into century buckets
        if year < 0:
            century = f"{abs(year) // 100 + 1}th century BC"
        elif year < 100:
            century = "1st century AD"
        else:
            century = f"{year // 100 + 1}th century"

        timeline[century].append(book)

    # Sort books within each century by year
    for century in timeline:
        timeline[century].sort(key=lambda b: b.get("year", 0))

    return timeline


def print_timeline(timeline, tradition_filter=None):
    """Print chronological view of books."""
    print(f"\n{'='*60}")
    print(f"  Philosophy Timeline")
    if tradition_filter:
        print(f"  Tradition: {tradition_filter}")
    print(f"{'='*60}")

    if not timeline:
        print("  No books found for this period.\n")
        return

    # Sort centuries chronologically
    def century_sort_key(label):
        if "BC" in label:
            num = int(label.split("th")[0].split("st")[0].split("nd")[0].split("rd")[0])
            return -num
        else:
            num = int(label.split("th")[0].split("st")[0].split("nd")[0].split("rd")[0])
            return num

    sorted_centuries = sorted(timeline.keys(), key=century_sort_key)

    for century in sorted_centuries:
        books = timeline[century]

        # Apply tradition filter
        if tradition_filter:
            books = [
                b for b in books
                if tradition_filter.lower() in b.get("tradition", "").lower()
            ]
        if not books:
            continue

        print(f"\n  {century.upper()} ({len(books)} books)")
        print(f"  {'-'*45}")

        for book in books:
            year  = book.get("year", "?")
            yr_str = f"{abs(year)} BC" if isinstance(year, int) and year < 0 else str(year)
            title  = book.get("title", "")[:38]
            author = book.get("author", "")[:20]
            trad   = book.get("tradition", "")[:18]
            print(f"  {yr_str:>8}  {title:<40} {author:<22} [{trad}]")

    print(f"\n{'='*60}\n")


def timeline_summary(books):
    """Print a one-line summary of the corpus time span."""
    years = [b.get("year") for b in books if isinstance(b.get("year"), int)]
    if not years:
        print("No year data available.")
        return
    earliest = min(years)
    latest   = max(years)
    span     = latest - earliest

    e_str = f"{abs(earliest)} BC" if earliest < 0 else str(earliest)
    l_str = f"{abs(latest)} BC"   if latest   < 0 else str(latest)

    print(f"\n  Corpus spans {span} years: {e_str} to {l_str}")
    print(f"  Total books with year data: {len(years)}\n")


if __name__ == "__main__":
    import sys
    books = load_books()

    start = int(sys.argv[1]) if len(sys.argv) > 1 else None
    end   = int(sys.argv[2]) if len(sys.argv) > 2 else None
    trad  = sys.argv[3]      if len(sys.argv) > 3 else None

    timeline_summary(books)
    tl = build_timeline(books, start, end)
    print_timeline(tl, trad)