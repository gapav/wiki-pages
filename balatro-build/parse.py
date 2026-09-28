import re, html, json
SUIT = {"Diamond": "♦", "Heart": "♥", "Spade": "♠", "Club": "♣"}

def rich(x):
    """Wiki cell HTML -> plain text + minimal HTML keeping only hl-*/suit-* colour spans."""
    x = re.sub(r'<(style|link)[^>]*>.*?</style>|<link[^>]*>', '', x, flags=re.S)
    x = re.sub(r'<br\s*/?>', ' ', x)
    # Suit icons become coloured unicode symbols.
    x = re.sub(r'<img[^>]*src="/images/(Diamond|Heart|Spade|Club)_suit_icon[^>]*>', lambda m: SUIT[m.group(1)], x)
    out, stack = [], []
    for tok in re.split(r'(<[^>]+>)', x):
        if not tok.startswith('<'):
            out.append(html.escape(html.unescape(tok), quote=False)); continue
        m = re.match(r'<span[^>]*class="([^"]*)"', tok)
        if m:
            cls = [c for c in m.group(1).split() if re.match(r'(hl|suit)-[a-z]+$', c)]
            stack.append(bool(cls))
            if cls: out.append(f'<span class="{" ".join(cls)}">')
        elif tok.startswith('<span'):
            stack.append(False)
        elif tok.startswith('</span'):
            if stack and stack.pop(): out.append('</span>')
    h = re.sub(r'\s+', ' ', ''.join(out)).replace('\xa0', ' ').strip()
    h = re.sub(r'<span class="[^"]*">\s*</span>', '', h)
    # Put the suit symbol inside the coloured suit name.
    h = re.sub(r'<span class="suit-icon">(.)</span><span class="(suit-[a-z]+)">\s*', r'<span class="\2">\1 ', h)
    text = re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', '', h))).strip()
    return text, h

def rows(page, idx=0):
    s = open(page).read()
    st = [m.start() for m in re.finditer(r'<table class="wikitable', s)][idx]
    t = s[st:s.find('</table>', st)]
    return re.findall(r'<tr[^>]*>(.*?)</tr>', t, re.S)

def cells(r): return re.findall(r'<td([^>]*)>(.*?)</td>', r, re.S)
img = lambda r, i=0: "https://balatrowiki.org" + re.sub(r'/thumb(/[^/]+)/.*', r'\1', re.findall(r'src="(/images/thumb/[^" ?]+)', r)[i])

# Jokers (wiki order = collection order)
R = {'1': 'common', '2': 'uncommon', '3': 'rare', '4': 'legendary'}
J = []
for r in rows('jokers.html', 1)[1:]:
    c = cells(r); n = int(rich(c[0][1])[0])
    e, eh = rich(c[2][1]); u, uh = rich(c[5][1])
    J.append(dict(n=n, name=rich(c[1][1])[0], img=img(r), eff=e, effH=eh, cost=rich(c[3][1])[0],
                  r=R[re.search(r'data-sort-value="(\d)"', c[4][0]).group(1)], unl=u, unlH=uh,
                  loc=f"page {(n-1)//15+1}, slot {(n-1)%15+1}"))

# Vouchers: base/upgrade pairs, 4 pairs per page
POS = ["top left", "top right", "bottom left", "bottom right"]
V = []
for i, r in enumerate(rows('vouchers.html')[2:]):
    c = [x[1] for x in cells(r)]
    loc = f"page {i//4+1}, {POS[i%4]}"
    (be, beh), (ue, ueh), (u, uh) = rich(c[1]), rich(c[3]), rich(c[4])
    base = rich(c[0])[0]
    V.append(dict(n=2*i+1, name=base, img=img(r, 0), eff=be, effH=beh, cost="$10", r="base",
                  unl="Available from start.", unlH="Available from start.", loc=loc))
    V.append(dict(n=2*i+2, name=rich(c[2])[0], img=img(r, 1), eff=ue, effH=ueh, cost="$10", r="upgraded",
                  unl=u, unlH=uh, base=base, loc=loc))

# Planets in collection order
wiki = {}
for r in rows('planets.html')[1:]:
    c = [x[1] for x in cells(r)]
    wiki[rich(c[1])[0]] = (rich(c[2]), img(r))
order = ["Mercury","Venus","Earth","Mars","Jupiter","Saturn","Uranus","Neptune","Pluto","Planet X","Ceres","Eris"]
secret = {"Planet X": "Five of a Kind", "Ceres": "Flush House", "Eris": "Flush Five"}
P = []
for i, n in enumerate(order):
    (e, eh), im = wiki[n]
    u = (f"Only appears after you've played a {secret[n]} in the current run." if n in secret else "Available from start.")
    uh = (f'Only appears after you\'ve played a <span class="hl-orange">{secret[n]}</span> in the current run.' if n in secret else u)
    P.append(dict(n=i+1, name=n, img=im, eff=e, effH=eh, cost="$3", r="secret" if n in secret else "standard",
                  unl=u, unlH=uh, loc=f"row {i//6+1}, slot {i%6+1}"))

# Achievements: wiki order + coloured descriptions + shared unlocks; icons and global % from Steam.
steam = {}
for part in open('ach.html').read().split('<div class="achieveRow')[1:]:
    name = html.unescape(re.search(r'<h3>(.*?)</h3>', part, re.S).group(1).strip())
    steam[name] = dict(img=re.search(r'<img src="([^"]+)"', part).group(1),
                       desc=html.unescape(re.search(r'<h5>(.*?)</h5>', part, re.S).group(1).strip()),
                       pct=float(re.search(r'achievePercent">([\d.]+)%', part).group(1)))
A = []
for r in rows('wach.html')[1:]:
    c = [x[1] for x in cells(r)]
    name = rich(c[1])[0]
    if name not in steam:          # "Platinum" is a console trophy, not on Steam
        continue
    e, eh = rich(c[2])
    if re.search(r'\.png|\{\{|\(\)', e):
        # Wiki cell has tooltip residue: use Steam's text, coloured the way the game colours these terms.
        e = steam[name]["desc"]
        eh = html.escape(e, quote=False)
        for term, cls in (("Red Stake", "red"), ("Black Stake", "gray"), ("Gold Stake", "yellow"),
                          ("Wild Cards", "orange"), ("Glass Cards", "orange"), ("Gold Sticker", "yellow")):
            eh = re.sub(term, f'<span class="hl-{cls}">{term}</span>', eh, flags=re.I)
    e, eh = e.rstrip("."), re.sub(r"\.$", "", eh)   # Steam's descriptions have no trailing period
    su = rich(c[3])[0]
    m = re.search(r'\.png\)\s*(.+)$', su)
    pct = steam[name]["pct"]
    A.append(dict(n=len(A)+1, name=name, img=steam[name]["img"], eff=e, effH=eh, pct=pct, cost=f"{pct}% of players",
                  r="common" if pct >= 50 else "uncommon" if pct >= 20 else "rare" if pct >= 5 else "legendary",
                  unl="Available from start.", unlH="", loc="", shares=m.group(1).strip() if m else None))
assert len(A) == len(steam), (len(A), len(steam))

print(len(J), len(V), len(P), len(A))
json.dump(dict(J=J, V=V, P=P, A=A), open('data.json', 'w'), ensure_ascii=False)
