import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from main import search_author, search_concept, find_book, year_str

BOOKS = [
    {"title": "Republic", "author": "Plato", "year": -380,
     "tradition": "Ancient Greek", "key_concepts": ["justice"]},
    {"title": "Nicomachean Ethics", "author": "Aristotle", "year": -340,
     "tradition": "Ancient Greek", "key_concepts": ["virtue"]},
    {"title": "Critique of Pure Reason", "author": "Immanuel Kant",
     "year": 1781, "tradition": "German Idealism", "key_concepts": ["reason"]},
]

class TestNav(unittest.TestCase):
    def test_author_exact(self):
        self.assertEqual(len(search_author(BOOKS, "Plato")), 1)
    def test_author_partial(self):
        self.assertEqual(len(search_author(BOOKS, "kant")), 1)
    def test_author_none(self):
        self.assertEqual(len(search_author(BOOKS, "Nietzsche")), 0)
    def test_concept(self):
        self.assertEqual(len(search_concept(BOOKS, "justice")), 1)
    def test_find_book(self):
        self.assertIsNotNone(find_book(BOOKS, "republic"))
    def test_find_book_none(self):
        self.assertIsNone(find_book(BOOKS, "zzz"))
    def test_year_bc(self):
        self.assertEqual(year_str(-380), "380 BC")
    def test_year_ad(self):
        self.assertEqual(year_str(1781), "1781")
    def test_year_none(self):
        self.assertEqual(year_str(None), "?")

if __name__ == "__main__":
    unittest.main(verbosity=2)