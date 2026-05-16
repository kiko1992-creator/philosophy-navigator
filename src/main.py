# main.py — Philosophy Navigator

import json, argparse, sys, csv
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from compare    import compare_thinkers, print_comparison
from timeline   import build_timeline, print_timeline, timeline_summary
from traditions import build_tradition_map, print_tradition_map, tradition_detail
from validator  import validate_books, match_author, match_concept, match_tradition, match_title

DATA_FILE = Path(__file__).parent.parent / "data" / "books.json"


def load_books():
    if not DATA_FILE.exists():
        raise SystemExit(f"Error: {DATA_FILE} not found")
    with open(DATA_FILE, encoding="utf-8") as f:
        books = json.load(f)
    validate_books(books)
    return books


def year_str(y):
    if not isinstance(y, int): return "?"
    return f"{abs(y)} BC" if y < 0 else str(y)


def search_author(books, q):
    return [b for b in books if match_author(b, q)]

def search_concept(books, q):
    return [b for b in books if match_concept(b, q)]

def search_tradition(books, q):
    return [b for b in books if match_tradition(b, q)]

def find_book(books, q):
    for b in books:
        if match_title(b, q): return b
    return None


def apply_sort_and_page(books, sort=None, offset=0, limit=None):
    """Sort and paginate a book list."""
    if sort == "year":
        books = sorted(books, key=lambda b: (b.get("year") is None, b.get("year", 0)))
    elif sort == "title":
        books = sorted(books, key=lambda b: b.get("title", "").lower())
    elif sort == "author":
        books = sorted(books, key=lambda b: b.get("author", "").lower())
    books = books[offset:]
    if limit is not None:
        books = books[:limit]
    return books


def summary(b):
    return {
        "title": b.get("title",""), "author": b.get("author",""),
        "year": b.get("year"), "year_str": year_str(b.get("year")),
        "tradition": b.get("tradition",""),
        "key_concepts": b.get("key_concepts",[])[:5],
    }

def print_profile(b):
    title     = b.get("title", "")
    author    = b.get("author", "")
    year      = year_str(b.get("year"))
    tradition = b.get("tradition", "")
    summary   = b.get("short_summary", "")
    argument  = b.get("central_argument", "")
    concepts  = b.get("key_concepts", [])
    related   = b.get("related_books", [])

    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")
    print(f"  Author    : {author}")
    print(f"  Year      : {year}")
    print(f"  Tradition : {tradition}")

    if summary:
        print(f"\n  WHAT IS IT?")
        print(f"  {summary}")

    if argument:
        print(f"\n  CENTRAL ARGUMENT")
        print(f"  {argument}")

    if concepts:
        print(f"\n  KEY CONCEPTS")
        # Show concepts as a numbered list for readability
        for i, c in enumerate(concepts, 1):
            print(f"    {i}. {c}")

    if related:
        print(f"\n  WHAT TO READ NEXT")
        for r in related:
            print(f"    → {r}")
    elif tradition:
        print(f"\n  WHAT TO READ NEXT")
        print(f"  Try: py src/main.py search-tradition \"{tradition}\" --sort year")
        print(f"  Try: py src/main.py similar \"{title}\"")

    print(f"\n{'─'*60}")
    print(f"  Search more: py src/main.py similar \"{title[:30]}\"")
    print()


def print_list(books):
    print(f"\n{'='*60}")
    print(f"  Philosophy Navigator - {len(books)} Books")
    print(f"{'='*60}")
    for i, b in enumerate(books, 1):
        print(f"  {i:<4} {b.get('title','')[:34]:<35} "
              f"{b.get('author','')[:21]:<22} {year_str(b.get('year'))}")
    print()

def print_results(matches, qtype, query):
    if not matches:
        print(f"\n  No books found for {qtype}: {query!r}\n")
        return
    print(f"\n{'='*60}")
    print(f"  {qtype}: {query!r} - {len(matches)} found")
    print(f"{'='*60}")
    for b in matches:
        print(f"\n  {b.get('title','')} ({year_str(b.get('year'))})")
        print(f"  Author    : {b.get('author','')}")
        print(f"  Tradition : {b.get('tradition','')}")
        concepts = ', '.join(b.get('key_concepts',[])[:3])
        if concepts: print(f"  Concepts  : {concepts}")
    print()

def print_profile(b):
    print(f"\n{'='*60}")
    print(f"  {b.get('title','')}")
    print(f"{'='*60}")
    print(f"  Author    : {b.get('author','')}")
    print(f"  Year      : {year_str(b.get('year'))}")
    print(f"  Tradition : {b.get('tradition','')}")
    if b.get("short_summary"):
        print(f"\n  SUMMARY\n  {b['short_summary']}")
    if b.get("central_argument"):
        print(f"\n  CENTRAL ARGUMENT\n  {b['central_argument']}")
    if b.get("key_concepts"):
        print(f"\n  KEY CONCEPTS\n  {', '.join(b['key_concepts'])}")
    if b.get("related_books"):
        print("\n  RELATED BOOKS")
        for r in b["related_books"]: print(f"    - {r}")
    print()


def export_csv(books, path):
    cols = ["title","author","year","tradition","key_concepts",
            "short_summary","central_argument","related_books","source"]
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for b in books:
            row = {c: b.get(c,"") for c in cols}
            row["key_concepts"]  = "; ".join(b.get("key_concepts",[]))
            row["related_books"] = "; ".join(b.get("related_books",[]))
            w.writerow(row)
    print(f"  Exported {len(books)} books to {path}")


def main():
    ap = argparse.ArgumentParser(description="Philosophy Navigator")
    ap.add_argument("--json",   action="store_true", dest="as_json",
                    help="Output as JSON")
    ap.add_argument("--export", default=None, metavar="FILE.csv",
                    help="Export results to CSV file")
    sub = ap.add_subparsers(dest="command")

    # list
    p = sub.add_parser("list")
    p.add_argument("--limit",  type=int, default=None)
    p.add_argument("--offset", type=int, default=0)
    p.add_argument("--sort",   choices=["year","title","author"], default=None)

    # search-author
    p = sub.add_parser("search-author")
    p.add_argument("author")
    p.add_argument("--limit",  type=int, default=None)
    p.add_argument("--offset", type=int, default=0)
    p.add_argument("--sort",   choices=["year","title","author"], default=None)

    # search-concept
    p = sub.add_parser("search-concept")
    p.add_argument("concept")
    p.add_argument("--limit",  type=int, default=None)
    p.add_argument("--offset", type=int, default=0)
    p.add_argument("--sort",   choices=["year","title","author"], default=None)

    # search-tradition
    p = sub.add_parser("search-tradition")
    p.add_argument("tradition")
    p.add_argument("--limit",  type=int, default=None)
    p.add_argument("--offset", type=int, default=0)
    p.add_argument("--sort",   choices=["year","title","author"], default=None)

    # show
    p = sub.add_parser("show")
    p.add_argument("title")

    # compare
    p = sub.add_parser("compare")
    p.add_argument("author1")
    p.add_argument("author2")

    # similar
    p = sub.add_parser("similar")
    p.add_argument("title")
    p.add_argument("--top", type=int, default=5)

    # timeline
    p = sub.add_parser("timeline")
    p.add_argument("--start",     type=int, default=None)
    p.add_argument("--end",       type=int, default=None)
    p.add_argument("--tradition", default=None)

    # traditions
    p = sub.add_parser("traditions")
    p.add_argument("--detail", default=None)

    # stats
    sub.add_parser("stats")

    args = ap.parse_args()
    if not args.command:
        ap.print_help()
        raise SystemExit(0)

    books = load_books()
    J     = args.as_json
    EXP   = args.export

    if args.command == "list":
        results = apply_sort_and_page(books,
                    getattr(args, "sort", None),
                    getattr(args, "offset", 0),
                    getattr(args, "limit", None))
        if EXP: export_csv(results, EXP)
        if J:   print(json.dumps({"total": len(results), "books": [summary(b) for b in results]}, indent=2, ensure_ascii=False))
        else:   print_list(results)

    elif args.command == "search-author":
        m = search_author(books, args.author)
        m = apply_sort_and_page(m,
                getattr(args, "sort", None),
                getattr(args, "offset", 0),
                getattr(args, "limit", None))
        if EXP: export_csv(m, EXP)
        if J:   print(json.dumps({"query": args.author, "total": len(m), "books": [summary(b) for b in m]}, indent=2, ensure_ascii=False))
        else:   print_results(m, "author", args.author)

    elif args.command == "search-concept":
        m = search_concept(books, args.concept)
        m = apply_sort_and_page(m,
                getattr(args, "sort", None),
                getattr(args, "offset", 0),
                getattr(args, "limit", None))
        if EXP: export_csv(m, EXP)
        if J:   print(json.dumps({"query": args.concept, "total": len(m), "books": [summary(b) for b in m]}, indent=2, ensure_ascii=False))
        else:   print_results(m, "concept", args.concept)

    elif args.command == "search-tradition":
        m = search_tradition(books, args.tradition)
        m = apply_sort_and_page(m,
                getattr(args, "sort", None),
                getattr(args, "offset", 0),
                getattr(args, "limit", None))
        if EXP: export_csv(m, EXP)
        if J:   print(json.dumps({"query": args.tradition, "total": len(m), "books": [summary(b) for b in m]}, indent=2, ensure_ascii=False))
        else:   print_results(m, "tradition", args.tradition)

    elif args.command == "show":
        b = find_book(books, args.title)
        if J:
            if b: print(json.dumps(profile(b), indent=2, ensure_ascii=False))
            else: print(json.dumps({"error": "Book not found", "query": args.title}, indent=2))
        else:
            if b: print_profile(b)
            else: print(f"\n  Not found: {args.title!r}\n")

    elif args.command == "compare":
        result = compare_thinkers(args.author1, args.author2, books)
        if J: print(json.dumps(result, indent=2, ensure_ascii=False, default=str))
        else: print_comparison(result)

    elif args.command == "similar":
        from similarity import build_tfidf_matrix, find_similar, print_similar
        _, matrix = build_tfidf_matrix(books)
        target, similar = find_similar(args.title, books, matrix, args.top)
        if J:
            if target:
                print(json.dumps({
                    "target": summary(target),
                    "similar": [{**summary(b), "score": s} for b, s in similar]
                }, indent=2, ensure_ascii=False))
            else:
                print(json.dumps({"error": "Not found", "query": args.title}, indent=2))
        else:
            print_similar(target, similar)

    elif args.command == "timeline":
        if J:
            filtered = [b for b in books
                if isinstance(b.get("year"), int)
                and (args.start is None or b["year"] >= args.start)
                and (args.end   is None or b["year"] <= args.end)
                and (args.tradition is None or args.tradition.lower() in b.get("tradition","").lower())]
            print(json.dumps({"total": len(filtered),
                "books": [summary(b) for b in sorted(filtered, key=lambda x: x["year"])]
            }, indent=2, ensure_ascii=False))
        else:
            timeline_summary(books)
            tl = build_timeline(books, args.start, args.end)
            print_timeline(tl, args.tradition)

    elif args.command == "traditions":
        trads, connections = build_tradition_map(books)
        if args.detail:
            if J:
                name = args.detail
                data = trads.get(name, {})
                print(json.dumps({
                    "tradition": name,
                    "book_count": len(data.get("books",[])),
                    "authors": sorted(data.get("authors",[])),
                    "concepts": sorted(data.get("concepts",[]))[:15],
                }, indent=2, ensure_ascii=False))
            else:
                tradition_detail(trads, connections, args.detail)
        else:
            if J:
                print(json.dumps({
                    "traditions": [{"name": k, "book_count": len(v["books"])}
                                   for k, v in sorted(trads.items(),
                                   key=lambda x: len(x[1]["books"]), reverse=True)]
                }, indent=2, ensure_ascii=False))
            else:
                print_tradition_map(trads, connections)

    elif args.command == "stats":
        total    = len(books)
        curated  = sum(1 for b in books if b.get("source") == "curated")
        api      = sum(1 for b in books if b.get("source") == "open_library")
        other    = total - curated - api
        enriched = sum(1 for b in books if b.get("short_summary","").strip()
                       and not b["short_summary"].startswith("A philosophical work by"))
        missing_summary  = sum(1 for b in books if not b.get("short_summary","").strip())
        missing_argument = sum(1 for b in books if not b.get("central_argument","").strip())
        missing_concepts = sum(1 for b in books if len(b.get("key_concepts",[])) < 2)

        if J:
            print(json.dumps({
                "total": total, "curated": curated, "open_library": api,
                "other": other, "enriched": enriched,
                "missing_summary": missing_summary,
                "missing_argument": missing_argument,
                "missing_concepts": missing_concepts,
            }, indent=2))
        else:
            print(f"\n{'='*60}")
            print(f"  Philosophy Navigator — Data Stats")
            print(f"{'='*60}")
            print(f"  Total books      : {total}")
            print(f"  Curated          : {curated}")
            print(f"  Open Library     : {api}")
            print(f"  Other/unknown    : {other}")
            print(f"  Enriched         : {enriched}")
            print(f"  Missing summary  : {missing_summary}")
            print(f"  Missing argument : {missing_argument}")
            print(f"  Missing concepts : {missing_concepts}")
            print()


if __name__ == "__main__":
    main()