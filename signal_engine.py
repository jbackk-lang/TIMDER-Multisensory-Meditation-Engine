"""
signal_engine.py — SignalEngine · TIMDER Multisensory Meditation Engine
Generuje sygnał klucza J (kanał synchronizacji).

POPRAWKA v2:
  - Tryb "pulse" oblicza czas impulsu PRZED dyskretyzacją → poprawne impulsy
    przy dowolnym sample_rate (nawet 5 Hz)
  - Nowy tryb "burst" — serie krótkich impulsów co N sekund
  - Nowy tryb "sweep" — liniowe narastanie i opadanie
  - preview zawsze 10 próbek równomiernie rozłożonych w czasie (nie pierwsze N)
  - Parametr pulse_duty: szerokość impulsu jako ułamek okresu (domyślnie 0.15)
  - Parametr pulse_period_s: okres impulsu w sekundach (domyślnie 0.5s)

Użycie:
    from signal_engine import generate_pulse

    sig = generate_pulse(level=1.0, mode="pulse", duration_s=5.0, sample_rate=100.0)
    print(sig["preview"])   # 10 próbek równomiernie z całego okresu
    print(sig["stats"])     # mean, max, duty_cycle
"""

import math


# ── Definicja trybów ──────────────────────────────────────────────────────────

MODES = ("stable", "pulse", "wave", "burst", "sweep", "off")


# ── Generator sygnału ─────────────────────────────────────────────────────────

def _sample(t: float, mode: str, level: float,
            pulse_period_s: float, pulse_duty: float) -> float:
    """
    Oblicza wartość sygnału w czasie t [s].

    Parametry:
        t              : czas w sekundach
        mode           : tryb sygnału
        level          : poziom bazowy [0, 1]
        pulse_period_s : okres impulsu w sekundach
        pulse_duty     : szerokość impulsu jako ułamek okresu [0, 1]
    """
    if mode == "off":
        return 0.0

    if mode == "stable":
        return level

    if mode == "wave":
        return level * (0.5 + 0.5 * math.sin(2 * math.pi * t / pulse_period_s))

    if mode == "sweep":
        # Trójkąt: narastanie od 0 do level, opadanie do 0 w każdym okresie
        phase = (t % pulse_period_s) / pulse_period_s
        if phase < 0.5:
            return level * phase * 2
        else:
            return level * (1.0 - (phase - 0.5) * 2)

    if mode == "pulse":
        # POPRAWKA: porównanie przez czas w sekundach, nie przez indeks próbki
        # Impuls aktywny gdy faza okresu < duty
        phase = (t % pulse_period_s) / pulse_period_s
        return level if phase < pulse_duty else 0.0

    if mode == "burst":
        # Seria 3 szybkich impulsów (20ms każdy) co pulse_period_s
        burst_width = 0.020   # 20 ms na impuls
        burst_gap   = 0.060   # 60 ms między impulsami w serii
        phase_t = t % pulse_period_s
        for i in range(3):
            start = i * burst_gap
            if start <= phase_t < start + burst_width:
                return level
        return 0.0

    return 0.0


def generate_pulse(
    level:          float = 1.0,
    mode:           str   = "stable",
    duration_s:     float = 60.0,
    sample_rate:    float = 100.0,
    pulse_period_s: float = 0.5,
    pulse_duty:     float = 0.15,
) -> dict:
    """
    Generuje sygnał klucza J dla kanału synchronizacji TIMDER.

    Parametry:
        level          : poziom bazowy sygnału [0.0, 1.0]
        mode           : "stable" | "pulse" | "wave" | "burst" | "sweep" | "off"
        duration_s     : długość sygnału w sekundach
        sample_rate    : liczba próbek na sekundę [Hz]
        pulse_period_s : okres impulsu / fali [s] (domyślnie 0.5s = 2 Hz)
        pulse_duty     : szerokość impulsu jako ułamek okresu (domyślnie 0.15 = 15%)

    Zwraca dict z:
        level, mode, duration_s, sample_rate, pulse_period_s, pulse_duty,
        total_samples, preview (10 próbek), stats (mean, max, duty_cycle)
    """
    assert 0.0 <= level <= 1.0, "level musi być w zakresie [0.0, 1.0]"
    assert mode in MODES,       f"tryb musi być jednym z {MODES}"
    assert duration_s > 0,      "duration_s musi być > 0"
    assert sample_rate > 0,     "sample_rate musi być > 0"
    assert pulse_period_s > 0,  "pulse_period_s musi być > 0"
    assert 0.0 < pulse_duty < 1.0, "pulse_duty musi być w zakresie (0, 1)"

    total_samples = int(duration_s * sample_rate)
    dt            = 1.0 / sample_rate

    # Generuj wszystkie próbki
    samples = [
        round(_sample(i * dt, mode, level, pulse_period_s, pulse_duty), 5)
        for i in range(total_samples)
    ]

    # Preview: 10 równomiernie rozłożonych próbek z całego okresu
    if total_samples >= 10:
        step    = total_samples // 10
        preview = [samples[i * step] for i in range(10)]
    else:
        preview = samples

    # Statystyki
    mean_val   = sum(samples) / len(samples) if samples else 0.0
    max_val    = max(samples)  if samples else 0.0
    active     = sum(1 for s in samples if s > 0)
    duty_cycle = active / total_samples if total_samples > 0 else 0.0

    return {
        "level":          level,
        "mode":           mode,
        "duration_s":     duration_s,
        "sample_rate":    sample_rate,
        "pulse_period_s": pulse_period_s,
        "pulse_duty":     pulse_duty,
        "total_samples":  total_samples,
        "preview":        [round(v, 4) for v in preview],
        "stats": {
            "mean":       round(mean_val, 4),
            "max":        round(max_val, 4),
            "duty_cycle": round(duty_cycle, 4),
        },
    }
