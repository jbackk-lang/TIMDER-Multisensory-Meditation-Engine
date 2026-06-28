"""
image_engine.py — ImageEngine · TIMDER Multisensory Meditation Engine
Generuje geometrię obrazu (defekt ρ) na podstawie fraktali Mandelbrota/Julii.

POPRAWKA v2:
  - Faktyczny rendering pikseli (numpy) zamiast samych metadanych
  - generate_fractal() zwraca macierz pikseli + opcjonalnie zapisuje PNG
  - Nowy preset "ρ-julia" (zbiór Julii)
  - Parametr `render=True/False` — kontrola czy liczyć piksele
  - Zapis do PNG przez stdlib (bez PIL) przez moduł png_writer

Użycie:
    from image_engine import generate_fractal

    meta = generate_fractal("ρ-smooth", size=256, render=False)
    full = generate_fractal("ρ-smooth", size=256, render=True, save_path="out.png")
"""

import math
import struct
import zlib
import os

# ── Presety ──────────────────────────────────────────────────────────────────

PRESETS = {
    "ρ-smooth": {
        "mode":       "mandelbrot",
        "iterations": 64,
        "defect":     0.10,
        "cx":        -0.5,
        "cy":         0.0,
        "zoom":       1.5,
        "colormap":   "teal",
    },
    "ρ-rough": {
        "mode":       "mandelbrot",
        "iterations": 128,
        "defect":     0.50,
        "cx":        -0.75,
        "cy":         0.1,
        "zoom":       2.5,
        "colormap":   "amber",
    },
    "ρ-minimal": {
        "mode":       "mandelbrot",
        "iterations": 32,
        "defect":     0.02,
        "cx":        -0.5,
        "cy":         0.0,
        "zoom":       1.0,
        "colormap":   "gray",
    },
    "ρ-julia": {
        "mode":       "julia",
        "iterations": 96,
        "defect":     0.25,
        "cx":        -0.7269,
        "cy":         0.1889,
        "zoom":       1.5,
        "colormap":   "purple",
    },
}

# ── Kolormapa (RGB) ───────────────────────────────────────────────────────────

COLORMAPS = {
    "teal":   [(14, 116, 144), (6, 182, 212), (165, 243, 252), (255, 255, 255)],
    "amber":  [(146, 64, 14),  (217, 119, 6),  (251, 191, 36),  (255, 251, 235)],
    "gray":   [(30, 30, 30),   (100, 100, 100),(200, 200, 200), (240, 240, 240)],
    "purple": [(46, 16, 101),  (109, 40, 217), (196, 181, 253), (245, 243, 255)],
}


def _interpolate_color(t: float, colormap: str) -> tuple:
    """Interpoluje kolor z mapy dla wartości t ∈ [0, 1]."""
    stops = COLORMAPS.get(colormap, COLORMAPS["teal"])
    n = len(stops) - 1
    idx = min(int(t * n), n - 1)
    local_t = (t * n) - idx
    r0, g0, b0 = stops[idx]
    r1, g1, b1 = stops[idx + 1]
    return (
        int(r0 + (r1 - r0) * local_t),
        int(g0 + (g1 - g0) * local_t),
        int(b0 + (b1 - b0) * local_t),
    )


# ── Rendering fraktala ────────────────────────────────────────────────────────

def _mandelbrot(cx: float, cy: float, zoom: float,
                size: int, max_iter: int) -> list:
    """Renderuje zbiór Mandelbrota. Zwraca listę wierszy RGB."""
    rows = []
    scale = zoom * 3.5 / size
    for py in range(size):
        row = []
        y0 = (py - size / 2) * scale + cy
        for px in range(size):
            x0 = (px - size / 2) * scale + cx
            x, y, i = 0.0, 0.0, 0
            while x * x + y * y <= 4.0 and i < max_iter:
                x, y = x * x - y * y + x0, 2 * x * y + y0
                i += 1
            t = i / max_iter
            row.extend(_interpolate_color(t, "teal"))  # placeholder, nadpisane poniżej
        rows.append(row)
    return rows


def _render(preset_name: str, size: int) -> list:
    """
    Renderuje fraktal do listy wierszy RGB (size × size × 3 bajtów).
    Zwraca: list[list[int]] — każdy wiersz to [R,G,B, R,G,B, ...]
    """
    p = PRESETS[preset_name]
    max_iter = p["iterations"]
    cx, cy   = p["cx"], p["cy"]
    zoom     = p["zoom"]
    colormap = p["colormap"]
    mode     = p["mode"]

    scale = zoom * 3.5 / size
    rows  = []

    for py in range(size):
        row = []
        y0  = (py - size / 2) * scale + cy
        for px in range(size):
            x0 = (px - size / 2) * scale + cx

            if mode == "julia":
                # Julia: c stały (cx, cy), z startuje z (x0, y0)
                x, y = x0, y0
                i    = 0
                while x * x + y * y <= 4.0 and i < max_iter:
                    x, y = x * x - y * y + cx, 2 * x * y + cy
                    i += 1
            else:
                # Mandelbrot: c = (x0, y0), z startuje z 0
                x, y = 0.0, 0.0
                i    = 0
                while x * x + y * y <= 4.0 and i < max_iter:
                    x, y = x * x - y * y + x0, 2 * x * y + y0
                    i += 1

            # Smooth coloring: ucieczka + log normalizacja
            if i < max_iter:
                log2   = math.log(math.log(x * x + y * y + 1e-10) / 2) / math.log(2)
                smooth = (i + 1 - log2) / max_iter
                smooth = max(0.0, min(1.0, smooth))
            else:
                smooth = 1.0  # wnętrze zbioru = kolor ostatni

            row.extend(_interpolate_color(smooth, colormap))
        rows.append(row)

    return rows


# ── Zapis PNG (bez zewnętrznych bibliotek) ────────────────────────────────────

def _write_png(path: str, rows: list, size: int) -> None:
    """Zapisuje listę wierszy RGB do pliku PNG używając tylko stdlib."""
    def chunk(name: bytes, data: bytes) -> bytes:
        c = name + data
        return struct.pack(">I", len(data)) + c + struct.pack(">I", zlib.crc32(c) & 0xFFFFFFFF)

    png_sig  = b"\x89PNG\r\n\x1a\n"
    ihdr_data = struct.pack(">IIBBBBB", size, size, 8, 2, 0, 0, 0)
    ihdr      = chunk(b"IHDR", ihdr_data)

    raw = b""
    for row in rows:
        raw += b"\x00" + bytes(row)

    idat = chunk(b"IDAT", zlib.compress(raw, 6))
    iend = chunk(b"IEND", b"")

    with open(path, "wb") as f:
        f.write(png_sig + ihdr + idat + iend)


# ── Główna funkcja ────────────────────────────────────────────────────────────

def generate_fractal(
    preset: str  = "ρ-smooth",
    size:   int  = 128,
    render: bool = True,
    save_path: str | None = None,
) -> dict:
    """
    Generuje geometrię obrazu defektu ρ.

    Parametry:
        preset    : jeden z "ρ-smooth", "ρ-rough", "ρ-minimal", "ρ-julia"
        size      : rozmiar obrazu w pikselach (size × size)
        render    : True = liczy piksele; False = tylko metadane (szybko)
        save_path : ścieżka do pliku PNG (opcjonalnie, tylko gdy render=True)

    Zwraca dict z:
        preset, size, pixels, defect_ratio, iterations, mode, colormap,
        rendered (bool), pixel_data (list[list[int]] lub None), saved_to (str lub None)
    """
    assert preset in PRESETS, \
        f"Nieznany preset '{preset}'. Dostępne: {list(PRESETS.keys())}"
    assert size >= 8,  "size musi być >= 8"
    assert size <= 1024, "size musi być <= 1024 (bez GPU)"

    p = PRESETS[preset]

    result = {
        "preset":       preset,
        "size":         f"{size}x{size}",
        "pixels":       size * size,
        "active_pixels": int(size * size * (1 - p["defect"])),
        "defect_ratio": p["defect"],
        "iterations":   p["iterations"],
        "mode":         p["mode"],
        "colormap":     p["colormap"],
        "rendered":     False,
        "pixel_data":   None,
        "saved_to":     None,
    }

    if render:
        pixel_data       = _render(preset, size)
        result["rendered"]    = True
        result["pixel_data"]  = pixel_data

        if save_path:
            _write_png(save_path, pixel_data, size)
            result["saved_to"] = save_path

    return result
