"""Edición de README.md / README.en.md entre marcadores <!-- NOMBRE:INICIO --> ... <!-- NOMBRE:FIN -->."""
from collections.abc import Callable
from xml.sax.saxutils import escape

from .output import ROOT, write

READMES = (("README.md", "es"), ("README.en.md", "en"))


def replace_block(text: str, name: str, block: str,
                  insert: Callable[[str, str], str] | None = None) -> str:
    """Reemplaza lo que hay entre los marcadores. Si aún no existen, `insert(texto, bloque_marcado)`
    decide dónde ponerlos (por defecto, al final)."""
    start, end = f"<!-- {name}:INICIO -->", f"<!-- {name}:FIN -->"
    if start not in text:
        if insert:
            return insert(text, f"{start}\n{block}\n{end}")
        return text.rstrip() + f"\n\n{start}\n{block}\n{end}\n"
    head, rest = text.split(start, 1)
    _, tail = rest.split(end, 1)
    return f"{head}{start}\n{block}\n{end}{tail}"


def update(name: str, block_for: Callable[[str], str],
           insert: Callable[[str, str], str] | None = None) -> None:
    """Aplica `replace_block` a los dos README; `block_for(lang)` arma el bloque de cada idioma."""
    for readme, lang in READMES:
        path = ROOT / readme
        write(path, replace_block(path.read_text(encoding="utf-8"), name, block_for(lang), insert))


def picture(name: str, alt: str, width: str) -> str:
    """<picture> que elige la variante oscura o clara según el tema de quien visita."""
    return (f'<picture><source media="(prefers-color-scheme: dark)" srcset="assets/{name}-dark.svg">'
            f'<img src="assets/{name}-light.svg" alt="{escape(alt, {chr(34): "&quot;"})}" width="{width}"></picture>')
