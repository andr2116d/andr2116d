import math
from pathlib import Path
from xml.sax.saxutils import escape

from github_api import USER
from header import THEMES, SANS, MONO

ROOT = Path(__file__).resolve().parent.parent
W, H = 1200, 230

UI = {
    "es": dict(bye="Gracias por pasar", sub=f"{USER}  ·  Trujillo, Perú"),
    "en": dict(bye="Thanks for stopping by", sub=f"{USER}  ·  Trujillo, Peru"),
}


def build(lang: str, theme: str) -> str:
    c, u = THEMES[theme], UI[lang]
    layers = [[(90, y) for y in (70, 115, 160)], [(190, y) for y in (50, 95, 140, 185)], [(290, y) for y in (92, 138)]]
    cx, cy, r = 1060, 115, 40
    hexa = [(cx + r * math.cos(math.radians(a)), cy + r * math.sin(math.radians(a))) for a in range(-90, 270, 60)]
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" '
         f'aria-label="{escape(u["bye"])}">',
         f"""<style>
  .edge {{ stroke:{c['edge']}; stroke-width:1.2; }}
  .flow {{ stroke:{c['accent']}; stroke-width:1.3; stroke-dasharray:4 14; opacity:.5; animation: flow 2.4s linear infinite; }}
  .beat {{ transform-box:fill-box; transform-origin:center; animation: beat 2.8s ease-in-out infinite; }}
  .ring {{ transform-origin:{cx}px {cy}px; animation: spin 12s linear infinite reverse; }}
  @keyframes flow {{ to {{ stroke-dashoffset:-36; }} }}
  @keyframes beat {{ 0%,100% {{ transform:scale(.55); opacity:.55 }} 50% {{ transform:scale(1); opacity:1 }} }}
  @keyframes spin {{ to {{ transform:rotate(360deg); }} }}
</style>
<defs>
  <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="{c['bg1']}"/><stop offset="1" stop-color="{c['bg2']}"/></linearGradient>
  <linearGradient id="line" x1="0" x2="1">
    <stop offset="0" stop-color="{c['accent']}"/><stop offset="1" stop-color="{c['accent2']}"/></linearGradient>
  <radialGradient id="glow" cx=".5" cy=".5" r=".5">
    <stop offset="0" stop-color="{c['accent2']}" stop-opacity=".14"/>
    <stop offset="1" stop-color="{c['accent2']}" stop-opacity="0"/></radialGradient>
  <pattern id="dots" width="24" height="24" patternUnits="userSpaceOnUse">
    <circle cx="2" cy="2" r="1.1" fill="{c['grid']}"/></pattern>
</defs>""",
         f'<rect width="{W}" height="{H}" rx="18" fill="url(#bg)"/>',
         f'<rect width="{W}" height="{H}" rx="18" fill="url(#dots)" opacity=".6"/>',
         f'<rect width="{W}" height="{H}" rx="18" fill="url(#glow)"/>']
    add = o.append

    # red: aristas fijas + flujo
    for la, lb in zip(layers, layers[1:]):
        for a in la:
            for b in lb:
                add(f'<line class="edge" x1="{a[0]}" y1="{a[1]}" x2="{b[0]}" y2="{b[1]}"/>')
    bridge = [layers[2][0], (480, 8), (820, 8), hexa[5]]
    bridge2 = [layers[2][1], (480, 222), (820, 222), hexa[3]]
    for k, pts in enumerate((bridge, bridge2)):
        d = (f"M{pts[0][0]:.0f},{pts[0][1]:.0f} C{pts[1][0]},{pts[1][1]} {pts[2][0]},{pts[2][1]} "
             f"{pts[3][0]:.0f},{pts[3][1]:.0f}")
        add(f'<path d="{d}" fill="none" stroke="{c["edge"]}" stroke-width="1.2" stroke-dasharray="2 7"/>')
        col = c["accent"] if k == 0 else c["accent2"]
        add(f'<circle r="3.6" fill="{col}"><animateMotion dur="4.5s" begin="{k * 2.2}s" repeatCount="indefinite" '
            f'path="{d}"/><animate attributeName="opacity" values="0;1;1;0" keyTimes="0;.08;.9;1" dur="4.5s" '
            f'begin="{k * 2.2}s" repeatCount="indefinite"/></circle>')
    for la, lb in zip(layers, layers[1:]):
        for i, a in enumerate(la):
            for j, b in enumerate(lb):
                if (i + j) % 2 == 0:
                    add(f'<line class="flow" style="animation-delay:-{(i + j) * .4:.1f}s" x1="{a[0]}" y1="{a[1]}" '
                        f'x2="{b[0]}" y2="{b[1]}"/>')
    for li, layer in enumerate(layers):
        for ni, (x, y) in enumerate(layer):
            add(f'<circle cx="{x}" cy="{y}" r="10" fill="{c["bg2"]}" stroke="{c["accent2"]}" stroke-width="2"/>'
                f'<circle class="beat" style="animation-delay:-{li * .9 + ni * .4:.1f}s" cx="{x}" cy="{y}" r="5" '
                f'fill="{c["accent2"]}"/>')

    # molécula
    pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in hexa)
    add(f'<polygon points="{pts}" fill="none" stroke="{c["accent"]}" stroke-width="2.5"/>')
    add(f'<circle class="ring" cx="{cx}" cy="{cy}" r="21" fill="none" stroke="{c["accent"]}" stroke-width="1.5" '
        f'stroke-dasharray="5 6" opacity=".7"/>')
    for i, (x, y) in enumerate(hexa):
        add(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="8" fill="{c["bg2"]}" stroke="{c["accent"]}" stroke-width="2.5"/>'
            f'<circle class="beat" style="animation-delay:-{i * .45:.2f}s" cx="{x:.1f}" cy="{y:.1f}" r="4" '
            f'fill="{c["accent"]}"/>')

    # despedida
    add(f'<text x="{W / 2}" y="112" text-anchor="middle" font-family="{SANS}" font-size="38" font-weight="700" '
        f'fill="{c["text"]}">{escape(u["bye"])}</text>')
    add(f'<rect x="{W / 2 - 32}" y="130" width="64" height="4" rx="2" fill="url(#line)"/>')
    add(f'<text x="{W / 2}" y="166" text-anchor="middle" font-family="{MONO}" font-size="16" '
        f'fill="{c["muted"]}">{escape(u["sub"])}</text>')
    add('</svg>')
    return "\n".join(o)


if __name__ == "__main__":
    out = ROOT / "assets"
    for lang in UI:
        for theme in THEMES:
            (out / f"footer-{lang}-{theme}.svg").write_text(build(lang, theme), encoding="utf-8")
    print("ok")