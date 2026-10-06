import urllib.error
from datetime import datetime, timezone
from pathlib import Path
from xml.sax.saxutils import escape

from header import THEMES, SANS, MONO
from github_api import USER, all_repos, api
from projects import TOPICS

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "now"
W, H = 1200, 92
ONLY_PORTFOLIO = False   # True = solo mostrar actividad de repos con topic portfolio/featured

UI = {
    "es": dict(label="Trabajando en", last="último commit", idle="Construyendo algo nuevo…"),
    "en": dict(label="Working on", last="last commit", idle="Building something new…"),
}


def ago(when: datetime, lang: str) -> str:
    days = (datetime.now(timezone.utc).date() - when.date()).days
    es = lang == "es"
    if days <= 0:
        return "hoy" if es else "today"
    if days == 1:
        return "ayer" if es else "yesterday"
    if days < 14:
        return f"hace {days} días" if es else f"{days} days ago"
    if days < 60:
        return f"hace {days // 7} semanas" if es else f"{days // 7} weeks ago"
    return f"hace {days // 30} meses" if es else f"{days // 30} months ago"


def from_github() -> dict | None:
    repos = [r for r in all_repos()
             if r["name"].lower() != USER.lower() and not r["fork"]
             and (not ONLY_PORTFOLIO or TOPICS & set(r.get("topics", [])))]
    for r in sorted(repos, key=lambda r: r["pushed_at"], reverse=True):
        try:
            commits = api(f"/repos/{USER}/{r['name']}/commits?per_page=1")
        except urllib.error.HTTPError:
            continue
        if commits:
            c = commits[0]["commit"]
            return dict(repo=r["name"], url=r["html_url"], message=c["message"], date=c["committer"]["date"])
    return None


def build(info: dict | None, lang: str, theme: str) -> str:
    c, u = THEMES[theme], UI[lang]
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" '
         f'aria-label="{u["label"]}: {escape(info["repo"]) if info else u["idle"]}">',
         f"""<style>
  .ping {{ transform-box:fill-box; transform-origin:center; animation: ping 2s ease-out infinite; }}
  @keyframes ping {{ 0% {{ transform:scale(1); opacity:.7 }} 100% {{ transform:scale(2.6); opacity:0 }} }}
</style>
<defs><linearGradient id="bg" x1="0" x2="1">
  <stop offset="0" stop-color="{c['bg1']}"/><stop offset="1" stop-color="{c['bg2']}"/></linearGradient>
  <linearGradient id="line" x1="0" x2="1">
  <stop offset="0" stop-color="{c['accent']}"/><stop offset="1" stop-color="{c['accent2']}"/></linearGradient></defs>""",
         f'<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="14" fill="url(#bg)" stroke="{c["edge"]}" stroke-width="1.5"/>',
         f'<rect x="1" y="{H - 4}" width="{W - 2}" height="3" rx="1.5" fill="url(#line)" opacity=".8"/>',
         '<circle class="ping" cx="34" cy="32" r="6" fill="#3fb950"/>'
         '<circle cx="34" cy="32" r="6" fill="#3fb950"/>']
    add = o.append
    if not info:
        add(f'<text x="54" y="{H / 2 + 5}" font-family="{SANS}" font-size="18" fill="{c["text"]}">{u["idle"]}</text>')
    else:
        msg = info["message"].strip().splitlines()[0]
        when = ago(datetime.fromisoformat(info["date"].replace("Z", "+00:00")), lang)
        head = u["label"]
        x_repo = 54 + len(head) * 10.2 + 16
        add(f'<text x="54" y="38" font-family="{SANS}" font-size="18" fill="{c["muted"]}">{escape(head)}</text>'
            f'<text x="{x_repo:.0f}" y="38" font-family="{SANS}" font-size="20" font-weight="700" '
            f'fill="{c["accent"]}">{escape(info["repo"])}</text>'
            f'<text x="{W - 32}" y="38" text-anchor="end" font-family="{SANS}" font-size="16" '
            f'fill="{c["muted"]}">{escape(u["last"])} · {escape(when)}</text>')
        room = int((W - 54 - 32) / 9.6) - 13   # 13 = largo del prefijo "$ git log -1 "
        if len(msg) > room:
            msg = msg[:room - 1].rstrip() + "…"
        add(f'<text x="54" y="68" font-family="{MONO}" font-size="16" fill="{c["text"]}" fill-opacity=".85">'
            f'<tspan fill="{c["accent2"]}">$ git log -1 </tspan>{escape(msg)}</text>')
    add('</svg>')
    return "\n".join(o)


def replace_block(text: str, block: str) -> str:
    start, end = "<!-- AHORA:INICIO -->", "<!-- AHORA:FIN -->"
    if start not in text:
        cut = text.index("</a>", text.index("assets/header-")) + len("</a>")
        return f"{text[:cut]}\n\n{start}\n{block}\n{end}{text[cut:]}"
    head, rest = text.split(start, 1)
    _, tail = rest.split(end, 1)
    return f"{head}{start}\n{block}\n{end}{tail}"


def render(info: dict | None) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for lang in UI:
        for theme in THEMES:
            (OUT / f"now-{lang}-{theme}.svg").write_text(build(info, lang, theme), encoding="utf-8")
    link = info["url"] if info else f"https://github.com/{USER}?tab=repositories"
    for readme, lang in (("README.md", "es"), ("README.en.md", "en")):
        path = ROOT / readme
        alt = f'{UI[lang]["label"]}: {escape(info["repo"])}' if info else UI[lang]["idle"]
        block = (f'<a href="{link}"><picture><source media="(prefers-color-scheme: dark)" '
                 f'srcset="assets/now/now-{lang}-dark.svg"><img src="assets/now/now-{lang}-light.svg" '
                 f'alt="{alt}" width="100%"></picture></a>')
        path.write_text(replace_block(path.read_text(encoding="utf-8"), block), encoding="utf-8")


def main() -> None:
    info = from_github()
    render(info)
    print("trabajando en:", info["repo"] if info else "(sin actividad pública)")


if __name__ == "__main__":
    main()