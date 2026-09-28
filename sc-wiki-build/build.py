#!/usr/bin/env python3
"""Build a single-file HTML reader for the S&C (strength & conditioning) Obsidian wiki.

Usage: python3 build.py            (writes ../sc-performance-wiki.html)
"""
import json, re
from pathlib import Path

HERE = Path(__file__).resolve().parent
VAULT = Path.home() / "Library/Mobile Documents/iCloud~md~obsidian/Documents/S&C/wiki"
OUT = HERE.parent / "sc-performance-wiki.html"
# [[Target]], [[Target|Alias]], [[Target\|Alias]] (inside tables), [[Target#Heading|Alias]]
LINK = re.compile(r"\[\[([^\]|\\#]*)(?:#([^\]|\\]+))?(?:\\?\|([^\]]+))?\]\]")

pages = {}
for p in sorted(VAULT.rglob("*.md")):
    folder = p.parent.relative_to(VAULT).as_posix()
    pages[p.stem] = {"md": p.read_text(encoding="utf-8"), "folder": "" if folder == "." else folder}

# Sidebar = index.md sections; each "- [[Page]] — description" line gives one entry.
nav, section, desc = [], None, {}
for line in pages["index"]["md"].splitlines():
    if line.startswith("## "):
        section = {"title": line[3:].strip(), "items": []}
        nav.append(section)
    elif section and line.lstrip().startswith("-"):
        m = LINK.search(line)
        if not m:
            continue
        target = m.group(1).strip()
        section["items"].append(target)
        d = re.split(r"\s+[—–-]\s+", line[m.end():], maxsplit=1)
        if len(d) > 1 and target not in desc:
            desc[target] = re.sub(r"\s+", " ", d[1]).strip()

listed = {t.lower() for s in nav for t in s["items"]}
extra = [n for n in pages if n.lower() not in listed and n != "index"]
if extra:
    nav.append({"title": "Other pages", "items": sorted(extra)})

data = json.dumps({"pages": pages, "nav": nav, "desc": desc}, ensure_ascii=False).replace("</", "<\\/")
html = (HERE / "template.html").read_text(encoding="utf-8")
html = html.replace("__MARKED__", (HERE / "marked.min.js").read_text(encoding="utf-8")).replace("__DATA__", data)
OUT.write_text(html, encoding="utf-8")
print(f"{len(pages)} pages, {sum(len(s['items']) for s in nav)} in sidebar, {len(extra)} extra, "
      f"{len(desc)} descriptions -> {OUT} ({OUT.stat().st_size // 1024} KB)")
