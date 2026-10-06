"""Cliente mínimo de la API de GitHub, compartido por todos los scripts.

- El usuario se detecta solo (PROFILE_USER, GITHUB_REPOSITORY_OWNER o dueño del remoto 'origin').
- Si existe la variable GITHUB_TOKEN (en GitHub Actions existe sola), la usa:
  el límite sube de 60 a 1000+ consultas por hora.
- Reintenta ante errores temporales (502, cortes de red) con espera creciente.
"""
import json
import os
import re
import subprocess
import time
import urllib.error
import urllib.request


def _detect_user() -> str:
    if user := os.environ.get("PROFILE_USER") or os.environ.get("GITHUB_REPOSITORY_OWNER"):
        return user
    try:
        url = subprocess.run(["git", "config", "--get", "remote.origin.url"],
                             capture_output=True, text=True, check=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        url = ""
    if m := re.search(r"github\.com[:/]([^/]+)/", url):
        return m.group(1)
    raise SystemExit("No pude detectar tu usuario: define PROFILE_USER o corre dentro del repo clonado.")


USER = _detect_user()


def fetch(url: str, *, auth: bool = True, tries: int = 3) -> bytes:
    req = urllib.request.Request(url, headers={"Accept": "application/vnd.github+json",
                                               "User-Agent": f"{USER}-profile"})
    if auth and (token := os.environ.get("GITHUB_TOKEN")):
        req.add_header("Authorization", f"Bearer {token}")
    for attempt in range(tries):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            if e.code == 404 or attempt == tries - 1:
                raise
        except urllib.error.URLError:
            if attempt == tries - 1:
                raise
        time.sleep(2 ** attempt)
    raise RuntimeError("inalcanzable")


def api(path: str):
    return json.loads(fetch(f"https://api.github.com{path}"))


def all_repos() -> list[dict]:
    repos, page = [], 1
    while True:
        batch = api(f"/users/{USER}/repos?per_page=100&type=owner&page={page}")
        repos += batch
        if len(batch) < 100:
            return repos
        page += 1