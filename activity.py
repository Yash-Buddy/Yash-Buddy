"""Builds assets/activity.svg: GitHub-style contribution graph on the board card.
Usage: python3 activity.py [username]   (no token needed; reads the public graph)"""
import datetime as dt, os, random, re, sys, urllib.request

USER = sys.argv[1] if len(sys.argv) > 1 else "Yash-Buddy"
levels, total = {}, None
if os.environ.get("DEMO"):
    random.seed(1)
    levels = {(dt.date.today() - dt.timedelta(d)).isoformat(): random.choice([0, 0, 0, 1, 2, 3, 4]) for d in range(371)}
else:
    try:
        html = urllib.request.urlopen(urllib.request.Request(
            f"https://github.com/users/{USER}/contributions", headers={"User-Agent": "Mozilla/5.0"})).read().decode()
        for tag in re.findall(r"<td[^>]*>", html):
            d, l = re.search(r'data-date="([^"]+)"', tag), re.search(r'data-level="(\d)"', tag)
            if d and l:
                levels[d.group(1)] = int(l.group(1))
        m = re.search(r"([\d,]+)\s+contributions\s+in the last year", html)
        total = m.group(1) if m else None
    except Exception as e:
        print("fetch failed:", e)

today = dt.date.today()
start = today - dt.timedelta(days=364)
start -= dt.timedelta(days=(start.weekday() + 1) % 7)          # back to Sunday
weeks = (today - start).days // 7 + 1
COL = ["#1f1f22", "#0e4429", "#006d32", "#26a641", "#39d353"]
X0, Y0, P, S = 64, 62, 15, 12

cells, mlist, last = "", [], None
for w in range(weeks):
    for r in range(7):
        day = start + dt.timedelta(days=w * 7 + r)
        if day > today:
            continue
        cells += f'<rect x="{X0 + w*P}" y="{Y0 + r*P}" width="{S}" height="{S}" rx="2.5" fill="{COL[levels.get(day.isoformat(), 0)]}"/>'
    sun = start + dt.timedelta(days=w * 7)
    if sun.month != last and (w == 0 or sun.day <= 14):
        mlist.append((X0 + w * P, sun.strftime("%b")))
        last = sun.month
if len(mlist) > 1 and mlist[1][0] - mlist[0][0] < 45:
    mlist.pop(0)
months = "".join(f'<text class="m" x="{x}" y="50">{n}</text>' for x, n in mlist)
days_lbl = "".join(f'<text class="m" x="28" y="{Y0 + r*P + 10}">{n}</text>' for r, n in ((1, "Mon"), (3, "Wed"), (5, "Fri")))
legend = "".join(f'<rect x="{770 + i*17}" y="{Y0 + 7*P + 14}" width="{S}" height="{S}" rx="2.5" fill="{c}"/>' for i, c in enumerate(COL))
summary = f"{total} contributions in the last year" if total else "Contributions in the last year"

tpl = open("assets/board-code.svg").read()
head = tpl[:tpl.index('<rect width="900"')]
head = re.sub(r'viewBox="[^"]*"', 'viewBox="0 0 900 214"', head, 1).replace("Code skills board", "GitHub activity graph")
head = head.replace("</style>", ".m{font:500 12px 'Helvetica Neue',Arial,sans-serif;fill:#7a7a7f}.s{font:600 14px 'Helvetica Neue',Arial,sans-serif;fill:#fff}</style>", 1)
svg = (head + '<rect width="900" height="214" rx="14" fill="#0e0e0f"/>' + months + days_lbl + cells
       + f'<text class="s" x="28" y="{Y0 + 7*P + 24}">{summary}</text>'
       + f'<text class="m" x="730" y="{Y0 + 7*P + 24}" text-anchor="end">Less</text>' + legend
       + f'<text class="m" x="{770 + 5*17 + 4}" y="{Y0 + 7*P + 24}">More</text></svg>')
open("assets/activity.svg", "w").write(svg)
print("wrote assets/activity.svg", "cells:", len(levels), "total:", total)
