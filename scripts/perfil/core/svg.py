"""Ayudas para armar SVG a mano."""
from .theme import THEMES, SANS, MONO


def wrap(text: str, width: int, max_lines: int | None = None) -> list[str]:
    """Parte un texto en líneas de como máximo `width` caracteres (SVG no hace saltos solo).
    Con `max_lines`, corta ahí y termina la última línea con '…'."""
    lines, cur = [], ""
    for word in text.split():
        if len(cur) + len(word) + 1 > width and cur:
            lines.append(cur)
            cur = word
        else:
            cur = f"{cur} {word}".strip()
    lines.append(cur)
    if max_lines and len(lines) > max_lines:
        lines = lines[:max_lines]
        lines[-1] = lines[-1].rstrip(".,;: ") + "…"
    return lines


def title_svg(tag: str, title: str, theme: str) -> str:
    """Título de sección: etiqueta tipo comentario, título y una barra con el degradado de acento."""
    c = THEMES[theme]
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="96" viewBox="0 0 1200 96" '
            f'role="img" aria-label="{title}"><defs><linearGradient id="l" x1="0" x2="1">'
            f'<stop offset="0" stop-color="{c["accent"]}"/><stop offset="1" stop-color="{c["accent2"]}"/>'
            f'</linearGradient></defs>'
            f'<text x="4" y="26" font-family="{MONO}" font-size="18" fill="{c["accent"]}">{tag}</text>'
            f'<text x="4" y="70" font-family="{SANS}" font-size="40" font-weight="700" fill="{c["text"]}">'
            f'{title}</text><rect x="4" y="84" width="64" height="4" rx="2" fill="url(#l)"/></svg>')
