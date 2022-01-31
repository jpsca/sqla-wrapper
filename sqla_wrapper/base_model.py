from typing import Any

from sqlalchemy import inspect


__all__ = ("BaseModel", )


class BaseModel:
    def fill(self, **attrs) -> Any:
        """Fill the object with the values of the attrs dict."""
        for name in attrs:
            setattr(self, name, attrs[name])
        return self

    def __repr__(self) -> str:
        output = ["<", self.__class__.__name__, f" #{id(self)}"]
        for attr in self._iter_attrs():
            output.append(f"\n {self._repr_attr(attr)}")
        output.append(">")
        return "".join(output)

    def _iter_attrs(self):
        names = inspect(self.__class__).columns.keys()
        for name in names:
            yield (name, getattr(self, name))

    def _repr_attr(self, attr):
        name, value = attr
        if hasattr(value, "isoformat"):
            value = value.isoformat()
        else:
            value = repr(value)
        return f"{name} = {value}"
