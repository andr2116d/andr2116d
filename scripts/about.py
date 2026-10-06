"""
Diseño: título + presentación arriba, tres pilares (Construyo, Aprendo,
Mejoro) con íconos dibujados a mano, una franja con el dato curioso y una
línea de cierre. Sin emojis: misma paleta y tipografía que la cabecera.
"""
from pathlib import Path
from xml.sax.saxutils import escape

from header import THEMES, SANS, MONO

W = 1200

TEXTS = {
    "es": dict(
        title="Sobre mí",
        tag="// perfil",
        intro=("Desarrollador backend y frontend autodidacta, de Trujillo, Perú. Estudio "
               "Ingeniería Química en la UNT e Ingeniería de Sistemas e IA en la UPAO: de la "
               "primera traigo el pensamiento en procesos; de la segunda, las herramientas "
               "para automatizarlos."),
        pillars=[
            ("Construyo", "APIs, backends y aplicaciones web completas, desde la base de datos "
                          "hasta la interfaz, pensadas para usarse de verdad."),
            ("Aprendo", "Tecnologías nuevas de forma constante. Hoy mi foco es la IA: aprendizaje "
                        "por refuerzo y redes neuronales de grafos."),
            ("Mejoro", "Buenas prácticas, código limpio, pruebas y arquitectura. Cada proyecto "
                       "suma experiencia y sale mejor que el anterior."),
        ],
        fact=("Dato curioso", "paso de balances de materia a balanceadores de carga sin cambiar de cuaderno."),
        foot="Abierto a colaborar en backend, frontend, IA y software para la industria química",
    ),
    "en": dict(
        title="About me",
        tag="// profile",
        intro=("Self-taught backend and frontend developer from Trujillo, Peru. I study "
               "Chemical Engineering at UNT and Systems Engineering & AI at UPAO: from the "
               "first I bring process thinking; from the second, the tools to automate it."),
        pillars=[
            ("I build", "APIs, backends and full web applications, from the database to the "
                        "interface, designed to be actually used."),
            ("I learn", "New technologies all the time. Right now my focus is AI: reinforcement "
                        "learning and graph neural networks."),
            ("I improve", "Good practices, clean code, testing and architecture. Every project "
                          "adds experience and turns out better than the last."),
        ],
        fact=("Fun fact", "I switch from mass balances to load balancers without changing notebooks."),
        foot="Open to collaborating on backend, frontend, AI and software for the chemical industry",
    ),
}


def wrap(text: str, width: int) -> list[str]:
    """Parte un texto en líneas de como máximo `width` caracteres (SVG no hace saltos solo)."""
    lines, cur = [], ""
    for word in text.split():
        if len(cur) + len(word) + 1 > width and cur:
            lines.append(cur)
            cur = word
        else:
            cur = f"{cur} {word}".strip()
    return lines + [cur]


def icon(kind: int, x: float, y: float, c: dict) -> str:
    a, b = c["accent"], c["accent2"]
    if kind == 0:  # capas apiladas (stack completo)
        return (f'<g transform="translate({x},{y})" fill="none" stroke-width="2.2" stroke-linejoin="round">'
                f'<path d="M20 4 L36 12 L20 20 L4 12 Z" stroke="{a}"/>'
                f'<path class="lift" d="M4 20 L20 28 L36 20" stroke="{b}"/>'
                f'<path d="M4 28 L20 36 L36 28" stroke="{a}" opacity=".6"/></g>')
    if kind == 1:  
        return (f'<g transform="translate({x},{y})" stroke-width="2">'
                f'<path d="M8 30 L20 10 L32 26 L8 30 M20 10 L20 24" stroke="{a}" fill="none"/>'
                f'<circle cx="20" cy="10" r="4.5" fill="{c["bg2"]}" stroke="{b}"/>'
                f'<circle cx="8" cy="30" r="4.5" fill="{c["bg2"]}" stroke="{a}"/>'
                f'<circle cx="32" cy="26" r="4.5" fill="{c["bg2"]}" stroke="{a}"/>'
                f'<circle class="pop" cx="20" cy="24" r="3.5" fill="{b}"/></g>')
    return (f'<g transform="translate({x},{y})" fill="none" stroke-width="2.2" stroke-linecap="round">'
            f'<path d="M4 36 L36 36 M4 36 L4 4" stroke="{c["muted"]}" opacity=".6"/>'
            f'<path class="draw" d="M6 32 L14 26 L21 28 L30 14 L36 8" stroke="{b}"/>'
            f'<path d="M30 8 L36 8 L36 14" stroke="{b}"/></g>')


def build(theme: str, lang: str) -> str:
    c, t = THEMES[theme], TEXTS[lang]
    lines = wrap(t["intro"], 80)
    top = 160 + len(lines) * 34 + 18
    H = top + 215 + 24 + 58 + 52  
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
           f'role="img" aria-label="{escape(t["title"])}: {escape(t["intro"])}">']
    add = out.append
    add(f"""<style>
  /* el estado oculto vive solo dentro de la animación ("both"): si un visor no
     ejecuta animaciones, el contenido se ve igual */
  .fade {{ animation: fadein .9s ease-out both; }}
  .lift {{ animation: lift 3s ease-in-out infinite; }}
  .pop {{ transform-box:fill-box; transform-origin:center; animation: pop 2.4s ease-in-out infinite; }}
  .draw {{ stroke-dasharray:60; animation: draw 2.2s ease-out .8s both; }}
  @keyframes fadein {{ from {{ opacity:0; }} to {{ opacity:1; }} }}
  @keyframes lift {{ 0%,100% {{ transform:translateY(0) }} 50% {{ transform:translateY(-3px) }} }}
  @keyframes pop {{ 0%,100% {{ transform:scale(.6) }} 50% {{ transform:scale(1.15) }} }}
  @keyframes draw {{ from {{ stroke-dashoffset:60; }} to {{ stroke-dashoffset:0; }} }}
</style>
<defs>
  <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="{c['bg1']}"/><stop offset="1" stop-color="{c['bg2']}"/>
  </linearGradient>
  <linearGradient id="line" x1="0" x2="1">
    <stop offset="0" stop-color="{c['accent']}"/><stop offset="1" stop-color="{c['accent2']}"/>
  </linearGradient>
  <pattern id="dots" width="24" height="24" patternUnits="userSpaceOnUse">
    <circle cx="2" cy="2" r="1.1" fill="{c['grid']}"/>
  </pattern>
</defs>""")
    add(f'<rect width="{W}" height="{H}" rx="18" fill="url(#bg)"/>')
    add(f'<rect width="{W}" height="{H}" rx="18" fill="url(#dots)" opacity=".5"/>')

    # título
    add(f'<text class="fade" x="60" y="60" font-family="{MONO}" font-size="18" fill="{c["accent"]}">'
        f'{escape(t["tag"])}</text>')
    add(f'<text class="fade" x="60" y="100" font-family="{SANS}" font-size="40" font-weight="700" '
        f'fill="{c["text"]}">{escape(t["title"])}</text>')
    add(f'<rect class="fade" x="60" y="114" width="64" height="4" rx="2" fill="url(#line)"/>')

    # presentación
    add(f'<text class="fade" style="animation-delay:.2s" font-family="{SANS}" font-size="23" fill="{c["text"]}">')
    for i, ln in enumerate(lines):
        add(f'<tspan x="60" y="{160 + i * 34}">{escape(ln)}</tspan>')
    add('</text>')

    # pilares
    cw, gap = 340, 30
    for k, (name, desc) in enumerate(t["pillars"]):
        x = 60 + k * (cw + gap)
        d = .5 + k * .25
        add(f'<g class="fade" style="animation-delay:{d:.2f}s">')
        add(f'<rect x="{x}" y="{top}" width="{cw}" height="215" rx="14" fill="{c["bg2"]}" '
            f'stroke="{c["edge"]}" stroke-width="1.2"/>')
        add(f'<rect x="{x}" y="{top}" width="4" height="215" rx="2" fill="url(#line)"/>')
        add(f'<g transform="translate({x + 22},{top + 18}) scale(1.2) translate({-x - 22},{-top - 18})">'
            + icon(k, x + 22, top + 18, c) + '</g>')
        add(f'<text x="{x + 84}" y="{top + 49}" font-family="{SANS}" font-size="25" font-weight="700" '
            f'fill="{c["text"]}">{escape(name)}</text>')
        add(f'<text font-family="{SANS}" font-size="19.5" fill="{c["text"]}" fill-opacity=".75">')
        for i, ln in enumerate(wrap(desc, 31)):
            add(f'<tspan x="{x + 22}" y="{top + 96 + i * 28}">{escape(ln)}</tspan>')
        add('</text></g>')


    fy = top + 215 + 24
    label, fact = t["fact"]
    add(f'<g class="fade" style="animation-delay:1.2s">'
        f'<rect x="60" y="{fy}" width="{W - 120}" height="58" rx="14" fill="{c["accent2"]}" fill-opacity=".08" '
        f'stroke="{c["accent2"]}" stroke-opacity=".35"/>'
        f'<g transform="translate(80,{fy + 10})" fill="none" stroke="{c["accent2"]}" stroke-width="2" '
        f'stroke-linejoin="round" stroke-linecap="round">'
        f'<path d="M12 2 H24 M14 2 V14 L4 34 a2 2 0 0 0 2 3 H30 a2 2 0 0 0 2 -3 L22 14 V2"/>'
        f'<path d="M8 27 H28" stroke-opacity=".6"/></g>'
        + "".join(f'<circle cx="{98 + dx}" cy="{fy + 42}" r="{r}" fill="{c["accent2"]}">'
                  f'<animate attributeName="cy" values="{fy + 42};{fy + 14}" dur="{d}s" begin="{b}s" repeatCount="indefinite"/>'
                  f'<animate attributeName="opacity" values="0;1;0" dur="{d}s" begin="{b}s" repeatCount="indefinite"/></circle>'
                  for dx, r, d, b in ((-5, 2, 2.2, 0), (3, 1.6, 1.8, .7), (-1, 1.3, 2.6, 1.3)))
        + f'<text x="132" y="{fy + 36}" font-family="{SANS}" font-size="19" fill="{c["text"]}" fill-opacity=".85">'
        f'<tspan font-weight="700" fill="{c["accent2"]}" fill-opacity="1">{escape(label)}:</tspan> {escape(fact)}</text></g>')

    add(f'<text class="fade" style="animation-delay:1.4s" x="{W / 2}" y="{H - 16}" text-anchor="middle" '
        f'font-family="{MONO}" font-size="16" fill="{c["muted"]}">{escape(t["foot"])}</text>')
    add('</svg>')
    return "\n".join(out)


if __name__ == "__main__":
    out = Path(__file__).resolve().parent.parent / "assets"
    for lang in TEXTS:
        for theme in THEMES:
            (out / f"about-{lang}-{theme}.svg").write_text(build(theme, lang), encoding="utf-8")
    print("ok")