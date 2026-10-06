"""Genera la cabecera animada del perfil (SVG) en 4 variantes: es/en x dark/light.

Concepto: "Química × Código". A la derecha, un anillo de benceno (la química)
cuyas uniones se transforman en una red neuronal (la IA). Por las aristas
viajan pulsos de señal y los nodos laten. 

"""
import math
from xml.sax.saxutils import escape
from pathlib import Path

W, H = 1200, 300

THEMES = {
    "dark": dict(bg1="#05080f", bg2="#080c14", grid="#141d2b", text="#e6edf3",
                 muted="#7d8794", accent="#22d3ee", accent2="#a78bfa", edge="#13303c"),
    "light": dict(bg1="#dfe9f1", bg2="#edf2f6", grid="#c6d3de", text="#0b1220",
                  muted="#4b5563", accent="#0e7490", accent2="#6d28d9", edge="#a9c9d6"),
}

TEXTS = {
    "es": dict(prompt="> hola_mundo", role="Backend · Frontend · Inteligencia Artificial",
               studies="Ing. Química · UNT   ×   Ing. de Sistemas e IA · UPAO"),
    "en": dict(prompt="> hello_world", role="Backend · Frontend · Artificial Intelligence",
               studies="Chemical Eng. · UNT   ×   Systems Eng. & AI · UPAO"),
}

SANS = "'Segoe UI', 'Helvetica Neue', Helvetica, Arial, sans-serif"
MONO = "'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace"


def nodes():
    cx, cy, r = 735, 150, 50
    hexa = [(cx + r * math.cos(math.radians(a)), cy + r * math.sin(math.radians(a)))
            for a in range(-90, 270, 60)]
    layers = [
        [(880, y) for y in (75, 125, 175, 225)],
        [(1000, y) for y in (55, 102, 150, 198, 245)],
        [(1115, y) for y in (100, 150, 200)],
    ]
    return (cx, cy), hexa, layers


def build(theme: str, lang: str) -> str:
    c = THEMES[theme]
    t = {k: escape(v) for k, v in TEXTS[lang].items()}
    n_role = len(TEXTS[lang]["role"])  # longitud real, sin escapar
    (cx, cy), hexa, layers = nodes()
    out = []
    add = out.append

    edges = []
    for i in range(6):                                  
        edges.append((hexa[i], hexa[(i + 1) % 6], "bond"))
    for a in (hexa[1], hexa[2]):                          # enlaces molécula -> red
        for b in layers[0]:
            edges.append((a, b, "link"))
    for la, lb in zip(layers, layers[1:]):                # red totalmente conectada
        for a in la:
            for b in lb:
                edges.append((a, b, "net"))

    add(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
        f'viewBox="0 0 {W} {H}" role="img" aria-label="Andreé Vargas">')
    add(f"""<style>
  .bond {{ stroke:{c['accent']}; stroke-width:2.5; }}
  .edge {{ stroke:{c['edge']}; stroke-width:1.2; }}
  .flow {{ stroke:{c['accent']}; stroke-width:1.4; stroke-dasharray:4 14;
           opacity:.55; animation: flow 2.4s linear infinite; }}
  .atom {{ fill:{c['bg2']}; stroke:{c['accent']}; stroke-width:2.5; }}
  .neuron {{ fill:{c['bg2']}; stroke:{c['accent2']}; stroke-width:2; }}
  .core {{ fill:{c['accent']}; transform-box:fill-box; transform-origin:center;
           animation: beat 2.8s ease-in-out infinite; }}
  .core2 {{ fill:{c['accent2']}; transform-box:fill-box; transform-origin:center;
            animation: beat 2.8s ease-in-out infinite; }}
  .ring {{ animation: spin 12s linear infinite; transform-origin:{cx}px {cy}px; }}
  .fade {{ opacity:0; animation: fadein 1s ease-out forwards; }}
  .cursor {{ animation: blink 1s step-end infinite; }}
  @keyframes flow {{ to {{ stroke-dashoffset:-36; }} }}
  @keyframes beat {{ 0%,100% {{ transform:scale(.55); opacity:.55 }} 50% {{ transform:scale(1); opacity:1 }} }}
  @keyframes spin {{ to {{ transform:rotate(360deg); }} }}
  @keyframes fadein {{ to {{ opacity:1; }} }}
  @keyframes blink {{ 50% {{ opacity:0; }} }}
</style>""")

    add(f"""<defs>
  <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="{c['bg1']}"/><stop offset="1" stop-color="{c['bg2']}"/>
  </linearGradient>
  <radialGradient id="glow" cx="0.78" cy="0.5" r="0.45">
    <stop offset="0" stop-color="{c['accent']}" stop-opacity=".16"/>
    <stop offset="1" stop-color="{c['accent']}" stop-opacity="0"/>
  </radialGradient>
  <pattern id="dots" width="24" height="24" patternUnits="userSpaceOnUse">
    <circle cx="2" cy="2" r="1.1" fill="{c['grid']}"/>
  </pattern>
  <linearGradient id="name" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="{c['accent']}"/><stop offset="1" stop-color="{c['accent2']}"/>
  </linearGradient>
  <clipPath id="type"><rect x="70" y="170" height="40" width="0">
    <animate attributeName="width" from="0" to="{n_role * 13.3 + 10:.0f}"
             dur="2.6s" begin="0.8s" fill="freeze" calcMode="discrete"
             values="{';'.join(str(round(i * 13.3)) for i in range(n_role + 1))}"/>
  </rect></clipPath>
</defs>""")
    add(f'<rect width="{W}" height="{H}" rx="18" fill="url(#bg)"/>')
    add(f'<rect width="{W}" height="{H}" rx="18" fill="url(#dots)" opacity=".7"/>')
    add(f'<rect width="{W}" height="{H}" rx="18" fill="url(#glow)"/>')

    add('<g class="fade" style="animation-delay:1.1s">')
    for (a, b, kind) in edges:
        if kind == "bond":
            continue
        add(f'<line class="edge" x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}"/>')
    for i, (a, b, kind) in enumerate(edges):
        if kind == "net" and i % 2:
            continue
        if kind == "bond":
            continue
        add(f'<line class="flow" style="animation-delay:-{(i * 0.37) % 2.4:.2f}s" '
            f'x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}"/>')
    add('</g>')

    paths = [
        [hexa[1], layers[0][0], layers[1][1], layers[2][0]],
        [hexa[2], layers[0][3], layers[1][3], layers[2][2]],
        [hexa[1], layers[0][1], layers[1][2], layers[2][1]],
        [hexa[2], layers[0][2], layers[1][4], layers[2][2]],
        [hexa[1], layers[0][2], layers[1][0], layers[2][0]],
    ]
    for k, p in enumerate(paths):
        d = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in p)
        col = c['accent'] if k % 2 == 0 else c['accent2']
        add(f'<circle r="3.6" fill="{col}" opacity="0">'
            f'<animateMotion dur="3.2s" begin="{2.2 + k * 0.75:.2f}s" repeatCount="indefinite" path="{d}"/>'
            f'<animate attributeName="opacity" values="0;1;1;0" keyTimes="0;.1;.85;1" '
            f'dur="3.2s" begin="{2.2 + k * 0.75:.2f}s" repeatCount="indefinite"/></circle>')

    add('<g class="fade" style="animation-delay:.3s">')
    orbit = (f"M{cx - 72},{cy} a72,30 -20 1,0 144,0 a72,30 -20 1,0 -144,0")
    add(f'<path d="{orbit}" fill="none" stroke="{c["accent"]}" stroke-width="1" '
        f'stroke-dasharray="2 6" opacity=".45" transform="rotate(-20 {cx} {cy})"/>')
    add(f'<g transform="rotate(-20 {cx} {cy})"><circle r="4" fill="{c["accent"]}">'
        f'<animateMotion dur="4s" repeatCount="indefinite" path="{orbit}"/></circle></g>')
    pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in hexa)
    add(f'<polygon points="{pts}" fill="none" class="bond"/>')
    # solo el anillo interno gira; los átomos quedan fijos para no despegarse de las aristas
    add(f'<circle class="ring" cx="{cx}" cy="{cy}" r="27" fill="none" stroke="{c["accent"]}" '
        f'stroke-width="1.6" stroke-dasharray="5 6" opacity=".7"/>')
    for i, (x, y) in enumerate(hexa):
        add(f'<circle class="atom" cx="{x:.1f}" cy="{y:.1f}" r="9"/>')
        add(f'<circle class="core" style="animation-delay:-{i * 0.45:.2f}s" cx="{x:.1f}" cy="{y:.1f}" r="4.5"/>')
    add('</g>')

    for li, layer in enumerate(layers):
        add(f'<g class="fade" style="animation-delay:{1.3 + li * 0.35:.2f}s">')
        for ni, (x, y) in enumerate(layer):
            add(f'<circle class="neuron" cx="{x}" cy="{y}" r="11"/>')
            add(f'<circle class="core2" style="animation-delay:-{(li * 0.9 + ni * 0.4):.2f}s" '
                f'cx="{x}" cy="{y}" r="5.5"/>')
        add('</g>')

    add(f'<text x="{cx}" y="232" text-anchor="middle" font-family="{MONO}" font-size="12" '
        f'fill="{c["muted"]}">C₆H₆</text>')
    add(f'<text x="1000" y="285" text-anchor="middle" font-family="{MONO}" font-size="12" '
        f'fill="{c["muted"]}">f(x) = σ(Wx + b)</text>')

    add(f'<text class="fade" x="72" y="92" font-family="{MONO}" font-size="18" '
        f'fill="{c["accent"]}">{t["prompt"]}</text>')
    add(f'<text class="fade" style="animation-delay:.2s" x="68" y="152" font-family="{SANS}" '
        f'font-size="62" font-weight="700" fill="{c["text"]}" letter-spacing="-1">'
        f'Andreé <tspan fill="url(#name)">Vargas</tspan></text>')
    add(f'<g clip-path="url(#type)"><text x="72" y="196" font-family="{MONO}" font-size="22" '
        f'fill="{c["text"]}">{t["role"]}</text></g>')
    add(f'<rect class="cursor" x="72" y="178" width="11" height="24" fill="{c["accent"]}">'
        f'<animate attributeName="x" dur="2.6s" begin="0.8s" fill="freeze" calcMode="discrete" '
        f'values="{";".join(str(round(72 + i * 13.3)) for i in range(n_role + 1))}"/></rect>')
    add(f'<text class="fade" style="animation-delay:3.4s" x="72" y="240" font-family="{SANS}" '
        f'font-size="16" fill="{c["muted"]}">{t["studies"]}</text>')

    add('</svg>')
    return "\n".join(out)


if __name__ == "__main__":
    out_dir = Path(__file__).resolve().parent.parent / "assets"
    out_dir.mkdir(exist_ok=True)
    for lang in TEXTS:
        for theme in THEMES:
            (out_dir / f"header-{lang}-{theme}.svg").write_text(build(theme, lang), encoding="utf-8")
    print("ok")