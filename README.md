# Philosophy Navigator

A Python CLI research companion for exploring philosophical books,
thinkers, concepts, and intellectual traditions.

> This tool is not a replacement for reading books.
> It is a navigator — helping you understand arguments,
> find connections, and discover what to read next.

## Setup

```bash
py -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Command reference

| Command | Description |
|---|---|
| `list` | List all books |
| `search-author <name>` | Search by author (partial match) |
| `search-concept <concept>` | Search by concept |
| `search-tradition <name>` | Search by tradition |
| `show <title>` | Full book profile |
| `similar <title>` | Find similar books (TF-IDF) |
| `compare <author1> <author2>` | Compare two philosophers |
| `timeline` | Browse chronologically |
| `traditions` | Map philosophical traditions |

## Global flags

`--json` — output as machine-readable JSON (place before command)
`--export FILE.csv` — export results to CSV (place before command)

## Examples

```bash
# Basic usage
py src/main.py list
py src/main.py search-author Plato
py src/main.py search-concept justice
py src/main.py search-tradition Stoicism
py src/main.py show Republic

# JSON output
py src/main.py --json show Republic
py src/main.py --json search-author kant
py src/main.py --json timeline --tradition Stoicism

# CSV export
py src/main.py --export outputs/books.csv list
py src/main.py --export outputs/plato.csv search-author Plato

# Advanced
py src/main.py similar "Being and Time"
py src/main.py compare Plato Aristotle
py src/main.py timeline --start -400 --end 200
py src/main.py timeline --tradition "German Idealism"
py src/main.py traditions
py src/main.py traditions --detail Existentialism
```

## Data

- 159 books across 9 philosophical traditions
- Source: Open Library API + curated hand-written entries
- Traditions: Ancient Greek, Stoicism, German Idealism,
  Existentialism, Political Philosophy, Rationalism,
  Analytic Philosophy, Empiricism, Post-structuralism

## Validation

On startup the tool automatically:
- Warns if any book is missing required fields
- Warns if year is not an integer
- Removes duplicate books (same title + author)

Example warning format:

WARNING: Book #5 missing key 'year': Some Title
WARNING: Book #12 invalid source 'wikipedia': Another Title
1 validation warning(s) found

## Running tests

```bash
py -m unittest tests.test_main -v
```

## Project structure
philosophy-navigator/
├── data/
│   └── books.json          ← 159-book database
├── src/
│   ├── main.py             ← CLI and core logic
│   ├── compare.py          ← thinker comparison
│   ├── similarity.py       ← TF-IDF similarity
│   ├── timeline.py         ← chronological view
│   ├── traditions.py       ← tradition mapping
│   └── fetcher.py          ← Open Library API
├── tests/
│   └── test_main.py        ← unit tests
├── outputs/                ← CSV exports
└── requirements.txt

## Author

Kiril Mickovski
