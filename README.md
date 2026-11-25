# land

Landing para el QR de la tarjeta de presentación de Julio Cubas Cárdenas y
Ana Paula Orozco.

- `index.html` + `styles.css` — versión publicada, con CSS mínimo (mobile first).
- `sin-css.html` — la misma página sin ninguna hoja de estilo, como referencia.

Presenta los dos tipos de servicio (ingeniería en sistemas y diseño gráfico),
el aviso de contacto en texto y, al final, la lista de Links: WhatsApp de cada
quien, teléfono de oficina, portafolio de Ana Paula y el sitio de VEIA.

Local: `python3 -m http.server 8080` desde este directorio.

## Favicon

`favicon.svg` (vectorial), `favicon.ico` (16/32/48) y `apple-touch-icon.png` (180).
Cuadrado verde con degradado y corazón blanco. Regenerar los PNG/ICO con
`python3 tools/favicon.py` (sin dependencias).
