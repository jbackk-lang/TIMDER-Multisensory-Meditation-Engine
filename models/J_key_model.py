class JKeyModel:
    """
    Model klucza J.
    """

    def __init__(self, level: int = 1, mode: str = "relax"):
        self.level = level
        self.mode = mode

    def as_dict(self) -> dict:
        return {
            "level": self.level,
            "mode": self.mode,
        }
