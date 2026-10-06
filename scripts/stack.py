"""Stack tecnológico como una "tabla periódica" (SVG), en es/en x oscuro/claro.

Referencia aIngeniería Química: cada tecnología es un "elemento" con número,
símbolo de dos letras.

Los logos están guardados en scripts/icons.json. Para agregar una tecnología: añádela a
GROUPS y su logo a fetch_icons.py; si no tiene logo, sale un monograma.
"""
import json
from pathlib import Path
from xml.sax.saxutils import escape

from header import THEMES, SANS, MONO

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "stack"
ICONS = json.loads((Path(__file__).parent / "icons.json").read_text(encoding="utf-8"))

# (nombre visible, símbolo, slug del logo o None)
GROUPS = [
    (("Backend", "Backend"), [
        ("Go", "Go", "go"), ("Python", "Py", "python"), ("Node.js", "Nd", "nodedotjs"),
        ("FastAPI", "Fa", "fastapi"), ("Echo", "Ec", "echo")]),
    (("Frontend", "Frontend"), [
        ("TypeScript", "Ts", "typescript"), ("JavaScript", "Js", "javascript"), ("React", "Re", "react"),
        ("Next.js", "Nx", "nextdotjs"), ("Tailwind", "Tw", "tailwindcss"), ("Astro", "As", "astro")]),
    (("Datos e IA", "Data & AI"), [
        ("PyTorch", "Pt", "pytorch"), ("scikit-learn", "Sk", "scikitlearn"), ("pandas", "Pd", "pandas"),
        ("PostgreSQL", "Pg", "postgresql"), ("MongoDB", "Mg", "mongodb"), ("Redis", "Rd", "redis"),
        ("InfluxDB", "If", "influxdb"), ("Supabase", "Sb", "supabase")]),
    (("Cloud y herramientas", "Cloud & tools"), [
        ("AWS", "Aw", "aws"), ("Cloudflare", "Cf", "cloudflare"), ("Vercel", "Vc", "vercel"),
        ("Railway", "Rw", "railway"), ("Docker", "Dk", "docker"), ("Terraform", "Tf", "terraform"),
        ("Git", "Gt", "git"), ("Linux", "Lx", "linux"), ("Playwright", "Pw", "playwright")]),
]

GROUP_COLORS = {
    "dark": ["#0891b2", "#8b5cf6", "#ec4899", "#d97706"],
    "light": ["#0891b2", "#7c3aed", "#db2777", "#b45309"],
}

UI = {
    "es": dict(tag="// tabla periódica del stack", title="Stack tecnológico"),
    "en": dict(tag="// periodic table of my stack", title="Tech stack"),
}

TW, TH, GAP = 104, 116, 8          # tamaño de cada "elemento"
LABEL_W = 170                       # columna de etiquetas de grupo
W = 40 + LABEL_W + 9 * (TW + GAP) + 32


def luminance(hex_color: str) -> float:
    rgb = [int(hex_color.lstrip("#")[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    lin = [v / 12.92 if v <= .03928 else ((v + .055) / 1.055) ** 2.4 for v in rgb]
    return .2126 * lin[0] + .7152 * lin[1] + .0722 * lin[2]


def contrast(a: str, b: str) -> float:
    la, lb = sorted((luminance(a), luminance(b)), reverse=True)
    return (la + .05) / (lb + .05)


def logo(slug, name: str, symbol: str, x: float, y: float, c: dict) -> str:
    if slug and slug in ICONS and "svg" in ICONS[slug]:
        ic = ICONS[slug]
        inner = ic["svg"]
        for dark in ("#252f3e", "#252F3E"):
            if dark in inner and contrast(dark, c["bg2"]) < 1.9:
                inner = inner.replace(dark, c["text"])
        return (f'<svg x="{x - 20}" y="{y - 20}" width="40" height="40" viewBox="{ic["viewBox"]}" '
                f'preserveAspectRatio="xMidYMid meet">{inner}</svg>')
    if slug and slug in ICONS:
        ic = ICONS[slug]
        col = "#" + ic["hex"]
        if contrast(col, c["bg2"]) < 1.12:  
            col = c["text"]
        return (f'<g transform="translate({x - 18},{y - 18}) scale(1.5)">'
                f'<path d="{ic["path"]}" fill="{col}"/></g>')
    label = "AWS" if name == "AWS" else symbol
    return (f'<rect x="{x - 19}" y="{y - 19}" width="38" height="38" rx="9" fill="none" '
            f'stroke="{c["accent"]}" stroke-width="2"/>'
            f'<text x="{x}" y="{y + 6}" text-anchor="middle" font-family="{SANS}" font-size="{15 if len(label) > 2 else 17}" '
            f'font-weight="800" fill="{c["accent"]}">{label}</text>')


def build(lang: str, theme: str) -> str:
    c = THEMES[theme]
    colors = GROUP_COLORS[theme]
    rows = len(GROUPS)
    H = 40 + rows * (TH + 14) + 26
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" '
         f'aria-label="{escape(UI[lang]["title"])}: ' + escape("; ".join(
             f'{names[0 if lang == "es" else 1]}: ' + ", ".join(t[0] for t in items)
             for names, items in GROUPS)) + '">']
    add = o.append
    add(f"""<style>
  /* todo es visible siempre: las animaciones solo agregan luz y movimiento */
  .glow {{ animation: glow 4s ease-in-out infinite; }}
  .wave {{ opacity:0; animation: wave 6s ease-in-out infinite; }}
  .float {{ animation: float 5s ease-in-out infinite; }}
  .beam {{ animation: beam 7s ease-in-out infinite; }}
  @keyframes glow {{ 0%,100% {{ opacity:.55 }} 50% {{ opacity:1 }} }}
  @keyframes wave {{ 0%,100% {{ opacity:0 }} 8% {{ opacity:.95 }} 22% {{ opacity:0 }} }}
  @keyframes float {{ 0%,100% {{ transform:translateY(0) }} 50% {{ transform:translateY(-3px) }} }}
  @keyframes beam {{ 0% {{ transform:translateX(-260px) }} 55%,100% {{ transform:translateX({W + 60}px) }} }}
</style>
<defs>
  <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="{c['bg1']}"/><stop offset="1" stop-color="{c['bg2']}"/></linearGradient>
  <pattern id="dots" width="24" height="24" patternUnits="userSpaceOnUse">
    <circle cx="2" cy="2" r="1.1" fill="{c['grid']}"/></pattern>
  <linearGradient id="beamg" x1="0" x2="1">
    <stop offset="0" stop-color="{c['accent']}" stop-opacity="0"/>
    <stop offset=".5" stop-color="{c['accent']}" stop-opacity=".10"/>
    <stop offset="1" stop-color="{c['accent']}" stop-opacity="0"/></linearGradient>
  <clipPath id="card"><rect width="{W}" height="{H}" rx="18"/></clipPath>
</defs>""")
    add(f'<rect width="{W}" height="{H}" rx="18" fill="url(#bg)"/>'
        f'<rect width="{W}" height="{H}" rx="18" fill="url(#dots)" opacity=".5"/>')

    n = 0
    for r, ((name_es, name_en), items) in enumerate(GROUPS):
        col = colors[r]
        y = 40 + r * (TH + 14)
        gname = name_es if lang == "es" else name_en
        add(f'<text x="40" y="{y + 28}" font-family="{MONO}" font-size="14" fill="{c["muted"]}">0{r + 1}</text>'
            f'<rect x="40" y="{y + 40}" width="28" height="4" rx="2" fill="{col}"/>')
        words = gname.split(" ", 1) if len(gname) > 14 else [gname]
        for k, wline in enumerate(words):
            add(f'<text x="40" y="{y + 70 + k * 22}" font-family="{SANS}" font-size="18" font-weight="700" '
                f'fill="{c["text"]}">{escape(wline)}</text>')

        for i, (name, symbol, slug) in enumerate(items):
            n += 1
            x = 40 + LABEL_W + i * (TW + GAP)
            add(f'<g><rect x="{x}" y="{y}" width="{TW}" height="{TH}" rx="12" fill="{c["bg2"]}" '
                f'stroke="{c["edge"]}" stroke-width="1.2"/>'
                f'<rect class="glow" style="animation-delay:-{(n * .37) % 4:.2f}s" x="{x + 10}" y="{y}" '
                f'width="{TW - 20}" height="3" rx="1.5" fill="{col}"/>'
                f'<text x="{x + 10}" y="{y + 20}" font-family="{MONO}" font-size="12" fill="{c["muted"]}">{n}</text>'
                f'<text x="{x + TW - 10}" y="{y + 21}" text-anchor="end" font-family="{MONO}" font-size="14" '
                f'font-weight="700" fill="{col}">{symbol}</text>'
                + f'<g class="float" style="animation-delay:-{(n * .53) % 5:.2f}s">'
                + logo(slug, name, symbol, x + TW / 2, y + 56, c) + '</g>' +
                f'<text x="{x + TW / 2}" y="{y + TH - 14}" text-anchor="middle" font-family="{SANS}" '
                f'font-size="{13 if len(name) > 10 else 14}" fill="{c["text"]}">{escape(name)}</text>'
                f'<rect class="wave" style="animation-delay:{(i + r) * .18:.2f}s" x="{x}" y="{y}" width="{TW}" '
                f'height="{TH}" rx="12" fill="{col}" fill-opacity=".07" stroke="{col}" stroke-width="2"/></g>')
    add(f'<g clip-path="url(#card)"><rect class="beam" x="0" y="0" width="200" height="{H}" fill="url(#beamg)"/></g>')
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


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    for lang in UI:
        for theme in THEMES:
            (OUT / f"stack-{lang}-{theme}.svg").write_text(build(lang, theme), encoding="utf-8")
            (OUT / f"title-{lang}-{theme}.svg").write_text(title_svg(lang, theme), encoding="utf-8")
    print("ok", W)