class ImageEngine:
    """
    Silnik obrazu TIMDER:
    - mode: typ defektu (np. 'ρ-smooth', 'ρ-fractal')
    Zwraca opis geometryczny jako model (nie obraz).
    """

    def fractal(self, mode: str = "ρ-smooth") -> dict:
        return {
            "type": "image",
            "mode": mode,
            "geometry": {
                "base_shape": "spiral",
                "iterations": 4 if mode == "ρ-smooth" else 8,
                "symmetry": "radial",
            },
        }
