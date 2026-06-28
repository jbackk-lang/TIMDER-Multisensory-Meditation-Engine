# FLOW.md — TIMDER-FLOW · Specyfikacja strumienia

Dokument opisuje strukturę, kolejność i reguły łączenia strumienia **TIMDER-FLOW** — jednolitego multisensorycznego wyjścia silnika TMME.

---

## 1. Czym jest TIMDER-FLOW

TIMDER-FLOW to zsynchronizowany strumień pięciu kanałów sensorycznych produkowany przez `integrator.py`. Każdy kanał odpowiada jednej warstwie protokołu TIMDER:

| Kanał | Silnik | Warstwa TIMDER | Opis |
|---|---|---|---|
| `rhythm` | `rhythm_engine` | skręt | rytm uderzeń, modulacja velocity |
| `color`  | `color_engine`  | Λ (struktura) | paleta barw psycho-geometrycznych |
| `light`  | `light_engine`  | τ (transformacja) | sekwencja jasności |
| `image`  | `image_engine`  | ρ (defekt) | geometria fraktala |
| `signal` | `signal_engine` | J-klucz | sygnał synchronizacji |

---

## 2. Kolejność generowania

```
RhythmEngine → ColorEngine → LightEngine → ImageEngine → SignalEngine → Integrator
```

Kolejność jest deterministyczna — te same parametry wejściowe zawsze produkują ten sam strumień.

---

## 3. Struktura wyjściowa `flow()`

```python
{
  "flow_name":  str,        # nazwa sesji
  "duration_s": float,      # czas trwania w sekundach
  "channels": {
    "rhythm":  { ... },     # wyjście rhythm_engine.generate_rhythm()
    "color":   { ... },     # wyjście color_engine.generate_palette()
    "light":   { ... },     # wyjście light_engine.generate_light_sequence()
    "image":   { ... },     # wyjście image_engine.generate_fractal()
    "signal":  { ... },     # wyjście signal_engine.generate_pulse()
  },
  "sync_check": {
    "rhythm_ok":  bool,
    "color_ok":   bool,
    "light_ok":   bool,
    "image_ok":   bool,
    "signal_ok":  bool,
  }
}
```

`sync_check` weryfikuje czy każdy kanał zwrócił oczekiwane klucze. Jeśli któryś kanał zwrócił pusty wynik, odpowiednia flaga będzie `False`.

---

## 4. Parametry sesji

### Sesja relaksacyjna (domyślna)
```python
flow(
    rhythm = generate_rhythm(bpm=60,  pattern="skręt",   duration_s=60),
    color  = generate_palette("Λ-relax"),
    light  = generate_light_sequence("τ-soft",  duration_s=60),
    image  = generate_fractal("ρ-smooth",  size=256, render=False),
    signal = generate_pulse(level=0.8, mode="wave",   duration_s=60),
    name   = "TIMDER-FLOW-relax",
    duration_s = 60.0,
)
```

### Sesja fokusowa
```python
flow(
    rhythm = generate_rhythm(bpm=72,  pattern="skręt",   duration_s=60),
    color  = generate_palette("Λ-focus"),
    light  = generate_light_sequence("τ-pulse", duration_s=60),
    image  = generate_fractal("ρ-rough",   size=256, render=False),
    signal = generate_pulse(level=1.0, mode="pulse",  duration_s=60),
    name   = "TIMDER-FLOW-focus",
    duration_s = 60.0,
)
```

### Sesja minimalna
```python
flow(
    rhythm = generate_rhythm(bpm=48,  pattern="skręt",   duration_s=300),
    color  = generate_palette("Λ-relax"),
    light  = generate_light_sequence("τ-steady", duration_s=300),
    image  = generate_fractal("ρ-minimal", size=64,  render=False),
    signal = generate_pulse(level=0.5, mode="stable", duration_s=300),
    name   = "TIMDER-FLOW-minimal",
    duration_s = 300.0,
)
```

---

## 5. Reguły synchronizacji

- `duration_s` powinno być identyczne we wszystkich kanałach i w wywołaniu `flow()`.
- `rhythm.bpm` i `signal.pulse_period_s` powinny być harmonicznie powiązane:  
  `pulse_period_s = 60 / bpm` daje synchronizację "jeden sygnał na uderzenie".
- `light.fps` i `signal.sample_rate` mogą być niezależne — integrator nie wymusza ich równości.

---

## 6. Rozszerzanie strumienia

TMME jest neutralny technologicznie. Strumień TIMDER-FLOW można podpiąć do:

- **DAW (MIDI)** — `rhythm` → nuta MIDI, `signal` → CC
- **LED** — `light.brightness` → PWM, `color.colors_hex` → RGB
- **VR/AR** — `image.pixel_data` → tekstura, `color` → skybox
- **OSC** — wszystkie kanały → pakiety OSC do dowolnej aplikacji
- **Terapia** — `light` → lampka biurkowa, `rhythm` → metronom

---

## 7. Przykład end-to-end

```python
from core.rhythm_engine import generate_rhythm
from core.color_engine  import generate_palette
from core.light_engine  import generate_light_sequence
from core.image_engine  import generate_fractal
from core.signal_engine import generate_pulse
from core.integrator    import flow

result = flow(
    rhythm = generate_rhythm(60, "skręt", 60),
    color  = generate_palette("Λ-relax"),
    light  = generate_light_sequence("τ-soft", duration_s=60),
    image  = generate_fractal("ρ-smooth", size=128, render=True, save_path="frame.png"),
    signal = generate_pulse(1.0, "wave", 60, 100),
    name   = "moja-sesja",
    duration_s = 60.0,
)

print(result["flow_name"])        # moja-sesja
print(result["sync_check"])       # wszystkie True
print(result["channels"]["image"]["saved_to"])  # frame.png
```
