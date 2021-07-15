from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError


class BaseModel:
    __abstract__ = True

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @classmethod
    def all(cls, dbs: Session, **attrs):
        """Returns all the object found with these attributes."""
        return dbs.execute(select(cls).filter_by(**attrs)).scalars().all()

    @classmethod
    def create(cls, dbs: Session, **attrs) -> Any:
        """Create and commits a new record for the model."""
        obj = cls(**attrs)
        dbs.add(obj)
        dbs.flush()
        return obj

    @classmethod
    def first(cls, dbs: Session, **attrs) -> Any:
        """Returns the first object found with these attributes."""
        return dbs.execute(select(cls).filter_by(**attrs)).scalars().first()

    @classmethod
    def first_or_create(cls, dbs: Session, **attrs) -> Any:
        """Tries to find a record, and if none exists
        it tries to creates a new one.
        """
        obj = cls.first(dbs, **attrs)
        if obj:
            return obj
        return cls.create_or_first(dbs, **attrs)

    @classmethod
    def create_or_first(cls, dbs: Session, **attrs) -> Any:
        """Tries to create a new record, and if it fails
        because already exists, return the first it founds.
        """
        try:
            return cls.create(dbs, **attrs)
        except IntegrityError:
            dbs.rollback()
        return cls.first(dbs, **attrs)

    def update(self, dbs, **attrs) -> Any:
        """Updates the record with the contents of the attrs dict
        and flushs."""
        for name in attrs:
            setattr(self, name, attrs[name])
        dbs.flush()
        return self

    def delete(self, dbs) -> None:
        """Removes the object from the current session and flushs."""
        dbs.delete(self)
        dbs.flush()
