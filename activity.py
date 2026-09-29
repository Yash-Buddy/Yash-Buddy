"""Builds assets/activity.svg (departures-board style GitHub activity).
Usage: GH_TOKEN=... python activity.py [username]   (no token -> '---' placeholders)"""
import json, os, re, sys, urllib.request

USER = sys.argv[1] if len(sys.argv) > 1 else "Yash-Buddy"
F = {}
def g(ch, *rows): F[ch] = rows
g("A","01110","10001","10001","11111","10001","10001","10001"); g("B","11110","10001","10001","11110","10001","10001","11110")
g("C","01110","10001","10000","10000","10000","10001","01110"); g("D","11110","10001","10001","10001","10001","10001","11110")
g("E","11111","10000","10000","11110","10000","10000","11111"); g("F","11111","10000","10000","11110","10000","10000","10000")
g("G","01110","10001","10000","10111","10001","10001","01111"); g("H","10001","10001","10001","11111","10001","10001","10001")
g("I","01110","00100","00100","00100","00100","00100","01110"); g("J","00111","00010","00010","00010","00010","10010","01100")
g("K","10001","10010","10100","11000","10100","10010","10001"); g("L","10000","10000","10000","10000","10000","10000","11111")
g("M","10001","11011","10101","10101","10001","10001","10001"); g("N","10001","11001","10101","10011","10001","10001","10001")
g("O","01110","10001","10001","10001","10001","10001","01110"); g("P","11110","10001","10001","11110","10000","10000","10000")
g("Q","01110","10001","10001","10001","10101","10010","01101"); g("R","11110","10001","10001","11110","10100","10010","10001")
g("S","01111","10000","10000","01110","00001","00001","11110"); g("T","11111","00100","00100","00100","00100","00100","00100")
g("U","10001","10001","10001","10001","10001","10001","01110"); g("V","10001","10001","10001","10001","10001","01010","00100")
g("W","10001","10001","10001","10101","10101","11011","10001"); g("X","10001","10001","01010","00100","01010","10001","10001")
g("Y","10001","10001","01010","00100","00100","00100","00100"); g("Z","11111","00001","00010","00100","01000","10000","11111")
g("0","01110","10001","10011","10101","11001","10001","01110"); g("1","00100","01100","00100","00100","00100","00100","01110")
g("2","01110","10001","00001","00010","00100","01000","11111"); g("3","11110","00001","00001","01110","00001","00001","11110")
g("4","00010","00110","01010","10010","11111","00010","00010"); g("5","11111","10000","11110","00001","00001","10001","01110")
g("6","00110","01000","10000","11110","10001","10001","01110"); g("7","11111","00001","00010","00100","01000","01000","01000")
g("8","01110","10001","10001","01110","10001","10001","01110"); g("9","01110","10001","10001","01111","00001","00010","01100")
g("-","00000","00000","00000","11111","00000","00000","00000"); g(" ","00000"*1,*["00000"]*6)

def dots(text, x, y):
    d = []
    for i, ch in enumerate(text.upper()):
        for r, row in enumerate(F.get(ch, F[" "])):
            for c, bit in enumerate(row):
                if bit == "1":
                    d.append(f"M{x + i*24 + c*4} {y + r*4}h0")
    return "".join(d)

def stats():
    tok = os.environ.get("GH_TOKEN")
    if not tok:
        return ["---"] * 4
    q = '{user(login:"%s"){contributionsCollection{contributionCalendar{totalContributions weeks{contributionDays{contributionCount}}}}}}' % USER
    req = urllib.request.Request("https://api.github.com/graphql", json.dumps({"query": q}).encode(),
                                 {"Authorization": f"bearer {tok}", "Content-Type": "application/json"})
    cal = json.load(urllib.request.urlopen(req))["data"]["user"]["contributionsCollection"]["contributionCalendar"]
    days = [d["contributionCount"] for w in cal["weeks"] for d in w["contributionDays"]]
    week = sum(d["contributionCount"] for d in cal["weeks"][-1]["contributionDays"])
    best = run = 0
    for n in days:
        run = run + 1 if n else 0
        best = max(best, run)
    return [str(cal["totalContributions"]), str(week), f"{best} DAYS", str(sum(1 for n in days if n))]

tpl = open("assets/board-code.svg").read()
head = tpl[:tpl.index('<rect width="900"')]          # svg tag + style + defs
labels = ["LAST 12 MONTHS", "THIS WEEK", "LONGEST STREAK", "ACTIVE DAYS"]
vals = stats()
rows = ""
for i, (lab, val) in enumerate(zip(labels, vals)):
    y = 70 + i * 36
    first = i == 0
    cls, col = ("as", "#3d7bff") if first else ("", "#f2f2f2")
    p = lambda k, t, x, c=col, cl=cls: (f'<path class="{cl}" stroke="{c}" stroke-width="3.2" stroke-linecap="round" fill="none" d="{dots(t, x, y)}"/>')
    rows += (f'<g opacity="0"><animate attributeName="opacity" from="0" to="1" dur=".4s" begin="{i*0.15:.2f}s" fill="freeze"/>'
             + p(0, f"A0{i+1}", 30) + p(0, lab, 194) + p(0, val, 674, "#ffb020", "bk" if first else "") + "</g>")
svg = (head.replace(re.search(r'viewBox="[^"]*"', head).group(0), 'viewBox="0 0 900 236"').replace('aria-label="Code skills board"', 'aria-label="GitHub activity board"')
       + '<rect width="900" height="236" rx="14" fill="#0e0e0f"/>'
       + '<text class="h" x="28" y="52">Gate</text><text class="h" x="192" y="52">Activity</text><text class="h g" x="672" y="52">Count</text>'
       + '<rect x="28" y="64" width="844" height="152" fill="url(#p)"/>' + rows + "</svg>")
open("assets/activity.svg", "w").write(svg)
print("wrote assets/activity.svg", vals)
