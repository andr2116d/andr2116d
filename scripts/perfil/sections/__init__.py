"""Secciones del perfil, en el orden en que aparecen en el README.

Cada módulo expone NAME, DYNAMIC (si usa la API de GitHub) y run() -> str (un resumen para el log).
Se importan bajo demanda: así, generar solo las fijas no exige PyYAML ni token.
"""
import importlib

FIJAS = ("header", "about", "pills", "stack", "footer")
DINAMICAS = ("now", "projects", "stats")
MANUALES = ("iconos",)          # no corren con "todo": se usan a mano
GRUPOS = {"fijas": FIJAS, "dinamicas": DINAMICAS, "todo": FIJAS + DINAMICAS}


def load(name: str):
    return importlib.import_module(f"{__name__}.{name}")
