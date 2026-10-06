from pathlib import Path

from header import THEMES, SANS

PILLS = {"es": "ES · Español", "en": "EN · English"}
W, H = 150, 36


def pill(label: str, theme: str, active: bool) -> str:
    c = THEMES[theme]
    if active:
        body = (f'<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="{H // 2}" fill="url(#g)"/>'
                f'<circle cx="20" cy="{H / 2}" r="4" fill="{c["bg1"]}"/>')
        fg, weight = c["bg1"], 700
    else:
        body = (f'<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="{H // 2}" fill="none" '
                f'stroke="{c["muted"]}" stroke-opacity=".6" stroke-width="1.5"/>'
                f'<circle cx="20" cy="{H / 2}" r="4" fill="none" stroke="{c["muted"]}" stroke-width="1.5"/>')
        fg, weight = c["muted"], 600
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
            f'role="img" aria-label="{label}">'
            f'<defs><linearGradient id="g" x1="0" x2="1"><stop offset="0" stop-color="{c["accent"]}"/>'
            f'<stop offset="1" stop-color="{c["accent2"]}"/></linearGradient></defs>{body}'
            f'<text x="34" y="{H / 2 + 5}" font-family="{SANS}" font-size="14" font-weight="{weight}" '
            f'fill="{fg}">{label}</text></svg>')


if __name__ == "__main__":
    out = Path(__file__).resolve().parent.parent / "assets"
    out.mkdir(exist_ok=True)
    for lang, label in PILLS.items():
        for theme in THEMES:
            for state, active in (("on", True), ("off", False)):
                (out / f"lang-{lang}-{state}-{theme}.svg").write_text(pill(label, theme, active), encoding="utf-8")
    print("ok")