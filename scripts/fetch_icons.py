"""Descarga los logos del stack y los guarda en scripts/icons.json.

Fuentes (versiones fijas, para que el resultado sea siempre el mismo):
  - Simple Icons 16.34.0 (licencia CC0): logos de un solo trazo + color de marca.
  - devicon (MIT): AWS y Playwright, que no están en Simple Icons.
  - labstack/echox (MIT): el ícono oficial de Echo.

"""
import json
import re
import urllib.request
from pathlib import Path

SIMPLE_ICONS = "https://raw.githubusercontent.com/simple-icons/simple-icons/16.34.0"
DEVICON = "https://raw.githubusercontent.com/devicons/devicon/7330accdbc47e2dc0c19789a48533c4a3c50fe58/icons"
ECHOX = "https://raw.githubusercontent.com/labstack/echox/a2a381d345df33a83a07eb4a3b38307b447f9e15"

SIMPLE = {
    "go": "Go", "python": "Python", "nodedotjs": "Node.js", "fastapi": "FastAPI",
    "typescript": "TypeScript", "javascript": "JavaScript", "react": "React", "nextdotjs": "Next.js",
    "tailwindcss": "Tailwind CSS", "astro": "Astro", "pytorch": "PyTorch", "scikitlearn": "scikit-learn",
    "pandas": "pandas", "postgresql": "PostgreSQL", "mongodb": "MongoDB", "redis": "Redis",
    "influxdb": "InfluxDB", "supabase": "Supabase", "docker": "Docker", "git": "Git", "linux": "Linux",
    "terraform": "Terraform", "cloudflare": "Cloudflare", "vercel": "Vercel", "railway": "Railway",
}

FULL = {
    "echo": ("Echo", f"{ECHOX}/site/public/favicon.svg", "labstack/echox (MIT)"),
    "playwright": ("Playwright", f"{DEVICON}/playwright/playwright-original.svg", "devicon (MIT)"),
    "aws": ("AWS", f"{DEVICON}/amazonwebservices/amazonwebservices-original-wordmark.svg", "devicon (MIT)"),
}


def get(url: str) -> str:
    with urllib.request.urlopen(url, timeout=30) as r:
        return r.read().decode("utf-8")


def main() -> None:
    brand = {x["title"]: x["hex"] for x in json.loads(get(f"{SIMPLE_ICONS}/data/simple-icons.json"))}
    icons = {}
    for slug, title in SIMPLE.items():
        svg = get(f"{SIMPLE_ICONS}/icons/{slug}.svg")
        path = re.search(r'<path d="([^"]+)"', svg).group(1)
        icons[slug] = dict(title=title, hex=brand[title], path=path)
        print("✓", title)
    for slug, (title, url, source) in FULL.items():
        svg = get(url)
        view_box = re.search(r'viewBox="([^"]+)"', svg).group(1)
        inner = re.sub(r"^.*?<svg[^>]*>", "", svg, flags=re.S)
        inner = re.sub(r"</svg>\s*$", "", inner.strip()).strip()
        icons[slug] = dict(title=title, viewBox=view_box, svg=re.sub(r"\s+", " ", inner), source=source)
        print("✓", title)
    out = Path(__file__).resolve().parent / "icons.json"
    out.write_text(json.dumps(icons, ensure_ascii=False), encoding="utf-8")
    print(f"{len(icons)} logos guardados en {out.name}")


if __name__ == "__main__":
    main()