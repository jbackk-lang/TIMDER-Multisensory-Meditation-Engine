class LightEngine:
    """
    Silnik światła TIMDER:
    - pattern: nazwa sekwencji (np. 'τ-soft', 'τ-pulse')
    Zwraca prosty model sekwencji jasności.
    """

    def sequence(self, pattern: str = "τ-soft") -> dict:
        if pattern == "τ-soft":
            seq = [
                {"t": 0.0, "brightness": 0.2},
                {"t": 0.5, "brightness": 0.4},
                {"t": 1.0, "brightness": 0.6},
                {"t": 1.5, "brightness": 0.8},
            ]
        else:
            seq = [
                {"t": 0.0, "brightness": 0.0},
                {"t": 0.25, "brightness": 1.0},
                {"t": 0.5, "brightness": 0.0},
            ]

        return {
            "type": "light",
            "pattern": pattern,
            "sequence": seq,
        }
