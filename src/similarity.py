# similarity.py
# TF-IDF based book similarity
# Finds philosophically similar books based on shared
# concepts, traditions, summaries and arguments

import json
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

DATA_FILE = Path(__file__).parent.parent / "data" / "books.json"


def load_books():
    """Load books from JSON file."""
    with open(DATA_FILE, encoding="utf-8") as f:
        return json.load(f)


def build_book_text(book):
    """
    Combine all meaningful text fields into one string.
    This is what TF-IDF will analyze.
    Repeat tradition and concepts to give them more weight.
    """
    concepts  = " ".join(book.get("key_concepts", []))
    tradition = book.get("tradition", "")
    summary   = book.get("short_summary", "")
    argument  = book.get("central_argument", "")
    author    = book.get("author", "")

    # Repeat tradition and concepts — boosts their TF-IDF weight
    return f"{tradition} {tradition} {concepts} {concepts} {summary} {argument} {author}"


def build_tfidf_matrix(books):
    """
    Build TF-IDF matrix from all books.
    Returns (vectorizer, matrix, books) tuple.
    """
    texts = [build_book_text(b) for b in books]

    vectorizer = TfidfVectorizer(
        min_df      = 1,
        max_df      = 0.9,
        ngram_range = (1, 2),   # unigrams and bigrams
        stop_words  = "english",
    )

    matrix = vectorizer.fit_transform(texts)
    return vectorizer, matrix


def find_similar(title_query, books, matrix, top_n=5):
    """
    Find books most similar to the given title.

    Parameters:
        title_query : partial title string (case-insensitive)
        books       : list of book dicts
        matrix      : TF-IDF matrix
        top_n       : number of similar books to return

    Returns:
        (target_book, similar_books) tuple
        similar_books is list of (book, score) tuples
    """
    # Find target book index
    query = title_query.lower()
    target_idx = None
    for i, book in enumerate(books):
        if query in book["title"].lower():
            target_idx = i
            break

    if target_idx is None:
        return None, []

    target_book = books[target_idx]

    # Compute cosine similarity between target and all books
    target_vector   = matrix[target_idx]
    similarity_scores = cosine_similarity(target_vector, matrix).flatten()

    # Sort by score descending, exclude the target itself
    ranked = sorted(
        enumerate(similarity_scores),
        key=lambda x: x[1],
        reverse=True
    )

    similar = []
    for idx, score in ranked:
        if idx == target_idx:
            continue
        if score < 0.01:   # skip zero similarity
            continue
        similar.append((books[idx], round(float(score), 4)))
        if len(similar) >= top_n:
            break

    return target_book, similar


def print_similar(target_book, similar_books):
    """Print similarity results in readable format."""
    if target_book is None:
        print("\n  Book not found.\n")
        return

    year = str(target_book["year"]) if target_book["year"] > 0 \
           else f"{abs(target_book['year'])} BC"

    print(f"\n{'='*58}")
    print(f"  Similar to: {target_book['title']}")
    print(f"  {target_book['author']} ({year}) — {target_book['tradition']}")
    print(f"{'='*58}")

    if not similar_books:
        print("  No similar books found.\n")
        return

    for i, (book, score) in enumerate(similar_books, 1):
        year = str(book["year"]) if book["year"] > 0 \
               else f"{abs(book['year'])} BC"
        bar  = "#" * int(score * 30)
        print(f"\n  {i}. {book['title']}")
        print(f"     {book['author']} ({year})")
        print(f"     Tradition : {book['tradition']}")
        concepts = ", ".join(book["key_concepts"][:3])
        print(f"     Concepts  : {concepts}")
        print(f"     Score     : {score:.4f}  {bar}")

    print(f"{'='*58}\n")


if __name__ == "__main__":
    import sys

    query = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "Republic"

    print(f"Loading books and building TF-IDF matrix...")
    books              = load_books()
    vectorizer, matrix = build_tfidf_matrix(books)
    print(f"Matrix: {matrix.shape[0]} books x {matrix.shape[1]} features")

    target, similar = find_similar(query, books, matrix)
    print_similar(target, similar)
    