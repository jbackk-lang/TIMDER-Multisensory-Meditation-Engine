# API.md — TIMDER Multisensory Meditation Engine · Dokumentacja API

---

## Moduły `core/`

### `rhythm_engine.generate_rhythm()`

```python
generate_rhythm(
    bpm:        float = 60.0,
    pattern:    str   = "skręt",
    duration_s: float = 60.0,
) -> dict
```

**Parametry**

| Nazwa | Typ | Opis |
|---|---|---|
| `bpm` | float > 0 | Tempo uderzeń na minutę |
| `pattern` | str | Identyfikator wzorca (np. `"skręt"`) |
| `duration_s` | float > 0 | Długość sekwencji w sekundach |

**Zwraca**

```python
{
  "bpm":        float,
  "pattern":    str,
  "duration_s": float,
  "beat_count": int,
  "beats": [
    { "time": float, "velocity": float, "pattern": str },
    ...
  ]
}
```

`velocity` ∈ [0.2, 1.0] — modulacja sinusoidalna co 4 uderzenia.

---

### `color_engine.generate_palette()`

```python
generate_palette(preset: str = "Λ-relax") -> dict
```

**Presety**

| Preset | Zastosowanie |
|---|---|
| `"Λ-relax"` | Sesja relaksacyjna — odcienie teal/zielone |
| `"Λ-focus"` | Sesja fokusowa — niebieskofioletowe |
| `"Λ-energy"` | Aktywacja — ciepłe czerwono-żółte |

**Zwraca**

```python
{
  "preset":      str,
  "colors_hsl":  list[tuple[int,int,int]],  # (H, S, L)
  "colors_hex":  list[str],                 # "#rrggbb"
}
```

---

### `light_engine.generate_light_sequence()`

```python
generate_light_sequence(
    preset:     str   = "τ-soft",
    duration_s: float = 60.0,
    fps:        float = 30.0,
) -> dict
```

**Presety**

| Preset | Freq [Hz] | Jasność min–max |
|---|---|---|
| `"τ-soft"`   | 0.1 | 0.30 – 0.80 |
| `"τ-pulse"`  | 0.5 | 0.10 – 1.00 |
| `"τ-steady"` | 0.0 | 0.70 – 0.70 |

**Zwraca**

```python
{
  "preset":       str,
  "duration_s":   float,
  "total_frames": int,
  "preview":      list[dict],  # 3 pierwsze klatki
}
```

Każda klatka: `{ "time": float, "brightness": float ∈ [0,1] }`.

---

### `image_engine.generate_fractal()` ← poprawiony v2

```python
generate_fractal(
    preset:    str        = "ρ-smooth",
    size:      int        = 128,
    render:    bool       = True,
    save_path: str | None = None,
) -> dict
```

**Presety**

| Preset | Tryb | Iteracje | Defekt ρ | Kolorystyka |
|---|---|---|---|---|
| `"ρ-smooth"`  | Mandelbrot | 64  | 0.10 | teal   |
| `"ρ-rough"`   | Mandelbrot | 128 | 0.50 | amber  |
| `"ρ-minimal"` | Mandelbrot | 32  | 0.02 | gray   |
| `"ρ-julia"`   | Julia      | 96  | 0.25 | purple |

**Parametry**

| Nazwa | Opis |
|---|---|
| `size` | Rozmiar obrazu (size × size px), max 1024 |
| `render` | `True` = liczy piksele (wolniej); `False` = tylko metadane |
| `save_path` | Ścieżka PNG do zapisu (tylko gdy `render=True`) |

**Zwraca**

```python
{
  "preset":        str,
  "size":          str,          # "128x128"
  "pixels":        int,
  "active_pixels": int,
  "defect_ratio":  float,
  "iterations":    int,
  "mode":          str,          # "mandelbrot" | "julia"
  "colormap":      str,
  "rendered":      bool,
  "pixel_data":    list | None,  # list[list[int]] RGB wiersze, gdy render=True
  "saved_to":      str | None,   # ścieżka PNG jeśli zapisano
}
```

**Ważne**: bez zewnętrznych bibliotek — używa tylko stdlib (`math`, `struct`, `zlib`).

---

### `signal_engine.generate_pulse()` ← poprawiony v2

```python
generate_pulse(
    level:          float = 1.0,
    mode:           str   = "stable",
    duration_s:     float = 60.0,
    sample_rate:    float = 100.0,
    pulse_period_s: float = 0.5,
    pulse_duty:     float = 0.15,
) -> dict
```

**Tryby**

| Tryb | Opis |
|---|---|
| `"stable"` | Stały sygnał = `level` |
| `"pulse"`  | Prostokąt: aktywny przez `pulse_duty × pulse_period_s`, potem 0 |
| `"wave"`   | Sinus: amplituda `level`, okres `pulse_period_s` |
| `"burst"`  | 3 impulsy po 20ms co `pulse_period_s` |
| `"sweep"`  | Trójkąt: narastanie + opadanie w `pulse_period_s` |
| `"off"`    | Zawsze 0 |

**Parametry**

| Nazwa | Opis |
|---|---|
| `level` | Poziom bazowy [0.0, 1.0] |
| `pulse_period_s` | Okres impulsu/fali w sekundach (domyślnie 0.5s = 2 Hz) |
| `pulse_duty` | Szerokość impulsu jako ułamek okresu (domyślnie 0.15 = 15%) |

**Zwraca**

```python
{
  "level":          float,
  "mode":           str,
  "duration_s":     float,
  "sample_rate":    float,
  "pulse_period_s": float,
  "pulse_duty":     float,
  "total_samples":  int,
  "preview":        list[float],  # 10 próbek równomiernie z całego sygnału
  "stats": {
    "mean":       float,
    "max":        float,
    "duty_cycle": float,          # ułamek czasu gdy sygnał > 0
  }
}
```

**Poprawka v2**: `preview` zawiera 10 próbek równomiernie rozłożonych, a nie pierwsze 10. Tryb `pulse` działa poprawnie przy dowolnym `sample_rate`.

---

### `integrator.flow()`

```python
flow(
    rhythm,
    color,
    light,
    image,
    signal,
    name:       str   = "TIMDER-FLOW",
    duration_s: float = 60.0,
) -> dict
```

Scala wyniki wszystkich pięciu silników w strumień TIMDER-FLOW.

**Zwraca**

```python
{
  "flow_name":  str,
  "duration_s": float,
  "channels":   dict,   # klucze: rhythm, color, light, image, signal
  "sync_check": dict,   # klucze: rhythm_ok, color_ok, light_ok, image_ok, signal_ok
}
```

---

## Modele `models/`

### `skręt_model.SkrewModel`

```python
@dataclass
class SkrewModel:
    intensity:     float   # 0.0 – 1.0
    smoothness:    float   # 0.0 – 1.0
    direction:     str     # "left" | "right"
    frequency_hz:  float   # > 0
```

Metody: `validate()`, `to_dict()`.

---

### `LTR_model.LTRModel`

```python
@dataclass
class LTRModel:
    lambda_val: float   # Λ ∈ [0, 1] — struktura
    tau_val:    float   # τ ∈ [0, 1] — transformacja
    rho_val:    float   # ρ ∈ [0, 1] — defekt
```

Metody: `validate()`, `state_vector()`, `to_dict()`.

---

### `J_key_model.JKeyModel`

```python
@dataclass
class JKeyModel:
    level: float   # 0.0 – 1.0
    mode:  str     # "stable" | "pulse" | "wave" | "off"
```

Metody: `validate()`, `to_dict()`.

---

### `flow_model.FlowModel`

```python
@dataclass
class FlowModel:
    name:       str
    duration_s: float
    bpm:        float
    channels:   list[str]
    meta:       dict
```

Metody: `validate()`, `to_dict()`.

---

## Zmiany wersji

### v2 (aktualna)
- `image_engine`: faktyczny rendering fraktala (Mandelbrot + Julia) do pikseli RGB, zapis PNG bez zewnętrznych bibliotek
- `image_engine`: nowy preset `"ρ-julia"`
- `image_engine`: parametr `render=True/False` — opcjonalny rendering
- `signal_engine`: tryb `"pulse"` poprawiony — działa przy dowolnym `sample_rate`
- `signal_engine`: nowe tryby `"burst"` i `"sweep"`
- `signal_engine`: `preview` to 10 równomiernych próbek z całego sygnału
- `signal_engine`: parametry `pulse_period_s` i `pulse_duty`

### v1 (poprzednia)
- `image_engine`: tylko metadane, brak renderowania pikseli
- `signal_engine`: tryb `"pulse"` nie działał przy sample_rate < 50
