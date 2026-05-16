import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from main import (
    search_author, search_concept, search_tradition,
    find_book, year_str, apply_sort_and_page
)
from validator import (
    normalize, validate_books, find_duplicates,
    match_author, match_concept, match_tradition, match_title
)

BOOKS = [
    {"title": "Republic", "author": "Plato", "year": -380,
     "tradition": "Ancient Greek", "key_concepts": ["justice", "the good"],
     "source": "curated", "short_summary": "Plato's dialogue on justice.",
     "central_argument": "Justice is harmony.", "related_books": []},
    {"title": "Nicomachean Ethics", "author": "Aristotle", "year": -340,
     "tradition": "Ancient Greek", "key_concepts": ["virtue", "eudaimonia"],
     "source": "open_library", "short_summary": "Aristotle on happiness.",
     "central_argument": "Happiness is virtuous activity.", "related_books": []},
    {"title": "Critique of Pure Reason", "author": "Immanuel Kant",
     "year": 1781, "tradition": "German Idealism",
     "key_concepts": ["reason", "a priori"],
     "source": "open_library", "short_summary": "Kant on knowledge.",
     "central_argument": "Knowledge requires both experience and reason.",
     "related_books": []},
    {"title": "Thus Spoke Zarathustra", "author": "Friedrich Nietzsche",
     "year": 1883, "tradition": "Existentialism",
     "key_concepts": ["will to power", "eternal recurrence"],
     "source": "open_library", "short_summary": "Nietzsche on values.",
     "central_argument": "God is dead; create your own values.",
     "related_books": []},
]


# ── Original tests ────────────────────────────────────────────
class TestSearch(unittest.TestCase):
    def test_author_exact(self):
        self.assertEqual(len(search_author(BOOKS, "Plato")), 1)

    def test_author_partial(self):
        self.assertEqual(len(search_author(BOOKS, "kant")), 1)

    def test_author_none(self):
        self.assertEqual(len(search_author(BOOKS, "Nietzsche")), 1)

    def test_author_case_insensitive(self):
        self.assertEqual(len(search_author(BOOKS, "ARISTOTLE")), 1)

    def test_concept(self):
        self.assertEqual(len(search_concept(BOOKS, "justice")), 1)

    def test_concept_partial(self):
        # "reason" matches both "reason" and "a priori" book
        results = search_concept(BOOKS, "reason")
        self.assertGreaterEqual(len(results), 1)

    def test_tradition(self):
        results = search_tradition(BOOKS, "Ancient Greek")
        self.assertEqual(len(results), 2)

    def test_tradition_case_insensitive(self):
        results = search_tradition(BOOKS, "existentialism")
        self.assertEqual(len(results), 1)

    def test_find_book(self):
        self.assertIsNotNone(find_book(BOOKS, "republic"))

    def test_find_book_partial(self):
        self.assertIsNotNone(find_book(BOOKS, "zarathustra"))

    def test_find_book_none(self):
        self.assertIsNone(find_book(BOOKS, "zzz"))


# ── year_str tests ────────────────────────────────────────────
class TestYearStr(unittest.TestCase):
    def test_year_bc(self):
        self.assertEqual(year_str(-380), "380 BC")

    def test_year_ad(self):
        self.assertEqual(year_str(1781), "1781")

    def test_year_none(self):
        self.assertEqual(year_str(None), "?")

    def test_year_zero(self):
        self.assertEqual(year_str(0), "0")

    def test_year_string(self):
        self.assertEqual(year_str("unknown"), "?")


# ── sort and paginate tests ───────────────────────────────────
class TestSortAndPage(unittest.TestCase):
    def test_sort_year(self):
        result = apply_sort_and_page(BOOKS, sort="year")
        years = [b["year"] for b in result]
        self.assertEqual(years, sorted(years))

    def test_sort_title(self):
        result = apply_sort_and_page(BOOKS, sort="title")
        titles = [b["title"].lower() for b in result]
        self.assertEqual(titles, sorted(titles))

    def test_sort_author(self):
        result = apply_sort_and_page(BOOKS, sort="author")
        authors = [b["author"].lower() for b in result]
        self.assertEqual(authors, sorted(authors))

    def test_limit(self):
        result = apply_sort_and_page(BOOKS, limit=2)
        self.assertEqual(len(result), 2)

    def test_offset(self):
        result = apply_sort_and_page(BOOKS, offset=2)
        self.assertEqual(len(result), 2)

    def test_limit_and_offset(self):
        result = apply_sort_and_page(BOOKS, offset=1, limit=2)
        self.assertEqual(len(result), 2)

    def test_offset_beyond_length(self):
        result = apply_sort_and_page(BOOKS, offset=100)
        self.assertEqual(len(result), 0)

    def test_no_args(self):
        result = apply_sort_and_page(BOOKS)
        self.assertEqual(len(result), len(BOOKS))


# ── validator tests ───────────────────────────────────────────
class TestNormalize(unittest.TestCase):
    def test_lowercase(self):
        self.assertEqual(normalize("Plato"), "plato")

    def test_strip(self):
        self.assertEqual(normalize("  Kant  "), "kant")

    def test_collapse_whitespace(self):
        self.assertEqual(normalize("Being  and   Time"), "being and time")

    def test_non_string(self):
        self.assertEqual(normalize(123), "123")


class TestValidateBooks(unittest.TestCase):
    def test_valid_books_no_warnings(self):
        warnings = validate_books(BOOKS)
        self.assertEqual(len(warnings), 0)

    def test_missing_required_field(self):
        bad = [{"author": "Unknown", "year": 2000,
                "tradition": "X", "source": "curated"}]
        warnings = validate_books(bad)
        self.assertTrue(any("title" in w for w in warnings))

    def test_wrong_type_year(self):
        bad = [{"title": "X", "author": "Y", "year": "1800",
                "tradition": "Z", "source": "curated"}]
        warnings = validate_books(bad)
        self.assertTrue(any("year" in w for w in warnings))

    def test_invalid_source(self):
        bad = [{"title": "X", "author": "Y", "year": 2000,
                "tradition": "Z", "source": "wikipedia"}]
        warnings = validate_books(bad)
        self.assertTrue(any("source" in w for w in warnings))


class TestFindDuplicates(unittest.TestCase):
    def test_no_duplicates(self):
        dups = find_duplicates(BOOKS)
        self.assertEqual(len(dups), 0)

    def test_detects_duplicate(self):
        dup_books = BOOKS + [{"title": "Republic", "author": "Plato",
                               "year": -380, "tradition": "Ancient Greek",
                               "key_concepts": []}]
        dups = find_duplicates(dup_books)
        self.assertEqual(len(dups), 1)

    def test_case_insensitive_duplicate(self):
        dup_books = BOOKS + [{"title": "republic", "author": "plato",
                               "year": -380, "tradition": "Ancient Greek",
                               "key_concepts": []}]
        dups = find_duplicates(dup_books)
        self.assertEqual(len(dups), 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)