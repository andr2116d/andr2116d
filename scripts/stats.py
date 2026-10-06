"""Panel de estadísticas propio (SVG), en es/en x oscuro/claro.

El panel muestra:
  - 4 indicadores: contribuciones del último año, racha actual, racha más larga
    y días activos.
  - Actividad semanal del último año (área con la línea en el color de acento).
  - Lenguajes más usados en tus repos públicos (con los colores de GitHub).

Los datos salen de la API GraphQL de GitHub. Si activas "Include private
contributions" en tu perfil, el calendario incluye tu trabajo privado (solo
cuenta, nunca muestra nombres ni código).

La API GraphQL siempre exige un token (aunque los datos sean públicos):
  - En GitHub Actions existe solo (GITHUB_TOKEN).
  - En tu computadora: export GITHUB_TOKEN=$(gh auth token)
"""
import json
import os
import urllib.request
from datetime import date
from pathlib import Path
from xml.sax.saxutils import escape

from header import THEMES, SANS, MONO
from github_api import USER
from projects import LANG_COLORS

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "stats"
W, H = 1200, 560

UI = {
    "es": dict(tag="// actividad", title="Estadísticas", contrib="contribuciones", contrib2="en 12 meses",
               cur="racha actual", longest="racha más larga", active="días activos", days="días",
               weekly="Actividad semanal", langs="Lenguajes más usados", week="esta semana",
               months="ene feb mar abr may jun jul ago sep oct nov dic".split()),
    "en": dict(tag="// activity", title="Stats", contrib="contributions", contrib2="in 12 months",
               cur="current streak", longest="longest streak", active="active days", days="days",
               weekly="Weekly activity", langs="Most used languages", week="this week",
               months="Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split()),
}

QUERY = """
query($login: String!, $cursor: String) {
  user(login: $login) {
    contributionsCollection {
      contributionCalendar {
        totalContributions
        weeks { contributionDays { contributionCount date } }
      }
    }
    repositories(ownerAffiliations: OWNER, isFork: false, privacy: PUBLIC, first: 100, after: $cursor) {
      pageInfo { hasNextPage endCursor }
      nodes { languages(first: 10, orderBy: {field: SIZE, direction: DESC}) { edges { size node { name } } } }
    }
  }
}"""

def graphql(variables: dict) -> dict:
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        raise SystemExit("Falta GITHUB_TOKEN. En tu computadora: export GITHUB_TOKEN=$(gh auth token)")
    req = urllib.request.Request(
        "https://api.github.com/graphql", method="POST",
        data=json.dumps({"query": QUERY, "variables": variables}).encode(),
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json",
                 "User-Agent": f"{USER}-profile"})
    with urllib.request.urlopen(req, timeout=30) as r:
        out = json.load(r)
    if out.get("errors"):
        raise SystemExit(f"GraphQL: {out['errors'][0].get('message')}")
    return out["data"]["user"]


def from_github() -> tuple[dict, dict]:
    langs, cursor, calendar = {}, None, None
    while True:
        user = graphql({"login": USER, "cursor": cursor})
        calendar = calendar or user["contributionsCollection"]["contributionCalendar"]
        repos = user["repositories"]
        for node in repos["nodes"]:
            for e in node["languages"]["edges"]:
                langs[e["node"]["name"]] = langs.get(e["node"]["name"], 0) + e["size"]
        if not repos["pageInfo"]["hasNextPage"]:
            return calendar, langs
        cursor = repos["pageInfo"]["endCursor"]


def metrics(calendar: dict) -> dict:
    days = [(date.fromisoformat(d["date"]), d["contributionCount"])
            for w in calendar["weeks"] for d in w["contributionDays"]]
    days.sort()
    counts = [c for _, c in days]
    # racha actual: si hoy aún no hay contribuciones, se cuenta desde ayer
    i = len(counts) - 1
    if counts and counts[i] == 0:
        i -= 1
    cur = 0
    while i >= 0 and counts[i] > 0:
        cur, i = cur + 1, i - 1
    longest = run = 0
    for c in counts:
        run = run + 1 if c else 0
        longest = max(longest, run)
    weeks = [sum(d["contributionCount"] for d in w["contributionDays"]) for w in calendar["weeks"]]
    week_start = [date.fromisoformat(w["contributionDays"][0]["date"]) for w in calendar["weeks"]]
    return dict(total=calendar["totalContributions"], cur=cur, longest=longest,
                active=sum(1 for c in counts if c), ndays=len(counts), weeks=weeks, week_start=week_start)



def smooth(pts: list[tuple[float, float]], y_min: float, y_max: float) -> str:
    d = f"M{pts[0][0]:.1f},{pts[0][1]:.1f}"
    for i in range(len(pts) - 1):
        p0, p1, p2 = pts[max(i - 1, 0)], pts[i], pts[i + 1]
        p3 = pts[min(i + 2, len(pts) - 1)]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, min(max(p1[1] + (p2[1] - p0[1]) / 6, y_min), y_max))
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, min(max(p2[1] - (p3[1] - p1[1]) / 6, y_min), y_max))
        d += f" C{c1[0]:.1f},{c1[1]:.1f} {c2[0]:.1f},{c2[1]:.1f} {p2[0]:.1f},{p2[1]:.1f}"
    return d


def tile(x, y, w, value, label, sub, c):
    return (f'<g><rect x="{x}" y="{y}" width="{w}" height="122" rx="14" fill="{c["bg2"]}" '
            f'stroke="{c["edge"]}" stroke-width="1.2"/>'
            f'<text x="{x + 24}" y="{y + 62}" font-family="{SANS}" font-size="46" font-weight="800" '
            f'fill="{c["text"]}" letter-spacing="-1">{escape(value)}'
            + (f'<tspan font-size="20" font-weight="600" fill="{c["muted"]}" letter-spacing="0"> {escape(sub)}</tspan>' if sub else "")
            + '</text>'
            f'<rect x="{x + 24}" y="{y + 76}" width="34" height="4" rx="2" fill="url(#line)"/>'
            f'<text x="{x + 24}" y="{y + 104}" font-family="{SANS}" font-size="17" fill="{c["text"]}" '
            f'fill-opacity=".75">{escape(label)}</text></g>')


def build(m: dict, langs: dict, lang: str, theme: str) -> str:
    c, u = THEMES[theme], UI[lang]
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" '
         f'aria-label="{u["title"]}: {m["total"]} {u["contrib"]} {u["contrib2"]}; {u["cur"]} {m["cur"]} {u["days"]}; '
         f'{u["longest"]} {m["longest"]} {u["days"]}">']
    add = o.append
    add(f"""<style>
  .twinkle {{ animation: tw 2s ease-in-out infinite; }}
  @keyframes tw {{ 50% {{ opacity:.35 }} }}
</style>
<defs>
  <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="{c['bg1']}"/><stop offset="1" stop-color="{c['bg2']}"/></linearGradient>
  <linearGradient id="line" x1="0" x2="1">
    <stop offset="0" stop-color="{c['accent']}"/><stop offset="1" stop-color="{c['accent2']}"/></linearGradient>
  <linearGradient id="area" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="{c['accent']}" stop-opacity=".35"/>
    <stop offset="1" stop-color="{c['accent']}" stop-opacity="0"/></linearGradient>
  <pattern id="dots" width="24" height="24" patternUnits="userSpaceOnUse">
    <circle cx="2" cy="2" r="1.1" fill="{c['grid']}"/></pattern>
</defs>""")
    add(f'<rect width="{W}" height="{H}" rx="18" fill="url(#bg)"/>'
        f'<rect width="{W}" height="{H}" rx="18" fill="url(#dots)" opacity=".5"/>')

    pct = round(100 * m["active"] / max(m["ndays"], 1))
    tiles = [(f'{m["total"]:,}'.replace(",", "." if lang == "es" else ","), f'{u["contrib"]} {u["contrib2"]}', ""),
             (f'{m["cur"]}', u["cur"], u["days"]), (f'{m["longest"]}', u["longest"], u["days"]),
             (f'{pct}%', u["active"], "")]
    tw, gap = (W - 80 - 3 * 24) / 4, 24
    for k, (v, lab, sub) in enumerate(tiles):
        add(tile(40 + k * (tw + gap), 36, tw, v, lab, sub, c))

    x0, y0, cw, ch = 64, 236, 660, 230
    add(f'<text x="40" y="208" font-family="{SANS}" font-size="20" font-weight="700" fill="{c["text"]}">'
        f'{u["weekly"]}</text>')
    wk = m["weeks"]
    top = max(wk) or 1
    step = cw / (len(wk) - 1)
    pts = [(x0 + i * step, y0 + ch - v / top * ch) for i, v in enumerate(wk)]
    line = smooth(pts, y0, y0 + ch)
    add(f'<line x1="{x0}" y1="{y0 + ch}" x2="{x0 + cw}" y2="{y0 + ch}" stroke="{c["edge"]}" stroke-width="1.5"/>')
    add(f'<line x1="{x0}" y1="{y0}" x2="{x0 + cw}" y2="{y0}" stroke="{c["edge"]}" stroke-dasharray="3 6"/>'
        f'<text x="{x0 - 10}" y="{y0 + 5}" text-anchor="end" font-family="{MONO}" font-size="13" '
        f'fill="{c["muted"]}">{top}</text>'
        f'<text x="{x0 - 10}" y="{y0 + ch + 5}" text-anchor="end" font-family="{MONO}" font-size="13" '
        f'fill="{c["muted"]}">0</text>')
    add(f'<path d="{line} L{x0 + cw},{y0 + ch} L{x0},{y0 + ch} Z" fill="url(#area)"/>')
    add(f'<path d="{line}" fill="none" stroke="url(#line)" stroke-width="2.5" stroke-linejoin="round" '
        f'stroke-linecap="round"/>')
    add(f'<circle r="4" fill="{c["accent"]}" opacity=".9"><animateMotion dur="7s" repeatCount="indefinite" '
        f'path="{line}"/></circle>')

    seen = set()
    for i, d in enumerate(m["week_start"]):
        if d.day <= 7 and d.month not in seen:
            seen.add(d.month)
            add(f'<text x="{x0 + i * step:.0f}" y="{y0 + ch + 24}" text-anchor="middle" font-family="{SANS}" '
                f'font-size="13" fill="{c["muted"]}">{u["months"][d.month - 1]}</text>')
    lx, ly = pts[-1]
    add(f'<circle cx="{lx:.1f}" cy="{ly:.1f}" r="7" fill="{c["bg2"]}" stroke="{c["accent2"]}" stroke-width="3"/>'
        f'<circle class="twinkle" cx="{lx:.1f}" cy="{ly:.1f}" r="13" fill="none" stroke="{c["accent2"]}" '
        f'stroke-opacity=".5"/>'
        f'<rect x="{lx - 128:.1f}" y="{ly - 46:.1f}" width="116" height="26" rx="13" fill="{c["bg2"]}" '
        f'stroke="{c["edge"]}"/>'
        f'<text x="{lx - 70:.1f}" y="{ly - 28:.1f}" text-anchor="middle" font-family="{SANS}" font-size="13.5" '
        f'fill="{c["text"]}"><tspan font-weight="700">{wk[-1]}</tspan> {u["week"]}</text>')

    lx0, ly0, bw = 790, 236, 370
    add(f'<line x1="760" y1="200" x2="760" y2="{H - 40}" stroke="{c["edge"]}"/>')
    add(f'<text x="{lx0}" y="208" font-family="{SANS}" font-size="20" font-weight="700" fill="{c["text"]}">'
        f'{u["langs"]}</text>')
    total = sum(langs.values()) or 1
    ranked = sorted(langs.items(), key=lambda kv: -kv[1])
    top5 = ranked[:5]
    other = sum(v for _, v in ranked[5:])
    if other / total >= .01:
        top5.append(("Otros" if lang == "es" else "Other", other))
    for k, (name, v) in enumerate(top5):
        y = ly0 + k * 50
        share = v / total
        col = LANG_COLORS.get(name, c["muted"])
        add(f'<text x="{lx0}" y="{y + 4}" font-family="{SANS}" font-size="16" fill="{c["text"]}">{escape(name)}</text>'
            f'<text x="{lx0 + bw}" y="{y + 4}" text-anchor="end" font-family="{MONO}" font-size="15" '
            f'fill="{c["muted"]}">{share * 100:.1f}%</text>'
            f'<rect x="{lx0}" y="{y + 14}" width="{bw}" height="10" rx="5" fill="{c["edge"]}" fill-opacity=".6"/>'
            f'<rect x="{lx0}" y="{y + 14}" width="{max(10, share * bw):.1f}" height="10" rx="5" fill="{col}"/>')
    add('</svg>')
    return "\n".join(o)


def title_svg(lang: str, theme: str) -> str:
    c, u = THEMES[theme], UI[lang]
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="96" viewBox="0 0 1200 96" '
            f'role="img" aria-label="{u["title"]}"><defs><linearGradient id="l" x1="0" x2="1">'
            f'<stop offset="0" stop-color="{c["accent"]}"/><stop offset="1" stop-color="{c["accent2"]}"/>'
            f'</linearGradient></defs>'
            f'<text x="4" y="26" font-family="{MONO}" font-size="18" fill="{c["accent"]}">{u["tag"]}</text>'
            f'<text x="4" y="70" font-family="{SANS}" font-size="40" font-weight="700" fill="{c["text"]}">'
            f'{u["title"]}</text><rect x="4" y="84" width="64" height="4" rx="2" fill="url(#l)"/></svg>')


def render(calendar: dict, langs: dict) -> dict:
    m = metrics(calendar)
    OUT.mkdir(parents=True, exist_ok=True)
    for lang in UI:
        for theme in THEMES:
            (OUT / f"stats-{lang}-{theme}.svg").write_text(build(m, langs, lang, theme), encoding="utf-8")
            (OUT / f"title-{lang}-{theme}.svg").write_text(title_svg(lang, theme), encoding="utf-8")
    return m


def main() -> None:
    m = render(*from_github())
    print(f"{m['total']} contribuciones · racha actual {m['cur']} · racha más larga {m['longest']}")


if __name__ == "__main__":
    main()