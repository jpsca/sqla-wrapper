from typing import Any

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError


def get_base_model(dbs: Any) -> Any:  # noqa: 13
    class BaseModel:
        __abstract__ = True

        def __init__(self, **kwargs):
            super().__init__(**kwargs)

        @classmethod
        def all(cls, **attrs):
            """Returns all the object found with these attributes."""
            return dbs.execute(select(cls).filter_by(**attrs)).scalars().all()

        @classmethod
        def create(cls, **attrs) -> Any:
            """Create and commits a new record for the model."""
            obj = cls(**attrs)
            dbs.add(obj)
            dbs.commit()
            return obj

        @classmethod
        def first(cls, **attrs) -> Any:
            """Returns the first object found with these attributes."""
            return dbs.execute(select(cls).filter_by(**attrs)).scalars().first()

        @classmethod
        def first_or_create(cls, **attrs) -> Any:
            """Tries to find a record, and if none exists
            it tries to creates a new one.
            """
            obj = cls.first(**attrs)
            if obj:
                return obj
            return cls.create_or_first(**attrs)

        @classmethod
        def create_or_first(cls, **attrs) -> Any:
            """Tries to create a new record, and if it fails
            because already exists, return the first it founds.
            """
            try:
                return cls.create(**attrs)
            except IntegrityError:
                dbs.rollback()
                return cls.first(**attrs)

        def update(self, **attrs) -> Any:
            """Updates the record with the contents of the attrs dict
            and commits."""
            for name in attrs:
                setattr(self, name, attrs[name])
            dbs.commit()
            return self

        def delete(self) -> None:
            """Removes the object from the current session and commits."""
            dbs.delete(self)
            dbs.commit()

    return BaseModel
