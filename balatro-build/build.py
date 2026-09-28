#!/usr/bin/env python3
"""Build ../balatro-missing-jokers.html from the saved wiki/Steam pages + template.html.

The *.html sources in this folder are snapshots of balatrowiki.org (Jokers, Vouchers,
Planet cards, Achievements) and Steam's global achievement stats; parse.py turns them into
data.json. Your own collection state (locked / not seen / unlocked dates) lives in template.html.

Usage: python3 build.py
"""
import json, os
from pathlib import Path

HERE = Path(__file__).resolve().parent
os.chdir(HERE)
import parse  # noqa: E402  (writes data.json)

d = json.loads((HERE / "data.json").read_text(encoding="utf-8"))
dump = lambda x: json.dumps(x, ensure_ascii=False).replace("</", "<\\/")
html = (HERE / "template.html").read_text(encoding="utf-8")
for key, k in (("__JOKERS__", "J"), ("__VOUCHERS__", "V"), ("__PLANETS__", "P"), ("__ACHIEVEMENTS__", "A")):
    html = html.replace(key, dump(d[k]))
out = HERE.parent / "balatro-missing-jokers.html"
out.write_text(html, encoding="utf-8")
print(f"-> {out} ({out.stat().st_size // 1024} KB)")
