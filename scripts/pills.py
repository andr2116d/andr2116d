from pathlib import Path

from header import THEMES, SANS

PILLS = {"es": "ES · Español", "en": "EN · English"}
CONTACTS = {"linkedin": "LinkedIn", "instagram": "Instagram"}
W, H = 150, 36
OUT = Path(__file__).resolve().parent.parent / "assets"


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


def glyph(kind: str, c: dict) -> str:
    a = c["accent"]
    if kind == "linkedin":
        return (f'<rect x="14" y="9" width="18" height="18" rx="4" fill="none" stroke="{a}" stroke-width="1.8"/>'
                f'<text x="23" y="23" text-anchor="middle" font-family="{SANS}" font-size="11" '
                f'font-weight="700" fill="{a}">in</text>')
    return (f'<rect x="14" y="9" width="18" height="18" rx="5.5" fill="none" stroke="{a}" stroke-width="1.8"/>'
            f'<circle cx="23" cy="18" r="4.2" fill="none" stroke="{a}" stroke-width="1.8"/>'
            f'<circle cx="28.2" cy="13.4" r="1.2" fill="{a}"/>')


def contact(kind: str, theme: str) -> str:
    c = THEMES[theme]
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
            f'role="img" aria-label="{CONTACTS[kind]}">'
            f'<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="10" fill="{c["bg2"]}" '
            f'stroke="{c["edge"]}" stroke-width="1.5"/>{glyph(kind, c)}'
            f'<text x="42" y="{H / 2 + 5}" font-family="{SANS}" font-size="14" font-weight="600" '
            f'fill="{c["text"]}">{CONTACTS[kind]}</text></svg>')


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    for theme in THEMES:
        for lang, label in PILLS.items():
            for state, active in (("on", True), ("off", False)):
                (OUT / f"lang-{lang}-{state}-{theme}.svg").write_text(pill(label, theme, active), encoding="utf-8")
        for kind in CONTACTS:
            (OUT / f"contact-{kind}-{theme}.svg").write_text(contact(kind, theme), encoding="utf-8")
    print("ok")