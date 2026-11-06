# Mil días

Un archivo de recuerdos, del 3 de noviembre de 2026 al 29 de julio de 2029.
Mil días, mil textos. Por Mauricio Daniel Medina.

Reproducción estática hecha por el autor a partir de
[https://mil-dias.lovable.app/](https://mil-dias.lovable.app/), sin Lovable:
HTML, CSS y JavaScript vanilla, sin framework, sin base de datos, sin login.

## Qué hay acá

- `index.html` — portada con el manifiesto completo.
- `dias/` — archivo con los 1000 días en números romanos (I–M). Solo I–IV
  son enlaces; el resto está en gris, no clicable, agrupado por centenas.
- `dia/<n>/` — una página por día, del 1 al 1000.
  - Días 1–4: texto completo, transcrito de mil-dias.lovable.app.
  - Días 5–999: «Este día aún no llegó.»
  - Día 1000: «Todavía no.»
- `content/days.json` — **fuente única de contenido**. Los textos viven acá.
- `scripts/generate.py` — genera todas las páginas, el sitemap y el feed
  a partir de `content/days.json`.
- `assets/` — `styles.css`, `og-mil-dias.png` y `og-mil-dias.svg`
  (reloj de arena dorado sobre negro).
- `sitemap.xml` — portada + archivo + las 1000 rutas de día.
- `feed.xml` — RSS con los 4 días publicados.
- `robots.txt` — con línea `Sitemap:`.
- `404.html` — página no encontrada, en español.
- `.nojekyll` — para que GitHub Pages sirva los archivos tal cual.

## Mejoras respecto al original

Sin tocar la voz ni los textos:

- Cada día tiene título propio en `<title>` (su primera frase temática),
  meta description, Open Graph y Twitter Card con imagen para compartir.
- Fecha real de publicación (día 1 = 2026-11-03, día 2 = 2026-11-04,
  día 3 = 2026-11-05, día 4 = 2026-11-06), autor y tiempo de lectura.
- Botones para compartir: copiar enlace, WhatsApp, X y LinkedIn.
- Footer con autor, portfolio y GitHub.
- Archivo completo hasta el día 1000 (el original solo llegaba al C).
- Sitemap, RSS y 404 en español, que el original no tenía.

## Cómo agregar un día nuevo

1. Abrir `content/days.json`.
2. Agregar la entrada del día, por ejemplo el día 5:

```json
"5": {
  "date": "2026-11-07",
  "published": true,
  "blocks": [
    {"type": "p", "text": "Primer párrafo del día."},
    {"type": "h2", "text": "Un subtítulo, si lo hay"},
    {"type": "p", "text": "Siguiente párrafo."}
  ]
}
```

   La fecha es la del día: día *n* = 3 de noviembre de 2026 + (*n* − 1) días.
   Los `blocks` se transcriben en orden, párrafo por párrafo, tal como
   se publican. No inventar párrafos que no existan.
3. Correr el generador:

```bash
python3 scripts/generate.py
```

4. Revisar `dia/5/` en el navegador y, si está bien, subir los cambios.

## Probar en local

```bash
python3 scripts/generate.py
python3 -m http.server 8000
# Abrir http://127.0.0.1:8000/
```

## Desplegar en GitHub Pages

1. Crear el repo (por ejemplo `mil-dias`) en GitHub y subir todo el
   contenido de esta carpeta a la rama `main`.
2. En GitHub: Settings → Pages → Source: **Deploy from a branch**,
   Branch: `main`, carpeta `/ (root)`.
3. La URL queda:
   `https://<usuario>.github.io/mil-dias/`
4. Si esa es la URL final, cambiar `SITE_URL` en `scripts/generate.py`
   por esa URL, volver a correr el generador y subir de nuevo, para que
   el sitemap, el feed y las etiquetas Open Graph apunten bien.

Para Vercel, en cambio: importar el repo, sin comando de build
(es un sitio estático) y con la carpeta raíz como salida.

## Nota sobre el contenido

Los textos de los días 1–4 son los publicados por el autor en
mil-dias.lovable.app al 6 de noviembre de 2026. Este repo es la versión
propia y editable de ese proyecto; Lovable ya no es necesaria para
trabajar en él.
