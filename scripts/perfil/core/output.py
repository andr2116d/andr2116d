"""Dónde y cómo se escriben los archivos generados."""
from collections.abc import Iterator
from pathlib import Path

from .theme import LANGS, THEMES

ROOT = Path(__file__).resolve().parents[3]   # scripts/perfil/core/output.py -> raíz del repo
ASSETS = ROOT / "assets"


def variants() -> Iterator[tuple[str, str]]:
    """Todas las combinaciones idioma × tema."""
    for lang in LANGS:
        for theme in THEMES:
            yield lang, theme


def write(path: Path, text: str) -> bool:
    """Escribe solo si el contenido cambió (no toca archivos idénticos). Devuelve True si escribió."""
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        if path.read_text(encoding="utf-8") == text:
            return False
    except FileNotFoundError:
        pass
    path.write_text(text, encoding="utf-8")
    return True


def prune(folder: Path, keep: set[str], pattern: str = "*.svg") -> None:
    """Borra los archivos generados que ya no corresponden a nada (p. ej. un proyecto que salió)."""
    for old in folder.glob(pattern):
        if old.name not in keep:
            old.unlink()
