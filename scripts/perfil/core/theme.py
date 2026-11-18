"""Paleta, tipografías y colores de lenguajes, iguales en todo el perfil."""

LANGS = ("es", "en")

THEMES = {
    "dark": dict(bg1="#05080f", bg2="#080c14", grid="#141d2b", text="#e6edf3",
                 muted="#7d8794", accent="#22d3ee", accent2="#a78bfa", edge="#13303c"),
    "light": dict(bg1="#dfe9f1", bg2="#edf2f6", grid="#c6d3de", text="#0b1220",
                  muted="#4b5563", accent="#0e7490", accent2="#6d28d9", edge="#a9c9d6"),
}

SANS = "'Segoe UI', 'Helvetica Neue', Helvetica, Arial, sans-serif"
MONO = "'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace"

# colores de GitHub (linguist) para las barras de lenguajes
LANG_COLORS = {
    "Python": "#3572A5", "TypeScript": "#3178c6", "JavaScript": "#f1e05a", "Go": "#00ADD8",
    "HTML": "#e34c26", "CSS": "#663399", "HCL": "#844FBA", "Dockerfile": "#384d54",
    "Shell": "#89e051", "Jupyter Notebook": "#DA5B0B", "Astro": "#ff5a03", "Java": "#b07219",
    "C++": "#f34b7d", "C": "#555555", "Rust": "#dea584", "PHP": "#4F5D95", "Vue": "#41b883",
    "Kotlin": "#A97BFF", "Dart": "#00B4AB", "SQL": "#e38c00", "MATLAB": "#e16737",
}
