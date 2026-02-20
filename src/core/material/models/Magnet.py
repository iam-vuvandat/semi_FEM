class Magnet:
    def __init__(self, name: str):
        self.name = name
        if name == "N30UH":
            self.relative_permeance = 1.05
            self.coercivity = 852000.0
        elif name == "NdFe30":
            self.relative_permeance = 1.0445730167132
            self.coercivity = 838000.0
        else:
            raise ValueError(f"Magnet '{name}' not found")