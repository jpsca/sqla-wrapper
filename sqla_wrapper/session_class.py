from typing import Any, List

import sqlalchemy.orm
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError


class Session(sqlalchemy.orm.Session):
    def all(self, Model: Any, **attrs) -> List[Any]:
        """Returns all the object found with these attributes."""
        return self.execute(
            select(Model).filter_by(**attrs)
        ).scalars().all()

    def create(self, Model: Any, **attrs) -> Any:
        """Creates a new object and adds it to the session."""
        obj = Model(**attrs)
        self.add(obj)
        self.flush()
        return obj

    def first(self, Model: Any, **attrs) -> Any:
        """Returns the first object found with these attributes."""
        return self.execute(
            select(Model).filter_by(**attrs)
        ).scalars().first()

    def first_or_create(self, Model: Any, **attrs) -> Any:
        """Tries to find an object, and if none exists
        it tries to creates a new one."""
        obj = self.first(Model, **attrs)
        if obj:
            return obj
        return self.create_or_first(Model, **attrs)

    def create_or_first(self, Model: Any, **attrs) -> Any:
        """Tries to create a new object, and if it fails
        because already exists, return the first it founds."""
        try:
            return self.create(Model, **attrs)
        except IntegrityError:
            self.rollback()
        return self.first(Model, **attrs)
