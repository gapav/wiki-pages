#!/usr/bin/env python3
"""Build a single-file HTML reader, styled after the game's box and playmat, for the Eternal Decks Obsidian wiki.

Usage: python3 build.py            (writes ../eternal-decks-rulebook.html)
"""
import json, re
from pathlib import Path

HERE = Path(__file__).resolve().parent
VAULT = Path.home() / "Library/Mobile Documents/iCloud~md~obsidian/Documents/Eternal_Decks/wiki"
OUT = HERE.parent / "eternal-decks-rulebook.html"
LINK = re.compile(r"\[\[([^\]|]+)(?:\|([^\]]+))?\]\]")

# All wiki pages, keyed by filename stem.
pages = {}
for p in sorted(VAULT.rglob("*.md")):
    folder = p.parent.relative_to(VAULT).as_posix()
    pages[p.stem] = {"md": p.read_text(encoding="utf-8"), "folder": "" if folder == "." else folder}

# Sidebar = the structure of index.md: ## section -> ### group -> linked pages, in order.
nav, section, group = [], None, None
for line in pages["index"]["md"].splitlines():
    if line.startswith("## "):
        section = {"title": line[3:].strip(), "groups": []}
        nav.append(section); group = None
    elif line.startswith("### ") and section:
        group = {"title": line[4:].strip(), "items": []}
        section["groups"].append(group)
    elif section:
        targets = [m.group(1).strip() for m in LINK.finditer(line)]
        if not targets:
            continue
        if group is None:
            group = {"title": "", "items": []}
            section["groups"].append(group)
        # "- **A Eternals:** [[Phoenix]] · …" lines become a labelled sub-row.
        label = re.match(r"-\s*\*\*([^*]+?):?\*\*", line)
        if label and len(targets) > 1:
            group["items"].append({"label": label.group(1).rstrip(":"), "links": targets})
        else:
            group["items"].extend({"links": [t]} for t in targets[:1])

# Pages that exist but index.md doesn't list go in an "Other" group so nothing is unreachable.
listed = {t for s in nav for g in s["groups"] for i in g["items"] for t in i["links"]}
extra = [n for n in pages if n not in listed and n not in ("index",)]
if extra:
    nav.append({"title": "Other pages", "groups": [{"title": "", "items": [{"links": [n]} for n in sorted(extra)]}]})

data = json.dumps({"pages": pages, "nav": nav}, ensure_ascii=False).replace("</", "<\\/")
marked = (HERE / "marked.min.js").read_text(encoding="utf-8")

html = (HERE / "template.html").read_text(encoding="utf-8")
html = html.replace("__MARKED__", marked).replace("__DATA__", data)
OUT.write_text(html, encoding="utf-8")
print(f"{len(pages)} pages, {len(listed)} in sidebar, {len(extra)} extra -> {OUT} ({OUT.stat().st_size // 1024} KB)")
