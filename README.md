# Philosophy Navigator

A Python CLI research companion for exploring philosophical books,
thinkers, concepts, and intellectual traditions.

> This tool is not a replacement for reading.
> It is a navigator — helping you find what to read next,
> understand core arguments, and map connections between thinkers.

## Usage

```bash
# List all books
py src/main.py list

# Search by author
py src/main.py search-author Plato
py src/main.py search-author Kant

# Search by concept
py src/main.py search-concept justice
py src/main.py search-concept virtue

# Search by tradition
py src/main.py search-tradition Stoicism
py src/main.py search-tradition "Political Philosophy"

# Show full book profile
py src/main.py show Republic
py src/main.py show "Being and Time"
```

## Current corpus — 10 books

| Title | Author | Year | Tradition |
|---|---|---|---|
| Republic | Plato | 380 BC | Ancient Greek |
| Nicomachean Ethics | Aristotle | 340 BC | Ancient Greek |
| Meditations | Marcus Aurelius | 180 | Stoicism |
| Leviathan | Thomas Hobbes | 1651 | Political Philosophy |
| Second Treatise of Government | John Locke | 1689 | Political Philosophy |
| Critique of Pure Reason | Immanuel Kant | 1781 | German Idealism |
| Phenomenology of Spirit | Hegel | 1807 | German Idealism |
| Thus Spoke Zarathustra | Nietzsche | 1883 | Existentialism |
| Being and Time | Heidegger | 1927 | Existentialism |
| A Theory of Justice | Rawls | 1971 | Political Philosophy |

## Setup

```bash
py -m venv .venv
.venv\Scripts\Activate.ps1
py src/main.py list
```

## Project structure

philosophy-navigator/
├── data/
│   └── books.json      ← philosophical book database
├── src/
│   └── main.py         ← CLI tool and all search functions
├── notebooks/          ← future Jupyter exploration
├── outputs/            ← future exports
└── README.md

## Next stage
TF-IDF similarity — find books most similar to any given book
based on shared concepts, arguments, and vocabulary.

## Author
Kiril Mickovski
