#!/usr/bin/env python3
"""Generador estático de Mil días.

Fuente única de contenido: content/days.json (días 1-4 transcritos del
sitio original; días 5-1000, placeholder).
Uso:  python3 scripts/generate.py
Salida: index.html, dias/index.html, acerca/index.html, dia/<n>/index.html,
        sitemap.xml, feed.xml, robots.txt, 404.html, vercel.json
Cambiar SITE_URL por la URL real de despliegue antes de publicar.
"""
import html
import json
import math
import re
import urllib.parse
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE_URL = "https://mil-dias-five.vercel.app"
# Si se despliega en un dominio propio, cambiar SITE_URL arriba y listo.
START = date(2026, 11, 3)

DATA = json.loads((ROOT / "content" / "days.json").read_text(encoding="utf-8"))
SITE = DATA["site"]
MANIFESTO = DATA["manifesto"]
DAYS = DATA["days"]


def roman(n: int) -> str:
    table = [(1000, "M"), (900, "CM"), (500, "D"), (400, "CD"),
             (100, "C"), (90, "XC"), (50, "L"), (40, "XL"),
             (10, "X"), (9, "IX"), (5, "V"), (4, "IV"), (1, "I")]
    out = ""
    for value, numeral in table:
        while n >= value:
            out += numeral
            n -= value
    return out


def esc(s: str) -> str:
    return html.escape(s, quote=True)


def day_date(n: int) -> date:
    entry = DAYS.get(str(n), {})
    if entry.get("date"):
        return date.fromisoformat(entry["date"])
    return START + timedelta(days=n - 1)


def is_published(n: int) -> bool:
    return bool(DAYS.get(str(n), {}).get("published"))


def blocks(n: int):
    if is_published(n):
        return DAYS[str(n)]["blocks"]
    text = DATA["placeholders"]["1000"] if n == 1000 else DATA["placeholders"]["5_to_999"]
    return [{"type": "p", "text": text}]


def first_paragraph(n: int) -> str:
    for b in blocks(n):
        if b["type"] == "p":
            return b["text"]
    return ""


def thematic_title(n: int) -> str:
    """Primera frase temática: primer subtítulo si lo hay, si no, primer párrafo."""
    for b in blocks(n):
        if b["type"] == "h2":
            return b["text"]
    return first_paragraph(n)


def reading_minutes(n: int) -> int:
    words = sum(len(b["text"].split()) for b in blocks(n) if b["type"] == "p")
    return max(1, math.ceil(words / 200))


MONTHS_ES = ["enero", "febrero", "marzo", "abril", "mayo", "junio",
              "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]


def fmt_date_es(d: date) -> str:
    return f"{d.day} de {MONTHS_ES[d.month - 1]} de {d.year}"


SHARE_JS = """<script>
function copyLink(btn){const u=btn.dataset.url;if(navigator.clipboard&&navigator.clipboard.writeText){navigator.clipboard.writeText(u).then(()=>{btn.textContent='Enlace copiado ✓';setTimeout(()=>btn.textContent='Copiar enlace',2500);}).catch(()=>{fallbackCopy(u,btn);});}else{fallbackCopy(u,btn);}}
function fallbackCopy(u,btn){const t=document.createElement('textarea');t.value=u;document.body.appendChild(t);t.select();try{document.execCommand('copy');btn.textContent='Enlace copiado ✓';}catch(e){btn.textContent=u;}document.body.removeChild(t);setTimeout(()=>btn.textContent='Copiar enlace',2500);}
</script>"""


def head(*, title, description, url, prefix, og_type="website"):
    return f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(description)}">
<meta name="author" content="{esc(SITE['author'])}">
<link rel="canonical" href="{esc(url)}">
<meta property="og:type" content="{og_type}">
<meta property="og:site_name" content="Mil días">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(description)}">
<meta property="og:url" content="{esc(url)}">
<meta property="og:image" content="{SITE_URL}/assets/og-mil-dias.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="Mil días — Un archivo de recuerdos">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{esc(title)}">
<meta name="twitter:description" content="{esc(description)}">
<meta name="twitter:image" content="{SITE_URL}/assets/og-mil-dias.png">
<meta name="theme-color" content="#0a0a09">
<link rel="icon" type="image/svg+xml" href="{prefix}assets/favicon.svg">
<link rel="alternate" type="application/rss+xml" title="Mil días" href="{SITE_URL}/feed.xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,500;0,600;1,400&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{prefix}assets/styles.css?v=2">
</head>
"""


def header(prefix, current=""):
    def cur(name):
        return ' aria-current="page"' if current == name else ""
    return f"""<body>
<header class="top">
<a class="logo" href="{prefix}index.html" aria-label="Inicio — Mil días"><img src="{prefix}assets/hourglass.svg?v=2" alt="" width="24" height="24"><span>Mil días</span></a>
<nav class="nav-links" aria-label="Navegación principal">
<a class="nav-link" href="{prefix}acerca/"{cur("acerca")}>Qué es esto</a>
<a class="nav-link" href="{prefix}dias/"{cur("archivo")}>Archivo</a>
</nav>
</header>
"""


def footer(prefix, progress=None):
    return f"""<footer class="site">
<p class="foot-title">Mil días</p>
<p class="foot-links"><a href="{prefix}acerca/">Qué es esto</a> · <a href="{prefix}dias/">Archivo</a> · <a href="{SITE_URL}/feed.xml">RSS</a></p>
</footer>
{SHARE_JS}
</body>
</html>
"""


def share_block(url, title):
    q_url = urllib.parse.quote(url, safe="")
    q_text = urllib.parse.quote(f"{title} — Mil días", safe="")
    return f"""<div class="share">
<p>Compartir este día</p>
<div class="share-buttons">
<button type="button" data-url="{esc(url)}" onclick="copyLink(this)">Copiar enlace</button>
<a href="https://wa.me/?text={q_text}%20{q_url}" target="_blank" rel="noopener">WhatsApp</a>
<a href="https://twitter.com/intent/tweet?text={q_text}&amp;url={q_url}" target="_blank" rel="noopener">X</a>
<a href="https://www.linkedin.com/sharing/share-offsite/?url={q_url}" target="_blank" rel="noopener">LinkedIn</a>
</div>
<p class="share-note"></p>
</div>"""


def day_nav(n, prefix):
    if n > 1:
        prev_link = (f'<a class="day-nav-btn prev" href="{prefix}dia/{n-1}/"'
                     f' aria-label="Ir al día {roman(n-1)}">‹ Día anterior'
                     f'<small>Día {roman(n-1)}</small></a>')
    else:
        prev_link = ('<span class="day-nav-btn prev disabled" aria-disabled="true">'
                     '‹ Día anterior<small>Es el primer día</small></span>')
    if n < 1000:
        next_link = (f'<a class="day-nav-btn next" href="{prefix}dia/{n+1}/"'
                     f' aria-label="Ir al día {roman(n+1)}">Día siguiente ›'
                     f'<small>Día {roman(n+1)}</small></a>')
    else:
        next_link = ('<span class="day-nav-btn next disabled" aria-disabled="true">'
                     'Día siguiente ›<small>Es el último día</small></span>')
    return (f'<nav class="day-nav" aria-label="Navegación entre días">{prev_link}'
            f'<a class="day-nav-btn today-btn" href="{prefix}index.html">Hoy'
            f'<small>Portada</small></a>{next_link}</nav>')


def render_day(n):
    rn = roman(n)
    prefix = "../../"
    url = f"{SITE_URL}/dia/{n}/"
    published = is_published(n)
    d = day_date(n)
    theme = thematic_title(n) if published else ""
    title = f"{theme} — Día {rn} — Mil días" if published else f"Día {rn} — Mil días"
    desc = first_paragraph(n) if published else "Este día aún no llegó."
    if n == 1000 and not published:
        desc = "Todavía no."
    body = []
    for b in blocks(n):
        if b.get("separator"):
            body.append('<hr class="gold-rule">')
        text = esc(b["text"])
        if b.get("italic"):
            text = f"<em>{text}</em>"
        tag = "h2" if b["type"] == "h2" else "p"
        body.append(f"<{tag}>{text}</{tag}>")
    entry_class = "entry" if published else "entry placeholder"
    meta = (f'<p class="meta"><span>{fmt_date_es(d)}</span></p>' if published
            else f'<p class="meta"><span>{fmt_date_es(d)}</span></p>')
    share = share_block(url, title) if published else ""
    article = f"""<main>
<p class="day-kicker">Día {rn}</p>
<h1 class="day-title">Día {rn}</h1>
{meta}
<article class="{entry_class}">
{chr(10).join(body)}
</article>
{day_nav(n, prefix)}
{share}
</main>"""
    page = (head(title=title, description=desc, url=url, prefix=prefix, og_type="article")
            + header(prefix) + article + footer(prefix, str(n)))
    out = ROOT / "dia" / str(n) / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(page, encoding="utf-8")
    return title, desc, url, d


def render_archive():
    months = {}
    for n in sorted((int(key) for key in DAYS if is_published(int(key))),
                    key=lambda n: (day_date(n), n)):
        day = day_date(n)
        months.setdefault((day.year, day.month), []).append((n, day))

    latest = next(reversed(months), None)
    years = {}
    for year, month in months:
        years.setdefault(year, []).append(month)

    for selected in [None, *(key for key in months if key != latest)]:
        active = selected or latest
        suffix = f"{selected[0]}-{selected[1]:02d}/" if selected else ""
        prefix = "../../" if selected else "../"
        archive_path = ROOT / "dias" / suffix
        archive_path.mkdir(parents=True, exist_ok=True)
        month_nav = ""
        if len(months) > 1:
            groups = []
            for year, year_months in reversed(years.items()):
                links = []
                for month in year_months:
                    key = (year, month)
                    href = "" if key == latest else f"{year}-{month:02d}/"
                    current = ' aria-current="page"' if key == active else ""
                    links.append(f'<li><a href="{prefix}dias/{href}"{current}>'
                                 f'{MONTHS_ES[month - 1].capitalize()}</a></li>')
                opened = " open" if active and active[0] == year else ""
                groups.append(f'<details{opened}><summary>{year}</summary>'
                              f'<ul>{"".join(links)}</ul></details>')
            month_nav = ('<nav class="archive-months" aria-label="Meses del archivo">'
                         + "".join(groups) + '</nav>')
        entries = ""
        if active:
            year, month = active
            month_name = MONTHS_ES[month - 1]
            items = []
            for n, day in months[active]:
                items.append(f'<li><a href="{prefix}dia/{n}/"><span>Día {roman(n)}</span>'
                             f'<time datetime="{day.isoformat()}">{day.day} de {month_name}</time></a></li>')
            entries = (f'<section aria-labelledby="archive-month"><h2 id="archive-month">'
                       f'{month_name.capitalize()} de {year}</h2>'
                       f'<ol class="archive-entries">{"".join(items)}</ol></section>')
        archive = (head(title="Archivo — Mil días",
                        description="Historias que encontraron su lugar en el tiempo.",
                        url=f"{SITE_URL}/dias/{suffix}", prefix=prefix)
                   .replace('assets/styles.css?v=2', 'assets/styles.css?v=3')
                   + header(prefix, current="archivo")
                   + f"""<main class="archive">
<h1>Archivo</h1>
<p class="subtitle">Historias que encontraron su lugar en el tiempo.</p>
{month_nav}
{entries}
<p class="archive-note">El resto de las páginas todavía está por escribirse.</p>
</main>"""
                   + footer(prefix, "4"))
        (archive_path / "index.html").write_text(archive, encoding="utf-8")


def main():
    # --- Portada ---
    url = f"{SITE_URL}/"
    desc = MANIFESTO[0] + " " + MANIFESTO[1]
    manifesto_html = "\n".join(f"<p><em>{esc(p)}</em></p>" for p in MANIFESTO)
    index = (head(title="Mil días — Un archivo de recuerdos", description=desc,
                  url=url, prefix="")
             + header("")
             + f"""<main class="cover">
<img class="hero-svg" src="assets/hourglass.svg?v=2" alt="" width="60" height="92">
<h1>Mil días</h1>
<p class="subtitle">{esc(SITE['subtitle'])}</p>
<hr class="gold-rule">
<div class="cover-text">
{manifesto_html}
</div>
<p class="signature"><span class="signature-name">{esc(SITE['author'])}</span></p>
</main>"""
             + footer("", "4"))
    (ROOT / "index.html").write_text(index, encoding="utf-8")

    render_archive()
    # dias.html redirige a dias/ (compatibilidad con la ruta /dias del original)
    (ROOT / "dias.html").write_text(
        '<!DOCTYPE html>\n<html lang="es"><head><meta charset="utf-8">'
        '<meta http-equiv="refresh" content="0; url=dias/">'
        '<link rel="canonical" href="dias/">'
        '<title>Archivo — Mil días</title></head>'
        '<body><p>El archivo está en <a href="dias/">dias/</a>.</p></body></html>\n',
        encoding="utf-8")

    # --- Qué es esto (solo información verificada del proyecto) ---
    about = (head(title="Qué es esto — Mil días",
                  description="Hay recuerdos que no desaparecen.",
                  url=f"{SITE_URL}/acerca/", prefix="../")
             + header("../", current="acerca")
             + f"""<main class="about">
<h1>Qué es esto</h1>
<p class="subtitle">Un archivo de recuerdos</p>
<hr class="gold-rule">
<div class="manifesto">
{manifesto_html}
</div>
<p class="signature"><span class="signature-name">{esc(SITE['author'])}</span></p>
<ul class="about-links">
<li><a href="../">Leer desde el inicio — Día I</a></li>
<li><a href="../dias/">Ver el archivo completo</a></li>
<li><a href="../feed.xml">Feed RSS</a></li>
</ul>
</main>"""
             + footer("../", "4"))
    (ROOT / "acerca").mkdir(exist_ok=True)
    (ROOT / "acerca" / "index.html").write_text(about, encoding="utf-8")

    # --- Días 1..1000 ---
    day_meta = {}
    for n in range(1, 1001):
        day_meta[n] = render_day(n)

    # --- Sitemap ---
    urls = [("", "2026-11-06"), ("dias/", "2026-11-06"), ("acerca/", "2026-11-06")]
    for n in range(1, 1001):
        urls.append((f"dia/{n}/", day_meta[n][3].isoformat()))
    sitemap = ('<?xml version="1.0" encoding="UTF-8"?>\n'
               '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
               + "".join(
                   f"  <url><loc>{SITE_URL}/{p}</loc><lastmod>{lm}</lastmod></url>\n"
                   for p, lm in urls)
               + "</urlset>\n")
    (ROOT / "sitemap.xml").write_text(sitemap, encoding="utf-8")

    # --- robots.txt ---
    (ROOT / "robots.txt").write_text(
        "User-agent: *\nAllow: /\n\n"
        f"Sitemap: {SITE_URL}/sitemap.xml\n", encoding="utf-8")

    # --- RSS ---
    items = []
    for n in sorted((k for k in DAYS if DAYS[k].get("published")), key=int):
        title, desc, url, d = day_meta[int(n)]
        items.append(
            f"    <item>\n      <title>{esc(title)}</title>\n"
            f"      <link>{esc(url)}</link>\n      <guid>{esc(url)}</guid>\n"
            f"      <pubDate>{d.strftime('%a, %d %b %Y')} 12:00:00 -0300</pubDate>\n"
            f"      <description>{esc(desc)}</description>\n    </item>")
    feed = ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<rss version="2.0">\n<channel>\n'
            '  <title>Mil días</title>\n'
            f'  <link>{SITE_URL}/</link>\n'
            '  <description>Un archivo de recuerdos — ' + esc(SITE['author']) + '</description>\n'
            '  <language>es-AR</language>\n'
            + "\n".join(items)
            + "\n</channel>\n</rss>\n")
    (ROOT / "feed.xml").write_text(feed, encoding="utf-8")

    # --- 404 en español ---
    notfound = (head(title="Página no encontrada — Mil días",
                     description="Esta página no existe. Volvé a Mil días, un archivo de recuerdos.",
                     url=f"{SITE_URL}/404.html", prefix="")
                + header("")
                + """<main class="notfound">
<h1>Esta página no existe</h1>
<p class="subtitle">Quizás ese día todavía no llegó.</p>
<p><a class="today-link" href="index.html">Volver al inicio</a></p>
<p><a href="dias/">Ir al archivo</a></p>
</main>"""
                + footer("", "4"))
    (ROOT / "404.html").write_text(notfound, encoding="utf-8")

    (ROOT / ".nojekyll").write_text("", encoding="utf-8")
    print(f"Generadas 1000 páginas de día + portada + archivo + sitemap + feed.")
    print(f"Día 1000 = {day_date(1000)} (debe ser 2029-07-29)")


if __name__ == "__main__":
    main()
