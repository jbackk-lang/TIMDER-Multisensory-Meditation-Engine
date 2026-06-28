class ColorEngine:
    """
    Silnik kolorów TIMDER:
    - mode: tryb (np. 'Λ-relax', 'Λ-focus')
    Zwraca paletę kolorów jako model do dalszej pracy.
    """

    def palette(self, mode: str = "Λ-relax") -> dict:
        if mode == "Λ-relax":
            colors = ["#1E90FF", "#32CD32", "#9370DB", "#FFFFFF"]
        else:
            colors = ["#FF4500", "#FFD700", "#00FFFF", "#000000"]

        return {
            "type": "color",
            "mode": mode,
            "palette": colors,
        }
