"""Builds assets/heatmap.svg: your GitHub contribution graph as an airport departures board.
Usage: python scripts/generate_heatmap.py [username]   (uses only the Python standard library)"""
import re, sys, os, html, urllib.request
from datetime import date

user = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("GH_USER", "Yash-Buddy")
url = f"https://github.com/users/{user}/contributions"
req = urllib.request.Request(url, headers={"User-Agent": "heatmap-board"})
page = urllib.request.urlopen(req, timeout=30).read().decode()

tips = {}
for fid, txt in re.findall(r'<tool-tip[^>]*for="([^"]+)"[^>]*>([^<]*)', page):
    m = re.match(r"(\d[\d,]*) contribution", txt.strip())
    tips[fid] = int(m.group(1).replace(",", "")) if m else 0

days = []
for tag in re.findall(r"<td[^>]*data-date[^>]*>", page):
    d = re.search(r'data-date="([^"]+)"', tag).group(1)
    i = re.search(r'id="contribution-day-component-(\d+)-(\d+)"', tag)
    lv = int(re.search(r'data-level="(\d)"', tag).group(1))
    days.append((int(i.group(2)), int(i.group(1)), d, lv, tips.get(i.group(0)[4:-1], 0)))
if not days:
    sys.exit("No contribution data found")
total = sum(x[4] for x in days)
weeks = max(x[0] for x in days) + 1

X0, Y0, P, R = 70, 124, 15, 4.6
W = X0 + weeks * P + 24
W = max(W, 900)
COL = {0: "#28282b", 1: "#2a4a99", 2: "#3d7bff", 3: "#8fb4ff", 4: "#f2f2f2"}
paths = {k: "" for k in COL}
last_active = None
mlist = []
seen = -1
for w, dow, d, lv, n in days:
    cx, cy = X0 + w * P, Y0 + dow * P
    if lv and (last_active is None or d > last_active[0]):
        last_active = (d, cx, cy)
    else:
        pass
    paths[lv] += f"M{cx} {cy}h0"
    mo = int(d[5:7])
    if dow == 0 and mo != seen and w < weeks - 2:
        seen = mo
        mlist.append((w, cx - R, date(2000, mo, 1).strftime("%b").upper()))
months = "".join(
    f'<text class="m" x="{x}" y="{Y0-14}">{lab}</text>'
    for i, (w, x, lab) in enumerate(mlist)
    if i == len(mlist) - 1 or mlist[i + 1][0] - w >= 3
)
# amber blinking marker on the most recent active day
mark = ""
if last_active:
    _, cx, cy = last_active
    for k in paths:
        paths[k] = paths[k].replace(f"M{cx} {cy}h0", "")
    mark = f'<path class="bk" stroke="#ffb020" stroke-width="{R*2}" stroke-linecap="round" d="M{cx} {cy}h0"/>'

H = 276
plane = '<g transform="translate(52,44) rotate(45) scale(1.55) translate(-12,-12)"><path fill="#0e0e0f" d="M21 16v-2l-8-5V3.5c0-.83-.67-1.5-1.5-1.5S10 2.67 10 3.5V9l-8 5v2l8-2.5V19l-2 1.5V22l3.5-1 3.5 1v-1.5L13 19v-5.5l8 2.5z"/></g>'
body = "".join(
    f'<path stroke="{COL[k]}" stroke-width="{R*2}" stroke-linecap="round" d="{d}"/>' for k, d in paths.items() if d
)
legend = "".join(
    f'<path stroke="{COL[k]}" stroke-width="{R*2}" stroke-linecap="round" d="M{W-190+k*20+60} 250h0"/>' for k in COL
)
svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="100%" role="img" aria-label="{total} GitHub contributions in the last year, shown as a departures board">
<style>@keyframes b{{0%,55%{{opacity:1}}70%,90%{{opacity:.15}}100%{{opacity:1}}}}.bk{{animation:b 2.4s ease-in-out infinite}}.t{{font:700 34px 'Helvetica Neue',Arial,sans-serif;fill:#fff;letter-spacing:-.5px}}.h{{font:600 16px 'Helvetica Neue',Arial,sans-serif;fill:#7a7a7f}}.m{{font:600 12px 'Helvetica Neue',Arial,sans-serif;fill:#7a7a7f}}.w{{font:600 14px 'Helvetica Neue',Arial,sans-serif;fill:#fff}}</style>
<rect width="{W}" height="{H}" rx="14" fill="#0e0e0f"/>
<rect x="28" y="20" width="48" height="48" rx="11" fill="#fff"/>{plane}
<text class="t" x="94" y="56">Activity</text>
<text class="h" x="{W-28}" y="54" text-anchor="end">{total:,} contributions in the last year</text>
{months}
<text class="m" x="28" y="{Y0+P+4}">MON</text><text class="m" x="28" y="{Y0+3*P+4}">WED</text><text class="m" x="28" y="{Y0+5*P+4}">FRI</text>
{body}{mark}
<text class="m" x="{W-200}" y="256" text-anchor="end">LESS</text>{legend}<text class="m" x="{W-38}" y="256">MORE</text>
<text class="w" x="28" y="256">{user.upper()} &#183; UPDATED {date.today().isoformat()}</text>
</svg>'''
os.makedirs("assets", exist_ok=True)
open("assets/heatmap.svg", "w").write(svg)
print(f"wrote assets/heatmap.svg: {total} contributions, {weeks} weeks")
