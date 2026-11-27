#!/usr/bin/env python3
"""Favicons del nodo de red, uno por día de la semana, sin dependencias.

Genera:
  favicon-1.svg … favicon-7.svg   (lunes … domingo, cada uno con su color)
  favicon.svg                     (copia del lunes, respaldo)
  favicon-32.png, apple-touch-icon.png, favicon.ico  (rojo señal, respaldo)

La paleta vive en DIAS y debe coincidir con las variables de styles.css.
Regenerar: python3 tools/favicon.py
"""
import math
import pathlib
import struct
import zlib

# (nombre, color claro, color base, color oscuro) — lunes a domingo.
DIAS = (
    ("lunes",      "#ef2b3d", "#c2152a", "#8c0e19"),
    ("martes",     "#f4511e", "#c03a12", "#8f2609"),
    ("miercoles",  "#f5a524", "#b4761a", "#7d4f0f"),
    ("jueves",     "#1aa876", "#0f6b52", "#0a5a45"),
    ("viernes",    "#12a4b8", "#0c6b7a", "#07454f"),
    ("sabado",     "#3b6ef0", "#2447b8", "#16266b"),
    ("domingo",    "#8b5cf6", "#5b32c4", "#341a75"),
)

BLANCO = (0xFF, 0xFF, 0xFF)

# Geometría en un lienzo de 64x64 (la misma del SVG).
NODOS = ((20, 21), (46, 27), (32, 47))
RADIO_NODO = 7.0
TRAMOS = ((NODOS[0], NODOS[1]), (NODOS[1], NODOS[2]), (NODOS[2], NODOS[0]))
GROSOR = 1.3  # radio del trazo (stroke-width 2.6)
RADIO_ESQUINA = 14 / 64


def hex_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def svg(claro, oscuro):
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" role="img" aria-label="Julio Cubas y Ana Paula Orozco">
  <defs>
    <linearGradient id="g" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="{claro}"/>
      <stop offset="1" stop-color="{oscuro}"/>
    </linearGradient>
  </defs>
  <rect width="64" height="64" rx="14" fill="url(#g)"/>
  <g stroke="#fff" stroke-width="2.6" stroke-linecap="round">
    <path d="M20 21 46 27M46 27 32 47M32 47 20 21"/>
  </g>
  <g fill="#fff">
    <circle cx="20" cy="21" r="7"/>
    <circle cx="46" cy="27" r="7"/>
    <circle cx="32" cy="47" r="7"/>
  </g>
</svg>
"""


def gradiente(t, claro, oscuro):
    return tuple(round(a + (b - a) * t) for a, b in zip(claro, oscuro))


def dist_segmento(x, y, a, b):
    ax, ay = a
    bx, by = b
    dx, dy = bx - ax, by - ay
    t = ((x - ax) * dx + (y - ay) * dy) / (dx * dx + dy * dy)
    t = max(0.0, min(1.0, t))
    return math.hypot(x - (ax + t * dx), y - (ay + t * dy))


def dentro_figura(x, y):
    for cx, cy in NODOS:
        if (x - cx) ** 2 + (y - cy) ** 2 <= RADIO_NODO ** 2:
            return True
    return any(dist_segmento(x, y, a, b) <= GROSOR for a, b in TRAMOS)


def dentro_rect(x, y, n, radio):
    radio *= n
    cx = min(max(x, radio), n - radio)
    cy = min(max(y, radio), n - radio)
    return (x - cx) ** 2 + (y - cy) ** 2 <= radio * radio


def render(n, radio, claro, oscuro, ss=4):
    filas = []
    escala = 64 / n
    total = ss * ss
    for py in range(n):
        fila = bytearray([0])  # filtro PNG 0
        for px in range(n):
            r = g = b = a = 0
            for sy in range(ss):
                for sx in range(ss):
                    x = px + (sx + 0.5) / ss
                    y = py + (sy + 0.5) / ss
                    if not dentro_rect(x, y, n, radio):
                        continue
                    if dentro_figura(x * escala, y * escala):
                        cr, cg, cb = BLANCO
                    else:
                        cr, cg, cb = gradiente((x / n + y / n) / 2, claro, oscuro)
                    r += cr
                    g += cg
                    b += cb
                    a += 255
            if a == 0:
                fila += bytes((0, 0, 0, 0))
            else:
                fila += bytes((r // total, g // total, b // total, a // total))
        filas.append(bytes(fila))
    return b"".join(filas)


def png(n, radio, claro, oscuro, ss=4):
    raw = render(n, radio, claro, oscuro, ss)

    def chunk(tipo, datos):
        c = struct.pack(">I", len(datos)) + tipo + datos
        return c + struct.pack(">I", zlib.crc32(tipo + datos) & 0xFFFFFFFF)

    ihdr = struct.pack(">IIBBBBB", n, n, 8, 6, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b""))


def ico(tamanos, radio, claro, oscuro):
    imgs = [png(n, radio, claro, oscuro) for n in tamanos]
    cab = struct.pack("<HHH", 0, 1, len(imgs))
    offset = 6 + 16 * len(imgs)
    entradas, datos = b"", b""
    for n, img in zip(tamanos, imgs):
        entradas += struct.pack("<BBBBHHII", n % 256, n % 256, 0, 0, 1, 32, len(img), offset)
        offset += len(img)
        datos += img
    return cab + entradas + datos


base = pathlib.Path(__file__).resolve().parent.parent

for i, (_nombre, claro, _base, oscuro) in enumerate(DIAS, start=1):
    (base / f"favicon-{i}.svg").write_text(svg(claro, oscuro), encoding="utf-8")

# Respaldo estático: el rojo del lunes.
_claro, _oscuro = hex_rgb(DIAS[0][1]), hex_rgb(DIAS[0][3])
(base / "favicon.svg").write_text(svg(DIAS[0][1], DIAS[0][3]), encoding="utf-8")
(base / "favicon-32.png").write_bytes(png(32, RADIO_ESQUINA, _claro, _oscuro))
(base / "apple-touch-icon.png").write_bytes(png(180, 0.0, _claro, _oscuro, ss=3))
(base / "favicon.ico").write_bytes(ico([16, 32, 48], RADIO_ESQUINA, _claro, _oscuro))
print("listo:", len(DIAS), "favicons + respaldos")
