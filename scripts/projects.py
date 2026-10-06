"""Sección de proyectos que se actualiza sola.

1. Lee tus repos públicos desde la API de GitHub.
2. Se queda solo con los que tienen el topic `portfolio` o `featured`.
3. Si el repo tiene un `portfolio.yml`, usa sus textos (es/en), stack y orden.
   Si no, usa la descripción del About y los lenguajes que detecta GitHub.
4. Genera una tarjeta SVG por proyecto (es/en x oscuro/claro) en assets/projects/.
5. Reescribe la sección entre <!-- PROYECTOS:INICIO --> y <!-- PROYECTOS:FIN -->
   en README.md y README.en.md.
"""
import base64
import hashlib
import re
import sys
import urllib.parse
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path
from xml.sax.saxutils import escape

import yaml

from github_api import USER, all_repos, api, fetch
from header import THEMES, SANS, MONO

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "projects"
TOPICS = {"portfolio", "featured"}
LINKS = {"es": f"https://github.com/{USER}", "en": f"https://github.com/{USER}/{USER}/blob/main/README.en.md"}

LANG_COLORS = {
    "Python": "#3572A5", "TypeScript": "#3178c6", "JavaScript": "#f1e05a", "Go": "#00ADD8",
    "HTML": "#e34c26", "CSS": "#663399", "HCL": "#844FBA", "Dockerfile": "#384d54",
    "Shell": "#89e051", "Jupyter Notebook": "#DA5B0B", "Astro": "#ff5a03", "Java": "#b07219",
    "C++": "#f34b7d", "C": "#555555", "Rust": "#dea584", "PHP": "#4F5D95", "Vue": "#41b883",
    "Kotlin": "#A97BFF", "Dart": "#00B4AB", "SQL": "#e38c00", "MATLAB": "#e16737",
}

UI = {
    "es": dict(title="Proyectos", tag="// portafolio", live="Demo en vivo",
               updated="Actualizado", demo="Demos en vivo", more="Ver {n} proyectos más",
               months="ene feb mar abr may jun jul ago sep oct nov dic".split()),
    "en": dict(title="Projects", tag="// portfolio", live="Live demo",
               updated="Updated", demo="Live demos", more="Show {n} more projects",
               months="Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split()),
}

CW, CH = 600, 400  
COVER_H = 130      
CHIP_Y = 290
BAR_Y = 334
MAX_BIG = 6       

def portfolio_yml(repo: dict) -> dict:
    url = f"https://raw.githubusercontent.com/{USER}/{repo['name']}/{repo['default_branch']}/portfolio.yml"
    try:
        return yaml.safe_load(fetch(url, auth=False).decode("utf-8")) or {}
    except Exception:
        return {}


IGNORE_DIRS = ("node_modules/", ".next/", "dist/", "build/", "vendor/", ".git/")
DEFAULT_ASSETS = {"next.svg", "vercel.svg", "file.svg", "globe.svg", "window.svg", "astro.svg",
                  "vite.svg", "react.svg", "svelte.svg", "nuxt.svg", "turbo.svg"}


def logo_rank(path: str):
    low = path.lower()
    name = low.rsplit("/", 1)[-1]
    if any(d in low for d in IGNORE_DIRS) or name in DEFAULT_ASSETS:
        return None
    if not name.endswith((".svg", ".png")):
        return None              
    if "wordmark" in name or "banner" in name or "screenshot" in name:
        return None                     
    order = [
        lambda n, l: l.endswith("app/icon.svg") or l.endswith("app/icon.png"),
        lambda n, l: n in ("favicon.svg", "icon.svg", "icon-source.svg", "logo-icon.svg", "isotipo.svg"),
        lambda n, l: n in ("logo.svg", "logo.png"),
        lambda n, l: n.startswith(("favicon-", "android-chrome-", "apple-touch-icon", "icon-")) and n.endswith(".png"),
    ]
    for i, rule in enumerate(order):
        if rule(name, low):
            return i
    return None

def is_square(data: bytes, mime: str) -> bool:
    if mime == "image/png":
        w, h = int.from_bytes(data[16:20], "big"), int.from_bytes(data[20:24], "big")
        return w >= 96 and 0.8 <= w / max(h, 1) <= 1.25
    m = re.search(rb'viewBox="\s*[-\d.]+[\s,]+[-\d.]+[\s,]+([\d.]+)[\s,]+([\d.]+)', data)
    if not m:
        m = re.search(rb'width="([\d.]+)(?:px)?"[^>]*height="([\d.]+)', data)
    if not m:
        return True
    w, h = float(m.group(1)), float(m.group(2))
    return 0.8 <= w / max(h, 1) <= 1.25


def find_logo(paths: list[str], read, forced: str = "") -> str:
    if forced:
        candidates = [forced]
    else:
        candidates = sorted((q for q in paths if logo_rank(q) is not None),
                            key=lambda q: (logo_rank(q), png_size_penalty(q), len(q)))
    for path in candidates[:6]:
        try:
            data = read(path)
        except Exception:
            continue
        mime = "image/svg+xml" if path.lower().endswith(".svg") else "image/png"
        if len(data) > 150_000 or not is_square(data, mime):
            continue
        return f"data:{mime};base64,{base64.b64encode(data).decode()}"
    return ""


def png_size_penalty(path: str) -> int:
    nums = re.findall(r"(\d+)", path.rsplit("/", 1)[-1])
    if not path.endswith(".png") or not nums:
        return 0
    n = int(nums[-1])
    return abs(n - 192) if n >= 128 else 1000 + (128 - n)


def load_repo(r: dict) -> dict:
    yml = portfolio_yml(r)
    return dict(
        name=r["name"], url=r["html_url"], homepage=r.get("homepage") or "",
        description=r.get("description") or "", topics=r.get("topics", []),
        stars=r["stargazers_count"], pushed_at=r["pushed_at"],
        languages=api(f"/repos/{USER}/{r['name']}/languages"),
        portfolio=yml, logo=repo_logo(r, yml.get("logo", "")),
    )


def from_github() -> list[dict]:
    selected = [r for r in all_repos()
                if not r["fork"] and not r["archived"] and TOPICS & set(r.get("topics", []))]
    items = []
    with ThreadPoolExecutor(max_workers=6) as pool:
        futures = {pool.submit(load_repo, r): r["name"] for r in selected}
        for fut in as_completed(futures):
            try:
                items.append(fut.result())
            except Exception as e:  
                print(f"aviso: se omitió {futures[fut]} ({e})", file=sys.stderr)
    if selected and not items:
        raise SystemExit("No se pudo leer ningún repo: no se modifica el README.")
    return items


def repo_logo(repo: dict, forced: str) -> str:
    base = f"https://raw.githubusercontent.com/{USER}/{repo['name']}/{repo['default_branch']}/"
    try:
        tree = api(f"/repos/{USER}/{repo['name']}/git/trees/{repo['default_branch']}?recursive=1")
        paths = [t["path"] for t in tree.get("tree", []) if t["type"] == "blob"]
    except Exception:
        paths = []

    def read(path: str) -> bytes:
        return fetch(base + urllib.parse.quote(path), auth=False)
    return find_logo(paths, read, forced)


def normalize(raw: dict) -> dict:
    p = raw.get("portfolio") or {}
    title = p.get("titulo") or p.get("title") or raw["name"].replace("-", " ").replace("_", " ").title()
    desc_es = p.get("es") or raw["description"]
    desc_en = p.get("en") or raw["description"] or desc_es
    langs = raw.get("languages") or {}
    total = sum(langs.values()) or 1
    lang_share = [(k, v / total) for k, v in sorted(langs.items(), key=lambda kv: -kv[1])]
    stack = p.get("stack") or [k for k, _ in lang_share[:4]]
    return dict(
        slug=raw["name"].lower(), title=title, desc={"es": desc_es, "en": desc_en},
        stack=stack[:5], langs=lang_share, url=raw["url"], demo=p.get("demo") or raw["homepage"],
        stars=raw["stars"], pushed=datetime.fromisoformat(raw["pushed_at"].replace("Z", "+00:00")),
        featured="featured" in raw["topics"] or bool(p.get("destacado") or p.get("featured")),
        order=p.get("orden", p.get("order", 100)),
        colors=p.get("portada") or p.get("cover"), 
        logo=raw.get("logo", ""),
    )

def wrap(text: str, width: int, max_lines: int) -> list[str]:
    lines, cur = [], ""
    for word in text.split():
        if len(cur) + len(word) + 1 > width and cur:
            lines.append(cur)
            cur = word
        else:
            cur = f"{cur} {word}".strip()
    lines.append(cur)
    if len(lines) > max_lines:
        lines = lines[:max_lines]
        lines[-1] = lines[-1].rstrip(".,;: ") + "…"
    return lines


COVERS = [("#06b6d4", "#7c3aed"), ("#0ea5e9", "#22d3ee"), ("#8b5cf6", "#ec4899"),
          ("#14b8a6", "#3b82f6"), ("#6366f1", "#06b6d4"), ("#a855f7", "#0ea5e9")]


def seeded(slug: str):
    h = int(hashlib.sha256(slug.encode()).hexdigest(), 16)
    state = [h]

    def rnd() -> float:
        state[0] = (state[0] * 6364136223846793005 + 1442695040888963407) % (1 << 64)
        return state[0] / (1 << 64)
    return h, rnd


def monogram(title: str) -> str:
    words = [w for w in title.replace("-", " ").split() if w[:1].isalpha()]
    return (words[0][0] + (words[1][0] if len(words) > 1 else "")).upper()


def cover(p: dict, w: float = None, h: float = None, clip: str = "", x0: float = .42, n: int = 9) -> list[str]:
    w, h = w or CW, h or COVER_H
    clip = clip or f"M1 17 a16 16 0 0 1 16 -16 H{CW - 17} a16 16 0 0 1 16 16 V{COVER_H} H1 Z"
    seed, rnd = seeded(p["slug"])
    c1, c2 = p["colors"] if p.get("colors") else COVERS[seed % len(COVERS)]
    angle = 20 + seed % 50
    o = [f'<defs><linearGradient id="cv" gradientTransform="rotate({angle})">'
         f'<stop offset="0" stop-color="{c1}"/><stop offset="1" stop-color="{c2}"/></linearGradient>'
         f'<clipPath id="top"><path d="{clip}"/></clipPath></defs>',
         '<g clip-path="url(#top)">',
         f'<rect width="{w}" height="{h}" fill="url(#cv)"/>']
    for k in range(3):
        y0 = h * (.3 + k * .23) + rnd() * h * .15
        o.append(f'<path d="M0 {y0:.0f} C {w * .3:.0f} {y0 - h * .3 + rnd() * h * .2:.0f}, '
                 f'{w * .6:.0f} {y0 + h * .3 - rnd() * h * .2:.0f}, {w} {y0 - h * .08:.0f}" fill="none" '
                 f'stroke="#fff" stroke-opacity=".10" stroke-width="{18 - k * 5}"/>')
    reach = min(w, h * 4.6) * .2
    pts = [(w * x0 + rnd() * w * (.97 - x0), 14 + rnd() * (h - 28)) for _ in range(n)]
    for i, (x, y) in enumerate(pts):
        for j in range(i + 1, len(pts)):
            x2, y2 = pts[j]
            if (x - x2) ** 2 + (y - y2) ** 2 < reach ** 2:
                o.append(f'<line x1="{x:.0f}" y1="{y:.0f}" x2="{x2:.0f}" y2="{y2:.0f}" stroke="#fff" stroke-opacity=".35"/>')
    for x, y in pts:
        r = 2.5 + rnd() * 3
        o.append(f'<circle class="twinkle" style="animation-delay:-{rnd() * 3:.1f}s" cx="{x:.0f}" cy="{y:.0f}" '
                 f'r="{r:.1f}" fill="#fff"/>')
    path = "M" + " L".join(f"{x:.0f},{y:.0f}" for x, y in sorted(pts)[:5])
    o.append(f'<circle r="3.5" fill="#fff"><animateMotion dur="4s" repeatCount="indefinite" path="{path}"/></circle>')
    o.append('</g>')
    return o


def card(p: dict, lang: str, theme: str) -> str:
    c, u = THEMES[theme], UI[lang]
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{CW}" height="{CH}" viewBox="0 0 {CW} {CH}" '
         f'role="img" aria-label="{escape(p["title"])}: {escape(p["desc"][lang])}">']
    add = o.append
    add(f"""<style>
  /* todo el contenido es visible desde el inicio: las animaciones solo decoran */
  .live {{ animation: live 1.8s ease-in-out infinite; }}
  .twinkle {{ animation: twinkle 3s ease-in-out infinite; }}
  .shine {{ animation: shine 3.5s ease-in-out infinite; }}
  @keyframes live {{ 50% {{ opacity:.3 }} }}
  @keyframes twinkle {{ 50% {{ opacity:.35 }} }}
  @keyframes shine {{ 0% {{ transform:translateX(-120px) }} 60%,100% {{ transform:translateX({CW}px) }} }}
</style>
<defs>
  <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="{c['bg1']}"/><stop offset="1" stop-color="{c['bg2']}"/>
  </linearGradient>
  <linearGradient id="gloss" x1="0" x2="1">
    <stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".5" stop-color="#fff" stop-opacity=".55"/>
    <stop offset="1" stop-color="#fff" stop-opacity="0"/>
  </linearGradient>
  <clipPath id="bar"><rect x="28" y="{BAR_Y}" width="{CW - 56}" height="8" rx="4"/></clipPath>
</defs>""")
    add(f'<rect x="1" y="1" width="{CW - 2}" height="{CH - 2}" rx="16" fill="url(#bg)"/>')
    o.extend(cover(p))
    add(f'<rect x="1" y="1" width="{CW - 2}" height="{CH - 2}" rx="16" fill="none" '
        f'stroke="{c["edge"]}" stroke-width="1.5"/>')

    add(f'<text x="24" y="36" font-family="{MONO}" font-size="15" fill="#fff" fill-opacity=".85">'
        f'{USER}/{escape(p["slug"])}</text>')
    if p["demo"]:
        w = len(u["live"]) * 8.4 + 40
        add(f'<g><rect x="{CW - 20 - w:.0f}" y="18" width="{w:.0f}" height="28" rx="14" fill="#000" fill-opacity=".35"/>'
            f'<circle class="live" cx="{CW - w + 1:.0f}" cy="32" r="5" fill="#4ade80"/>'
            f'<text x="{CW - w + 13:.0f}" y="37" font-family="{SANS}" font-size="14" font-weight="600" '
            f'fill="#fff">{u["live"]}</text></g>')

    add(f'<circle cx="64" cy="{COVER_H}" r="38" fill="{c["bg2"]}"/>'
        f'<circle cx="64" cy="{COVER_H}" r="32" fill="none" stroke="url(#cv)" stroke-width="3"/>')
    if p["logo"]:
        add(f'<image href="{p["logo"]}" x="42" y="{COVER_H - 22}" width="44" height="44" '
            f'preserveAspectRatio="xMidYMid meet"/>')
    else:
        add(f'<text x="64" y="{COVER_H + 9}" text-anchor="middle" font-family="{SANS}" font-size="26" '
            f'font-weight="800" fill="{c["text"]}">{monogram(p["title"])}</text>')

    add(f'<text x="116" y="{COVER_H + 36}" font-family="{SANS}" font-size="28" font-weight="700" '
        f'fill="{c["text"]}">{escape(p["title"])}</text>')
    add(f'<text font-family="{SANS}" font-size="19" fill="{c["text"]}" fill-opacity=".78">')
    for i, ln in enumerate(wrap(p["desc"][lang], 56, 3)):
        add(f'<tspan x="28" y="{COVER_H + 78 + i * 26}">{escape(ln)}</tspan>')
    add('</text>')

    x, cy = 28, CHIP_Y
    for s in p["stack"]:
        w = len(s) * 8.6 + 24
        if x + w > CW - 28:
            break
        add(f'<g><rect x="{x}" y="{cy}" width="{w:.0f}" height="28" rx="14" '
            f'fill="{c["accent"]}" fill-opacity=".1" stroke="{c["accent"]}" stroke-opacity=".45"/>'
            f'<text x="{x + w / 2:.0f}" y="{cy + 19}" text-anchor="middle" font-family="{MONO}" font-size="14" '
            f'fill="{c["accent"]}">{escape(s)}</text></g>')
        x += w + 8

    add(f'<rect x="28" y="{BAR_Y}" width="{CW - 56}" height="8" rx="4" fill="{c["edge"]}"/>')
    add('<g clip-path="url(#bar)">')
    bx = 28.0
    for name, share in p["langs"]:
        w = share * (CW - 56)
        add(f'<rect x="{bx:.1f}" y="{BAR_Y}" width="{w + .5:.1f}" height="8" '
            f'fill="{LANG_COLORS.get(name, c["muted"])}"/>')
        bx += w
    add(f'<rect class="shine" x="0" y="{BAR_Y}" width="100" height="8" fill="url(#gloss)"/></g>')

    lx, ly = 28, BAR_Y + 36
    for name, share in [l for l in p["langs"] if l[1] >= .01][:3]:
        label = f"{name} {share * 100:.0f}%"
        add(f'<circle cx="{lx + 5}" cy="{ly - 5}" r="5" fill="{LANG_COLORS.get(name, c["muted"])}"/>'
            f'<text x="{lx + 15}" y="{ly}" font-family="{SANS}" font-size="14" fill="{c["muted"]}">'
            f'{escape(label)}</text>')
        lx += len(label) * 7.4 + 32
    when = f'{u["updated"]} {u["months"][p["pushed"].month - 1]} {p["pushed"].year}'
    stars = f'★ {p["stars"]}   ' if p["stars"] else ""
    add(f'<text x="{CW - 28}" y="{ly}" text-anchor="end" font-family="{SANS}" font-size="14" '
        f'fill="{c["muted"]}">{stars}{when}</text>')
    add('</svg>')
    return "\n".join(o)


def compact_card(p: dict, lang: str, theme: str) -> str:
    c, u = THEMES[theme], UI[lang]
    W2, H2, band = CW, 170, 130
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W2}" height="{H2}" viewBox="0 0 {W2} {H2}" '
         f'role="img" aria-label="{escape(p["title"])}: {escape(p["desc"][lang])}">']
    add = o.append
    add(f"""<style>
  .live {{ animation: live 1.8s ease-in-out infinite; }}
  .twinkle {{ animation: twinkle 3s ease-in-out infinite; }}
  @keyframes live {{ 50% {{ opacity:.3 }} }}
  @keyframes twinkle {{ 50% {{ opacity:.35 }} }}
</style>
<defs><linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
  <stop offset="0" stop-color="{c['bg1']}"/><stop offset="1" stop-color="{c['bg2']}"/></linearGradient>
  <clipPath id="bar"><rect x="{band + 24}" y="134" width="{W2 - band - 48}" height="6" rx="3"/></clipPath></defs>""")
    add(f'<rect x="1" y="1" width="{W2 - 2}" height="{H2 - 2}" rx="16" fill="url(#bg)"/>')
    o.extend(cover(p, band, H2, f"M17 1 H{band} V{H2 - 1} H17 a16 16 0 0 1 -16 -16 V17 a16 16 0 0 1 16 -16 Z",
                   x0=0.05, n=6))
    add(f'<rect x="1" y="1" width="{W2 - 2}" height="{H2 - 2}" rx="16" fill="none" stroke="{c["edge"]}" stroke-width="1.5"/>')

    cx, cy = band / 2, H2 / 2
    add(f'<circle cx="{cx}" cy="{cy}" r="34" fill="{c["bg2"]}"/>'
        f'<circle cx="{cx}" cy="{cy}" r="29" fill="none" stroke="url(#cv)" stroke-width="3"/>')
    if p["logo"]:
        add(f'<image href="{p["logo"]}" x="{cx - 20}" y="{cy - 20}" width="40" height="40" '
            f'preserveAspectRatio="xMidYMid meet"/>')
    else:
        add(f'<text x="{cx}" y="{cy + 8}" text-anchor="middle" font-family="{SANS}" font-size="23" '
            f'font-weight="800" fill="{c["text"]}">{monogram(p["title"])}</text>')

    x = band + 24
    add(f'<text x="{x}" y="32" font-family="{MONO}" font-size="13" fill="{c["muted"]}">'
        f'{USER}/<tspan fill="{c["accent"]}">{escape(p["slug"])}</tspan></text>')
    if p["demo"]:
        add(f'<circle class="live" cx="{W2 - 70}" cy="27" r="4.5" fill="#3fb950"/>'
            f'<text x="{W2 - 60}" y="32" font-family="{SANS}" font-size="13" font-weight="600" fill="#3fb950">Demo</text>')
    add(f'<text x="{x}" y="64" font-family="{SANS}" font-size="24" font-weight="700" fill="{c["text"]}">'
        f'{escape(p["title"])}</text>')
    add(f'<text font-family="{SANS}" font-size="16.5" fill="{c["text"]}" fill-opacity=".78">')
    for i, ln in enumerate(wrap(p["desc"][lang], 48, 2)):
        add(f'<tspan x="{x}" y="{92 + i * 22}">{escape(ln)}</tspan>')
    add('</text>')

    add(f'<rect x="{x}" y="134" width="{W2 - x - 24}" height="6" rx="3" fill="{c["edge"]}"/><g clip-path="url(#bar)">')
    bx = float(x)
    for name, share in p["langs"]:
        w = share * (W2 - x - 24)
        add(f'<rect x="{bx:.1f}" y="134" width="{w + .5:.1f}" height="6" fill="{LANG_COLORS.get(name, c["muted"])}"/>')
        bx += w
    add('</g>')
    top = " · ".join(n for n, sh in p["langs"][:2] if sh >= .01)
    when = f'{u["months"][p["pushed"].month - 1]} {p["pushed"].year}'
    stars = f'★ {p["stars"]}   ' if p["stars"] else ""
    add(f'<text x="{x}" y="160" font-family="{SANS}" font-size="13" fill="{c["muted"]}">{escape(top)}</text>'
        f'<text x="{W2 - 24}" y="160" text-anchor="end" font-family="{SANS}" font-size="13" '
        f'fill="{c["muted"]}">{stars}{when}</text>')
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


def picture(name: str, alt: str, width: str) -> str:
    return (f'<picture><source media="(prefers-color-scheme: dark)" srcset="assets/{name}-dark.svg">'
            f'<img src="assets/{name}-light.svg" alt="{escape(alt, {chr(34): "&quot;"})}" width="{width}"></picture>')


def grid(projects: list[dict], lang: str, kind: str) -> list[str]:
    rows = []
    for i in range(0, len(projects), 2):
        cells = [f'<a href="{p["url"]}">{picture(f"projects/{p["slug"]}-{kind}{lang}", p["title"], "49%")}</a>'
                 for p in projects[i:i + 2]]
        rows.append('<p align="center">\n  ' + "\n  ".join(cells) + "\n</p>")
    return rows


def section(projects: list[dict], lang: str) -> str:
    u = UI[lang]
    if not projects:  
        return ""
    big, rest = projects[:MAX_BIG], projects[MAX_BIG:]
    parts = [f'<a href="{LINKS[lang]}">{picture(f"projects/title-{lang}", u["title"], "100%")}</a>', ""]
    parts += grid(big, lang, "")
    if rest:   
        parts.append(f'\n<details>\n<summary><b>{u["more"].format(n=len(rest))}</b></summary>\n<br>\n')
        parts += grid(rest, lang, "mini-")
        parts.append("</details>\n")
    demos = [f'<a href="{p["demo"]}">{escape(p["title"])} ↗</a>' for p in projects if p["demo"]]
    if demos:
        parts.append(f'<p align="center"><sub>{u["demo"]}: ' + " &nbsp;·&nbsp; ".join(demos) + "</sub></p>")
    return "\n".join(parts)


def replace_between(text: str, block: str) -> str:
    start, end = "<!-- PROYECTOS:INICIO -->", "<!-- PROYECTOS:FIN -->"
    if start not in text:
        return text.rstrip() + f"\n\n{start}\n{block}\n{end}\n"
    head, rest = text.split(start, 1)
    _, tail = rest.split(end, 1)
    return f"{head}{start}\n{block}\n{end}{tail}"


def render(raw: list[dict]) -> list[dict]:
    projects = sorted((normalize(r) for r in raw),
                      key=lambda p: (not p["featured"], p["order"], -p["pushed"].timestamp()))

    OUT.mkdir(parents=True, exist_ok=True)
    keep = set()
    for lang in UI:
        for theme in THEMES:
            name = f"title-{lang}-{theme}.svg"
            (OUT / name).write_text(title_svg(lang, theme), encoding="utf-8")
            keep.add(name)
            for p in projects[:MAX_BIG]:
                name = f'{p["slug"]}-{lang}-{theme}.svg'
                (OUT / name).write_text(card(p, lang, theme), encoding="utf-8")
                keep.add(name)
            for p in projects[MAX_BIG:]:
                name = f'{p["slug"]}-mini-{lang}-{theme}.svg'
                (OUT / name).write_text(compact_card(p, lang, theme), encoding="utf-8")
                keep.add(name)
    for old in OUT.glob("*.svg"):         
        if old.name not in keep:
            old.unlink()

    for readme, lang in (("README.md", "es"), ("README.en.md", "en")):
        path = ROOT / readme
        path.write_text(replace_between(path.read_text(encoding="utf-8"), section(projects, lang)),
                        encoding="utf-8")
    return projects


def main() -> None:
    projects = render(from_github())
    print(f"{len(projects)} proyectos:", ", ".join(p["title"] for p in projects) or "(ninguno con topic portfolio)")


if __name__ == "__main__":
    main()