#!/usr/bin/env python3
"""Genera favicon (SVG ya existe) y PNG/ICO sin dependencias."""
import struct, zlib, math, pathlib

VERDE_CLARO = (0x1a, 0xa8, 0x76)
VERDE_OSCURO = (0x0a, 0x5a, 0x45)
BLANCO = (0xff, 0xff, 0xff)


def gradiente(t):
    return tuple(round(a + (b - a) * t) for a, b in zip(VERDE_CLARO, VERDE_OSCURO))


def dentro_corazon(u, v):
    s = 0.55
    x = u / s
    y = v / s - 0.18
    return (x * x + y * y - 1) ** 3 - x * x * y * y * y <= 0


def dentro_rect(px, py, n, radio):
    radio = radio * n
    cx = min(max(px, radio), n - radio)
    cy = min(max(py, radio), n - radio)
    dx, dy = px - cx, py - cy
    return dx * dx + dy * dy <= radio * radio


def render(n, radio, ss=4):
    filas = []
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
                    u = x / n * 2 - 1
                    v = 1 - y / n * 2
                    if dentro_corazon(u, v):
                        cr, cg, cb = BLANCO
                    else:
                        t = (u + v + 2) / 4
                        cr, cg, cb = gradiente(t)
                    r += cr; g += cg; b += cb; a += 255
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


base = pathlib.Path(__file__).resolve().parent.parent
(base / "favicon-32.png").write_bytes(png(32, 0.22))
(base / "apple-touch-icon.png").write_bytes(png(180, 0.0, ss=3))
(base / "favicon.ico").write_bytes(ico([16, 32, 48], 0.22))
print("listo")
