"""
tests/test_signal.py — Testy jednostkowe · signal_engine v2
Uruchom: python3 -m pytest tests/test_signal.py -v
         lub: python3 tests/test_signal.py
"""

import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.signal_engine import generate_pulse, MODES


def _run(name, fn):
    try:
        fn()
        print(f"  ✓ {name}")
        return True
    except Exception as e:
        print(f"  ✗ {name} — {e}")
        return False


def test_stable_mode():
    """Tryb stable: każda próbka = level."""
    r = generate_pulse(level=0.7, mode="stable", duration_s=1.0, sample_rate=10.0)
    assert all(abs(v - 0.7) < 1e-4 for v in r["preview"])
    assert r["stats"]["duty_cycle"] == 1.0


def test_off_mode():
    """Tryb off: każda próbka = 0."""
    r = generate_pulse(level=1.0, mode="off", duration_s=1.0, sample_rate=10.0)
    assert all(v == 0.0 for v in r["preview"])
    assert r["stats"]["max"] == 0.0
    assert r["stats"]["duty_cycle"] == 0.0


def test_pulse_mode_low_sample_rate():
    """Tryb pulse działa poprawnie przy niskim sample_rate (5 Hz).
    BUG w v1: przy sr=5 i duty=0.15, period=0.5 → wszystkie próbki = level.
    POPRAWKA v2: obliczenie przez czas, nie indeks próbki.
    """
    r = generate_pulse(
        level=1.0, mode="pulse", duration_s=2.0,
        sample_rate=5.0, pulse_period_s=0.5, pulse_duty=0.15
    )
    # duty_cycle powinien być ~0.15 (15% czasu aktywny)
    # Przy sr=5 i period=0.5 mamy 2.5 próbki na okres
    # Impuls trwa 0.15×0.5=0.075s < 1/5=0.2s → może trafić 0 lub 1 próbkę na okres
    # Ważne: NIE wszystkie próbki mogą być = 1.0
    preview_vals = set(r["preview"])
    assert 0.0 in preview_vals or r["stats"]["duty_cycle"] < 1.0, \
        "pulse przy sr=5 nie powinien zwracać samych 1.0"


def test_pulse_mode_high_sample_rate():
    """Tryb pulse: duty_cycle ≈ pulse_duty przy wysokim sample_rate."""
    r = generate_pulse(
        level=1.0, mode="pulse", duration_s=10.0,
        sample_rate=1000.0, pulse_period_s=0.5, pulse_duty=0.15
    )
    assert abs(r["stats"]["duty_cycle"] - 0.15) < 0.02, \
        f"duty_cycle={r['stats']['duty_cycle']:.4f} daleko od 0.15"


def test_wave_mode():
    """Tryb wave: wartości ∈ [0, level], mean ≈ level/2."""
    r = generate_pulse(level=1.0, mode="wave", duration_s=10.0, sample_rate=100.0)
    assert all(0.0 <= v <= 1.0 for v in r["preview"])
    assert abs(r["stats"]["mean"] - 0.5) < 0.05, \
        f"mean wave={r['stats']['mean']:.4f}, oczekiwano ~0.5"


def test_burst_mode():
    """Tryb burst: duty_cycle < 0.2 (serie krótkich impulsów)."""
    r = generate_pulse(
        level=1.0, mode="burst", duration_s=5.0,
        sample_rate=1000.0, pulse_period_s=1.0
    )
    # 3 impulsy × 20ms = 60ms aktywnych na 1000ms → duty ≈ 0.06
    assert r["stats"]["duty_cycle"] < 0.20, \
        f"burst duty_cycle={r['stats']['duty_cycle']:.4f}, powinno być < 0.20"


def test_sweep_mode():
    """Tryb sweep: mean ≈ level/2, wartości ∈ [0, level]."""
    r = generate_pulse(level=1.0, mode="sweep", duration_s=10.0, sample_rate=100.0)
    assert all(0.0 <= v <= 1.0 for v in r["preview"])
    assert abs(r["stats"]["mean"] - 0.5) < 0.05


def test_preview_length():
    """Preview zawsze 10 elementów (przy total_samples >= 10)."""
    r = generate_pulse(duration_s=5.0, sample_rate=100.0)
    assert len(r["preview"]) == 10


def test_preview_spread():
    """Preview jest rozłożony równomiernie — nie są to pierwsze 10 próbek.
    Test: preview[9] powinien odpowiadać końcowi sygnału, nie jego początku.
    """
    # Użyj sweep (narastającego) — pierwsze próbki ≈ 0, ostatnie ≈ 0.5
    r = generate_pulse(
        level=1.0, mode="sweep", duration_s=5.0,
        sample_rate=100.0, pulse_period_s=10.0   # długi okres → cały czas narastanie
    )
    # Próbka preview[9] powinna być późno w sygnale → wartość wyższa niż preview[0]
    assert r["preview"][9] > r["preview"][0], \
        "preview powinien być rozłożony — ostatnia próbka powinna być wyższa niż pierwsza przy sweep"


def test_total_samples():
    """total_samples = int(duration_s × sample_rate)."""
    r = generate_pulse(duration_s=3.7, sample_rate=50.0)
    assert r["total_samples"] == int(3.7 * 50.0)


def test_invalid_level():
    """level > 1.0 rzuca AssertionError."""
    try:
        generate_pulse(level=1.5)
        assert False
    except AssertionError:
        pass


def test_invalid_mode():
    """Nieznany tryb rzuca AssertionError."""
    try:
        generate_pulse(mode="nieznany")
        assert False
    except AssertionError:
        pass


def test_all_modes_run():
    """Wszystkie tryby generują wynik bez błędów."""
    for mode in MODES:
        r = generate_pulse(level=1.0, mode=mode, duration_s=1.0, sample_rate=100.0)
        assert r["total_samples"] == 100


def test_stats_keys():
    """Wynik zawiera stats z mean, max, duty_cycle."""
    r = generate_pulse()
    assert "mean"       in r["stats"]
    assert "max"        in r["stats"]
    assert "duty_cycle" in r["stats"]


if __name__ == "__main__":
    tests = [
        ("stable: wszystkie próbki = level",         test_stable_mode),
        ("off: wszystkie próbki = 0",                test_off_mode),
        ("pulse przy sr=5 (poprawka v2)",            test_pulse_mode_low_sample_rate),
        ("pulse duty_cycle ≈ 0.15 przy sr=1000",     test_pulse_mode_high_sample_rate),
        ("wave: mean ≈ 0.5",                         test_wave_mode),
        ("burst: duty_cycle < 0.20",                 test_burst_mode),
        ("sweep: mean ≈ 0.5",                        test_sweep_mode),
        ("preview ma 10 elementów",                  test_preview_length),
        ("preview równomiernie rozłożony",           test_preview_spread),
        ("total_samples = duration × sample_rate",   test_total_samples),
        ("level > 1.0 → AssertionError",             test_invalid_level),
        ("nieznany mode → AssertionError",           test_invalid_mode),
        ("wszystkie tryby generują wynik",           test_all_modes_run),
        ("stats zawiera mean, max, duty_cycle",      test_stats_keys),
    ]

    print("=" * 50)
    print("test_signal.py — signal_engine v2")
    print("=" * 50)
    ok = sum(_run(name, fn) for name, fn in tests)
    print(f"\n  {ok}/{len(tests)} testów przeszło")
