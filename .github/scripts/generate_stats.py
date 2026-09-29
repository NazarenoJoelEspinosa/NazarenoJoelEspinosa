import os, json, urllib.request
from pathlib import Path
from collections import Counter

USER="NazarenoJoelEspinosa"
TOKEN=os.environ["GITHUB_TOKEN"]
HEADERS={"Authorization":f"Bearer {TOKEN}","Accept":"application/vnd.github+json","User-Agent":"profile-stats"}

def get(url):
    req=urllib.request.Request(url,headers=HEADERS)
    with urllib.request.urlopen(req) as r:
        return json.load(r)

u=get(f"https://api.github.com/users/{USER}")
repos=get(f"https://api.github.com/users/{USER}/repos?per_page=100&type=owner")
langs=Counter()

for r in repos:
    if r.get("fork"): continue
    try:
        for k,v in get(r["languages_url"]).items():
            langs[k]+=v
    except Exception:
        pass

def esc(x):
    return str(x).replace("&","&amp;").replace("<","&lt;").replace(">","&gt;").replace('"',"&quot;")

def svg(title,body,height):
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" width="760" height="'
        + str(height) + '" viewBox="0 0 760 ' + str(height) + '">'
        '<rect width="100%" height="100%" rx="18" fill="#0B1020" stroke="#4F46E5" stroke-width="2"/>'
        '<text x="32" y="48" font-family="Arial" font-size="25" font-weight="700" fill="#C4B5FD">'
        + esc(title) + '</text>' + body + '</svg>'
    )

Path("dist").mkdir(exist_ok=True)

values=[
    ("Repos",u.get("public_repos",0)),
    ("Stars",sum(r.get("stargazers_count",0) for r in repos)),
    ("Followers",u.get("followers",0)),
    ("Following",u.get("following",0)),
    ("Forks",sum(r.get("forks_count",0) for r in repos)),
]

body=""
for i,(label,value) in enumerate(values):
    x=32+(i%3)*245
    y=95+(i//3)*72
    body+=f'<text x="{x}" y="{y}" font-family="Arial" font-size="27" font-weight="700" fill="#F8FAFC">{value}</text>'
    body+=f'<text x="{x}" y="{y+23}" font-family="Arial" font-size="14" fill="#94A3B8">{esc(label)}</text>'

Path("dist/github-stats.svg").write_text(svg("GitHub Stats",body,220),encoding="utf-8")

top=langs.most_common(6)
total=sum(langs.values()) or 1
colors=["#4F46E5","#6366F1","#7C3AED","#8B5CF6","#A78BFA","#C4B5FD"]
body=""

for i,(name,value) in enumerate(top):
    pct=round(value/total*100,1)
    y=78+i*25
    width=max(4,pct*5.2)
    body+=f'<text x="32" y="{y}" font-family="Arial" font-size="14" fill="#E2E8F0">{esc(name)}</text>'
    body+=f'<rect x="145" y="{y-13}" width="{width:.1f}" height="12" rx="6" fill="{colors[i]}"/>'
    body+=f'<text x="670" y="{y}" font-family="Arial" font-size="13" fill="#94A3B8" text-anchor="end">{pct}%</text>'

Path("dist/github-languages.svg").write_text(svg("Top Languages",body,250),encoding="utf-8")
Path("dist/github-stats-dark.svg").write_text(Path("dist/github-stats.svg").read_text(),encoding="utf-8")
Path("dist/github-languages-dark.svg").write_text(Path("dist/github-languages.svg").read_text(),encoding="utf-8")
