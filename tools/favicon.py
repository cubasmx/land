#!/usr/bin/env python3
"""Genera favicon PNG/ICO (nodo de red) sin dependencias externas.

El SVG equivalente vive en favicon.svg. Este script dibuja la misma figura a
mano: cuadrado verde con degradado, tres nodos blancos unidos por trazos.
Regenerar: python3 tools/favicon.py
"""
import math
import pathlib
import struct
import zlib

VERDE_CLARO = (0x1a, 0xA8, 0x76)
VERDE_OSCURO = (0x0A, 0x5A, 0x45)
BLANCO = (0xFF, 0xFF, 0xFF)

# Geometría en un lienzo de 64x64 (la misma del SVG).
NODOS = ((20, 21), (46, 27), (32, 47))
RADIO_NODO = 7.0
TRAMOS = ((NODOS[0], NODOS[1]), (NODOS[1], NODOS[2]), (NODOS[2], NODOS[0]))
GROSOR = 1.3  # radio del trazo (stroke-width 2.6)


def gradiente(t):
    return tuple(round(a + (b - a) * t) for a, b in zip(VERDE_CLARO, VERDE_OSCURO))


def dist_segmento(x, y, a, b):
    ax, ay = a
    bx, by = b
    dx, dy = bx - ax, by - ay
    t = ((x - ax) * dx + (y - ay) * dy) / (dx * dx + dy * dy)
    t = max(0.0, min(1.0, t))
    px, py = ax + t * dx, ay + t * dy
    return math.hypot(x - px, y - py)


def dentro_figura(x, y):
    for cx, cy in NODOS:
        if (x - cx) ** 2 + (y - cy) ** 2 <= RADIO_NODO ** 2:
            return True
    for a, b in TRAMOS:
        if dist_segmento(x, y, a, b) <= GROSOR:
            return True
    return False


def dentro_rect(x, y, n, radio):
    radio *= n
    cx = min(max(x, radio), n - radio)
    cy = min(max(y, radio), n - radio)
    return (x - cx) ** 2 + (y - cy) ** 2 <= radio * radio


def render(n, radio, ss=4):
    filas = []
    escala = 64 / n
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
                        u = x / n
                        v = y / n
                        cr, cg, cb = gradiente((u + v) / 2)
                    r += cr
                    g += cg
                    b += cb
                    a += 255
            total = ss * ss
            if a == 0:
                fila += bytes((0, 0, 0, 0))
            else:
                fila += bytes((r // total, g // total, b // total, a // total))
        filas.append(bytes(fila))
    return b"".join(filas)


def png(n, radio, ss=4):
    raw = render(n, radio, ss)

    def chunk(tipo, datos):
        c = struct.pack(">I", len(datos)) + tipo + datos
        return c + struct.pack(">I", zlib.crc32(tipo + datos) & 0xFFFFFFFF)

    ihdr = struct.pack(">IIBBBBB", n, n, 8, 6, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b""))


def ico(tamanos, radio):
    imgs = [png(n, radio) for n in tamanos]
    cab = struct.pack("<HHH", 0, 1, len(imgs))
    offset = 6 + 16 * len(imgs)
    entradas, datos = b"", b""
    for n, img in zip(tamanos, imgs):
        entradas += struct.pack("<BBBBHHII", n % 256, n % 256, 0, 0, 1, 32, len(img), offset)
        offset += len(img)
        datos += img
    return cab + entradas + datos


RADIO_ESQUINA = 14 / 64

base = pathlib.Path(__file__).resolve().parent.parent
(base / "favicon-32.png").write_bytes(png(32, RADIO_ESQUINA))
(base / "apple-touch-icon.png").write_bytes(png(180, 0.0, ss=3))
(base / "favicon.ico").write_bytes(ico([16, 32, 48], RADIO_ESQUINA))
print("listo")
