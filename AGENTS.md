# AGENTS.md

Self-contained single-file HTML pages, opened straight from disk (`file://`). There is no server,
package manager, bundler or test suite. The builds are plain Python 3 (standard library only).

## Generated or hand-edited

| Page | Kind | Edit here | Then |
|---|---|---|---|
| `balatro-missing-jokers.html` | generated | `balatro-build/template.html` | `python3 balatro-build/build.py` |
| `eternal-decks-rulebook.html` | generated | `eternal-decks-build/template.html` | `python3 eternal-decks-build/build.py` |
| `sc-performance-wiki.html` | generated | `sc-wiki-build/template.html` | `python3 sc-wiki-build/build.py` |
| `bookshelf.html` | hand-edited | the file itself | nothing to build |

- **Never edit a generated page directly.** The next build overwrites it. Change the template
  or the build script, rebuild, and commit the source change together with the regenerated page.
- The generated pages are large, and their data sits on a few very long lines
  (`sc-performance-wiki.html` is about 1.9 MB). Don't read them whole: read the template, or grep the output.
- Builds can run from any directory because they resolve paths from `__file__`. With unchanged
  inputs they produce no diff, so after a template change `git diff --stat` should show only the
  template and its page.

## How the builds work

Each `build.py` reads `template.html`, replaces the placeholder tokens with plain string replacement,
and writes `../<page>.html`.

- Placeholders: `__DATA__` and `__MARKED__` (the wikis); `__JOKERS__`, `__VOUCHERS__`, `__PLANETS__`
  and `__ACHIEVEMENTS__` (Balatro). A token the build doesn't replace ships as literal text.
- JSON embedded in a `<script>` has `</` escaped to `<\/` so that page content can't close the tag.
  Keep this escaping for any new data you inline.
- `marked.min.js` is vendored in each wiki build folder and inlined into the page. Don't swap it for a CDN link.

### Balatro (`balatro-build/`)

- `jokers.html`, `vouchers.html`, `planets.html` and `wach.html` are saved snapshots of
  balatrowiki.org, and `ach.html` is Steam's global achievement stats. They are parser input, not pages.
- `build.py` imports `parse.py`, which regenerates `data.json` from those snapshots as a side
  effect. `data.json` is generated but committed.
- The user's own collection state lives in `template.html`, in the `TABS` object: the `locked` and
  `undisc` lists of collection numbers per tab, `unlockedOn` (achievement name → local date and time),
  and `progress`. Collection-progress updates go there, not in the parser.
- To refresh game data, replace the snapshot HTML and rebuild. `parse.py` reads wiki table columns
  by position, so a changed wiki layout can produce wrong data without raising an error. Check the
  printed counts (currently `150 32 12 31` for jokers, vouchers, planets and achievements) and spot-check the page.

### Obsidian wikis (`eternal-decks-build/`, `sc-wiki-build/`)

- The content is not in this repo. It is read from the user's iCloud Obsidian vaults:
  `~/Library/Mobile Documents/iCloud~md~obsidian/Documents/Eternal_Decks/wiki` and `.../S&C/wiki`.
  Content changes happen in the vault, and the page only needs a rebuild. These builds work only on
  a Mac with the vault synced.
- Every `*.md` in the vault becomes a page, keyed by filename stem. The sidebar is derived from the
  vault's `index.md` headings and `[[wikilinks]]`. Pages that `index.md` doesn't link to land in an
  "Other pages" group, and the build prints how many there are.
- The two builds parse `index.md` differently. Eternal Decks uses `##` sections, `###` groups and
  `- **Label:** [[A]] · [[B]]` rows. S&C uses `##` sections with `- [[Page]] — description` lines, and
  its link regex also handles `[[Page#Heading|Alias]]` and `[[Page\|Alias]]` inside tables.

## Page conventions

Match these when changing a page or adding one:

- Everything is inline: CSS, JS and data. The only external requests are Google Fonts and images
  (balatrowiki.org, Steam, `covers.openlibrary.org`). No frameworks or JS dependencies.
- Plain `<style>` and `<script>` blocks, design tokens as CSS custom properties on `:root`, a
  `max-width` media query for phone widths, and `prefers-reduced-motion` handling. Where a page has
  a dark theme, it uses `prefers-color-scheme` to override the same variables.
- `localStorage` is used only for per-viewer conveniences (current tab or view, status overrides).
  Wrap every read and write in `try/catch`, and prefix the keys with the page name (`balatro-*`,
  `bookshelf-*`).
- Escape user or content strings before building HTML with `innerHTML` (see `esc` in `bookshelf.html`).
- Short comments explain *why* or describe structure. Keep that density.

### bookshelf.html

To add a book, add an entry to the `BOOKS` array near the top of the script. The comment above it
documents the fields. `status` is `"reading"`, `"want"` or `"read"`. Covers use
`https://covers.openlibrary.org/b/id/<id>-L.jpg`. Genre colours are in `GENRES`.

## Adding a page

- Hand-written: one `<name>.html` at the repo root.
- Generated: a `<name>-build/` folder with `build.py` and `template.html` that writes `../<name>.html`.
  Follow the existing scripts: `HERE = Path(__file__).resolve().parent`, and print a one-line summary with the output size.
- Either way, add a row to the table in `README.md`.

## Checking a change

- Rebuild, then `git diff --stat` to confirm only the expected files changed.
- Open the page in a browser (`open <page>.html`) and check it at desktop and phone widths,
  and in dark mode for pages that have one.
