from typing import Any


__all__ = ("BaseModel", )


class BaseModel:
    def fill(self, **attrs) -> Any:
        """Fill the object with the values of the attrs dict."""
        for name in attrs:
            setattr(self, name, attrs[name])
        return self
