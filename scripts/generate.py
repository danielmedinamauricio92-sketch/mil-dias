#!/usr/bin/env python3
"""Generador estático de Mil días.

Fuente única de contenido: content/days.json (días 1-4 transcritos de
https://mil-dias.lovable.app/ vía browser.open; días 5-1000, placeholder).
Uso:  python3 scripts/generate.py
Salida: index.html, dias/index.html, dia/<n>/index.html, sitemap.xml,
        feed.xml, robots.txt, 404.html
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
SITE_URL = "https://danielmedinamauricio92-sketch.github.io/mil-dias"
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


def fmt_date_es(d: date) -> str:
    months = ["enero", "febrero", "marzo", "abril", "mayo", "junio",
              "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
    return f"{d.day} de {months[d.month - 1]} de {d.year}"


HOURGLASS = """<svg viewBox="0 0 100 100" fill="none" stroke="#c9a227" stroke-width="3" stroke-linecap="round" aria-hidden="true">
<path d="M25 8 H75 M25 92 H75"/>
<path d="M25 8 L45 50 L25 92 M75 8 L55 50 L75 92"/>
<path d="M45 50 H55" stroke="#d4af37" stroke-width="2"/>
<circle cx="50" cy="62" r="5" fill="#c9a227" stroke="none"/>
<path d="M45 72 L55 72 L50 82 Z" fill="#c9a227" stroke="none"/>
</svg>"""

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
<link rel="alternate" type="application/rss+xml" title="Mil días" href="{SITE_URL}/feed.xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,500;0,600;1,400&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{prefix}assets/styles.css">
</head>
"""


def header(prefix):
    return f"""<body>
<header class="top">
<a class="logo" href="{prefix}index.html" aria-label="Inicio — Mil días">{HOURGLASS}<span>Mil días</span></a>
<a class="nav-archivo" href="{prefix}dias/">Archivo</a>
</header>
"""


def footer(prefix, progress):
    return f"""<footer class="site">
<p>Mil días — Un archivo de recuerdos · por {esc(SITE['author'])}</p>
<p><a href="{esc(SITE['portfolio'])}">Portfolio</a> · <a href="{esc(SITE['github'])}">GitHub</a></p>
<p>Reproducción estática hecha por el autor a partir de <a href="{esc(SITE['source'])}">mil-dias.lovable.app</a>, sin Lovable.</p>
</footer>
<div class="progress"><b>{progress}</b> / 1000</div>
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
    prev_link = (f'<a href="{prefix}dia/{n-1}/">‹ Día anterior</a>' if n > 1
                 else '<span></span>')
    next_link = (f'<a href="{prefix}dia/{n+1}/">Día siguiente ›</a>' if n < 1000
                 else '<span></span>')
    return f"""<nav class="day-nav">{prev_link}<a href="{prefix}index.html">Hoy</a>{next_link}</nav>"""


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
        if b["type"] == "h2":
            body.append(f"<h2>{esc(b['text'])}</h2>")
        else:
            body.append(f"<p>{esc(b['text'])}</p>")
    entry_class = "entry" if published else "entry placeholder"
    meta = (f'<p class="meta"><span>{fmt_date_es(d)}</span>'
            f'<span>{reading_minutes(n)} min de lectura</span>'
            f'<span>por {esc(SITE["author"])}</span></p>' if published
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


def main():
    # --- Portada ---
    url = f"{SITE_URL}/"
    desc = MANIFESTO[0] + " " + MANIFESTO[1]
    manifesto_html = "\n".join(f"<p>{esc(p)}</p>" for p in MANIFESTO)
    index = (head(title="Mil días — Un archivo de recuerdos", description=desc,
                  url=url, prefix="")
             + header("")
             + f"""<main>
{HOURGLASS.replace('viewBox="0 0 100 100"', 'viewBox="0 0 100 100" class="hero-svg"')}
<h1>Mil días</h1>
<p class="subtitle">{esc(SITE['subtitle'])}</p>
<p class="dates">{esc(SITE['start_label'])}</p>
<hr class="gold-rule">
<div class="manifesto">
{manifesto_html}
</div>
<p><a class="today-link" href="dia/4/">Hoy — Día IV de 1000</a></p>
</main>"""
             + footer("", "4"))
    (ROOT / "index.html").write_text(index, encoding="utf-8")

    # --- Archivo ---
    groups = []
    for start in range(1, 1001, 100):
        end = min(start + 99, 1000)
        items = []
        for n in range(start, end + 1):
            if is_published(n):
                items.append(f'<a href="../dia/{n}/">{roman(n)}</a>')
            else:
                items.append(f'<span aria-disabled="true">{roman(n)}</span>')
        groups.append(f"<h2>Días {roman(start)} – {roman(end)}</h2>\n"
                      f'<div class="archive-grid">{"".join(items)}</div>')
    archive = (head(title="Mil días — un archivo de recuerdos",
                    description="Archivo de Mil días: mil días de recuerdos, del 3 de noviembre de 2026 al 29 de julio de 2029. Solo los días I a IV están publicados.",
                    url=f"{SITE_URL}/dias/", prefix="../")
               + header("../")
               + f"""<main class="archive">
<h1>Archivo</h1>
<p class="subtitle">Mil días, uno por uno.</p>
<p class="meta"><span>4 de 1000 publicados</span><span>Del 3 de noviembre de 2026 al 29 de julio de 2029</span></p>
{chr(10).join(groups)}
</main>"""
               + footer("../", "4"))
    (ROOT / "dias").mkdir(exist_ok=True)
    (ROOT / "dias" / "index.html").write_text(archive, encoding="utf-8")
    # dias.html redirige a dias/ (compatibilidad con la ruta /dias del original)
    (ROOT / "dias.html").write_text(
        '<!DOCTYPE html>\n<html lang="es"><head><meta charset="utf-8">'
        '<meta http-equiv="refresh" content="0; url=dias/">'
        '<link rel="canonical" href="dias/">'
        '<title>Archivo — Mil días</title></head>'
        '<body><p>El archivo está en <a href="dias/">dias/</a>.</p></body></html>\n',
        encoding="utf-8")

    # --- Días 1..1000 ---
    day_meta = {}
    for n in range(1, 1001):
        day_meta[n] = render_day(n)

    # --- Sitemap ---
    urls = [("", "2026-11-06"), ("dias/", "2026-11-06")]
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
            '  <description>Un archivo de recuerdos — Mauricio Daniel Medina</description>\n'
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
