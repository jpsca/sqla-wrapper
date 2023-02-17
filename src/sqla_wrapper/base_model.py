import typing as t

from sqlalchemy import inspect


__all__ = ("BaseModel", )


class BaseModel:
    def fill(self, **attrs: t.Any) -> t.Any:
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

    def _iter_attrs(self) -> t.Generator:
        inspection = inspect(self.__class__)
        if inspection is None:
            raise StopIteration
        names = inspection.columns.keys()
        for name in names:
            yield (name, getattr(self, name))

    def _repr_attr(self, attr: t.Any) -> str:
        name, value = attr
        if hasattr(value, "isoformat"):
            value = value.isoformat()
        else:
            value = repr(value)
        return f"{name} = {value}"
