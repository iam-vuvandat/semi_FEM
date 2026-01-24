from dataclasses import dataclass

@dataclass
class Container:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __repr__(self):
        items = (f"{k}={v!r}" for k, v in self.__dict__.items())
        return f"Storage({', '.join(items)})"