# land

Landing para el QR de la tarjeta de presentación.

Una sola página (`index.html`), **sin CSS**: presenta los dos tipos de servicio,
ingeniería en sistemas y diseño gráfico, con sus listas y un enlace de WhatsApp
por persona (`wa.me`, formato 52 + 10 dígitos). HTML semántico pensado para
leerse en teléfono.

Abrir `index.html` en el navegador o servirlo con
`python3 -m http.server` desde este directorio.

## Favicon

`favicon.svg` (vectorial), `favicon.ico` (16/32/48) y `apple-touch-icon.png` (180).
Cuadrado verde con degradado y corazón blanco. Regenerar los PNG/ICO con
`python3 tools/favicon.py` (sin dependencias).
