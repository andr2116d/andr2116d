"""python -m perfil [grupo|sección ...]  ·  ver perfil/__init__.py"""
import sys
import time

from .sections import DINAMICAS, FIJAS, GRUPOS, MANUALES, load


def main(argv: list[str]) -> int:
    if "--lista" in argv or "-h" in argv or "--help" in argv:
        print("grupos:    " + ", ".join(GRUPOS))
        print("fijas:     " + ", ".join(FIJAS))
        print("dinámicas: " + ", ".join(DINAMICAS) + "   (usan la API; stats exige GITHUB_TOKEN)")
        print("manuales:  " + ", ".join(MANUALES))
        return 0
    names: list[str] = []
    for arg in argv or ["todo"]:
        for name in GRUPOS.get(arg, (arg,)):
            if name not in FIJAS + DINAMICAS + MANUALES:
                print(f"sección desconocida: {name}  (python -m perfil --lista)", file=sys.stderr)
                return 2
            if name not in names:
                names.append(name)
    for name in names:
        t0 = time.perf_counter()
        msg = load(name).run()
        print(f"{name:<9} {msg}  ({time.perf_counter() - t0:.1f} s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
