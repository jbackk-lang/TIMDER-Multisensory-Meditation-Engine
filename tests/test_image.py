"""
tests/test_image.py — Testy jednostkowe · image_engine v2
Uruchom: python3 -m pytest tests/test_image.py -v
         lub: python3 tests/test_image.py
"""

import sys, os, math, tempfile
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.image_engine import generate_fractal, PRESETS, _interpolate_color


def _run(name, fn):
    try:
        fn()
        print(f"  ✓ {name}")
        return True
    except Exception as e:
        print(f"  ✗ {name} — {e}")
        return False


def test_meta_only():
    """render=False zwraca tylko metadane, bez pikseli."""
    r = generate_fractal("ρ-smooth", size=16, render=False)
    assert r["rendered"] is False
    assert r["pixel_data"] is None
    assert r["pixels"] == 16 * 16
    assert r["defect_ratio"] == PRESETS["ρ-smooth"]["defect"]


def test_render_shape():
    """render=True zwraca pixel_data o kształcie size×size."""
    r = generate_fractal("ρ-smooth", size=16, render=True)
    assert r["rendered"] is True
    assert r["pixel_data"] is not None
    rows = r["pixel_data"]
    assert len(rows) == 16
    assert len(rows[0]) == 16 * 3   # RGB


def test_all_presets_render():
    """Wszystkie presety renderują bez błędów."""
    for preset in PRESETS:
        r = generate_fractal(preset, size=8, render=True)
        assert r["rendered"], f"preset {preset} nie wyrenderował"
        assert r["pixel_data"] is not None


def test_julia_preset():
    """Preset ρ-julia używa trybu Julia."""
    r = generate_fractal("ρ-julia", size=16, render=False)
    assert r["mode"] == "julia"


def test_pixel_values_in_range():
    """Wszystkie wartości pikseli są w [0, 255]."""
    r = generate_fractal("ρ-smooth", size=16, render=True)
    for row in r["pixel_data"]:
        for v in row:
            assert 0 <= v <= 255, f"wartość piksela poza zakresem: {v}"


def test_save_png():
    """Zapis PNG do pliku działa — plik jest niepusty."""
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        path = f.name
    try:
        r = generate_fractal("ρ-smooth", size=16, render=True, save_path=path)
        assert r["saved_to"] == path
        assert os.path.getsize(path) > 0
    finally:
        os.unlink(path)


def test_invalid_preset():
    """Nieznany preset rzuca AssertionError."""
    try:
        generate_fractal("ρ-nieistniejący")
        assert False, "powinien rzucić AssertionError"
    except AssertionError:
        pass


def test_size_too_small():
    """size < 8 rzuca AssertionError."""
    try:
        generate_fractal("ρ-smooth", size=4)
        assert False
    except AssertionError:
        pass


def test_size_too_large():
    """size > 1024 rzuca AssertionError."""
    try:
        generate_fractal("ρ-smooth", size=2048)
        assert False
    except AssertionError:
        pass


def test_colormap_interpolation():
    """_interpolate_color zwraca tuple (R,G,B) w [0,255]."""
    for t in [0.0, 0.25, 0.5, 0.75, 1.0]:
        r, g, b = _interpolate_color(t, "teal")
        assert 0 <= r <= 255 and 0 <= g <= 255 and 0 <= b <= 255


def test_deterministic():
    """Ten sam preset + size → identyczne pixel_data."""
    r1 = generate_fractal("ρ-smooth", size=16, render=True)
    r2 = generate_fractal("ρ-smooth", size=16, render=True)
    assert r1["pixel_data"] == r2["pixel_data"]


if __name__ == "__main__":
    tests = [
        ("meta only (render=False)",         test_meta_only),
        ("kształt pixel_data",               test_render_shape),
        ("wszystkie presety renderują",       test_all_presets_render),
        ("preset ρ-julia → mode julia",       test_julia_preset),
        ("wartości pikseli ∈ [0,255]",       test_pixel_values_in_range),
        ("zapis PNG",                         test_save_png),
        ("nieznany preset → AssertionError",  test_invalid_preset),
        ("size < 8 → AssertionError",         test_size_too_small),
        ("size > 1024 → AssertionError",      test_size_too_large),
        ("interpolacja koloru",               test_colormap_interpolation),
        ("determinizm",                       test_deterministic),
    ]

    print("=" * 50)
    print("test_image.py — image_engine v2")
    print("=" * 50)
    ok = sum(_run(name, fn) for name, fn in tests)
    print(f"\n  {ok}/{len(tests)} testów przeszło")
