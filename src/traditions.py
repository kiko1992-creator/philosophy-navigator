# traditions.py
# Map connections between philosophical traditions

import json
from pathlib import Path
from collections import defaultdict, Counter

DATA_FILE = Path(__file__).parent.parent / "data" / "books.json"


def load_books():
    with open(DATA_FILE, encoding="utf-8") as f:
        return json.load(f)


def build_tradition_map(books):
    """
    Analyze all traditions and their connections.

    Returns dict with:
      - traditions: {name: {books, authors, concepts, years}}
      - connections: {(trad1, trad2): connection_strength}
    """
    # Gather data per tradition
    traditions = defaultdict(lambda: {
        "books"   : [],
        "authors" : set(),
        "concepts": set(),
        "years"   : [],
    })

    for book in books:
        trad = book.get("tradition", "").strip()
        if not trad:
            continue

        traditions[trad]["books"].append(book.get("title", ""))
        traditions[trad]["authors"].add(book.get("author", ""))

        for concept in book.get("key_concepts", []):
            traditions[trad]["concepts"].add(concept.lower())

        year = book.get("year")
        if isinstance(year, int):
            traditions[trad]["years"].append(year)

    # Find connections between traditions via shared concepts
    connections = {}
    trad_list = list(traditions.keys())

    for i in range(len(trad_list)):
        for j in range(i + 1, len(trad_list)):
            t1 = trad_list[i]
            t2 = trad_list[j]

            shared = traditions[t1]["concepts"] & traditions[t2]["concepts"]

            if shared:
                key = (t1, t2)
                connections[key] = {
                    "strength"       : len(shared),
                    "shared_concepts": sorted(shared)[:5],
                }

    return dict(traditions), connections


def print_tradition_map(traditions, connections):
    """Print tradition overview and connection map."""

    print(f"\n{'='*60}")
    print(f"  Philosophical Traditions — Overview")
    print(f"{'='*60}")
    print(f"  {'Tradition':<28} {'Books':>6} {'Authors':>8} {'Period'}")
    print(f"  {'-'*55}")

    # Sort by book count descending
    sorted_trads = sorted(
        traditions.items(),
        key=lambda x: len(x[1]["books"]),
        reverse=True
    )

    for trad, data in sorted_trads:
        years   = data["years"]
        n_books = len(data["books"])
        n_auth  = len(data["authors"])

        if years:
            min_y = min(years)
            max_y = max(years)
            min_s = f"{abs(min_y)} BC" if min_y < 0 else str(min_y)
            max_s = f"{abs(max_y)} BC" if max_y < 0 else str(max_y)
            period = f"{min_s} – {max_s}"
        else:
            period = "Unknown"

        print(f"  {trad:<28} {n_books:>6} {n_auth:>8}   {period}")

    # Print connections
    print(f"\n{'='*60}")
    print(f"  Tradition Connections (shared concepts)")
    print(f"{'='*60}")

    sorted_connections = sorted(
        connections.items(),
        key=lambda x: x[1]["strength"],
        reverse=True
    )

    for (t1, t2), data in sorted_connections[:15]:
        strength = data["strength"]
        concepts = ", ".join(data["shared_concepts"][:3])
        bar      = "#" * min(strength, 20)
        print(f"\n  {t1} ↔ {t2}")
        print(f"  Shared concepts ({strength}): {concepts}")
        print(f"  Strength: {bar}")

    print(f"\n{'='*60}\n")


def tradition_detail(traditions, connections, tradition_query):
    """Print detailed view of one tradition."""
    query = tradition_query.lower()
    match = None

    for trad in traditions:
        if query in trad.lower():
            match = trad
            break

    if not match:
        print(f"\n  Tradition not found: '{tradition_query}'\n")
        return

    data = traditions[match]
    years = data["years"]

    print(f"\n{'='*60}")
    print(f"  {match}")
    print(f"{'='*60}")
    print(f"  Books   : {len(data['books'])}")
    print(f"  Authors : {len(data['authors'])}")

    if years:
        min_y = min(years)
        max_y = max(years)
        min_s = f"{abs(min_y)} BC" if min_y < 0 else str(min_y)
        max_s = f"{abs(max_y)} BC" if max_y < 0 else str(max_y)
        print(f"  Period  : {min_s} to {max_s}")

    print(f"\n  KEY AUTHORS")
    for author in sorted(data["authors"])[:8]:
        print(f"    - {author}")

    print(f"\n  TOP CONCEPTS")
    for concept in sorted(data["concepts"])[:10]:
        print(f"    - {concept}")

    # Find connected traditions
    connected = []
    for (t1, t2), conn_data in connections.items():
        if t1 == match or t2 == match:
            other = t2 if t1 == match else t1
            connected.append((other, conn_data["strength"],
                             conn_data["shared_concepts"]))

    if connected:
        connected.sort(key=lambda x: x[1], reverse=True)
        print(f"\n  CONNECTED TRADITIONS")
        for other, strength, concepts in connected[:5]:
            print(f"    - {other} (shared: {', '.join(concepts[:3])})")

    print(f"{'='*60}\n")


if __name__ == "__main__":
    import sys
    books      = load_books()
    trads, connections = build_tradition_map(books)

    if len(sys.argv) > 1:
        tradition_detail(trads, connections, " ".join(sys.argv[1:]))
    else:
        print_tradition_map(trads, connections)