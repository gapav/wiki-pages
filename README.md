# html-pages

Self-contained single-file HTML pages. Open any `.html` directly in a browser — no server needed.

| Page | Source | Rebuild |
|---|---|---|
| `balatro-missing-jokers.html` | `balatro-build/` — snapshots of balatrowiki.org + Steam achievement stats, parsed into `data.json` | `python3 balatro-build/build.py` |
| `eternal-decks-rulebook.html` | Eternal Decks Obsidian vault (`iCloud~md~obsidian/Documents/Eternal_Decks/wiki`) | `python3 eternal-decks-build/build.py` |
| `sc-performance-wiki.html` | S&C Obsidian vault (`iCloud~md~obsidian/Documents/S&C/wiki`) | `python3 sc-wiki-build/build.py` |

Each `build.py` fills its `template.html` and writes the page to this folder (its parent directory).
The two Obsidian builds read the vault from iCloud, so they only rebuild on a Mac with that vault synced.
