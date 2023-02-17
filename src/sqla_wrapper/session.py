import typing as t

import sqlalchemy.orm
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import scoped_session


__all__ = ("Session",)


class Session(sqlalchemy.orm.Session):
    """SQLAlchemy default Session class has the method `.get(Model, pk)`
    to query and return a record by its primary key.

    This class extends the `sqlalchemy.orm.Session` class with some useful
    active-record-like methods.
    """

    def all(self, Model: t.Any, **attrs) -> t.Sequence[t.Any]:
        """Returns all the object found with these attributes.

        The filtering is done with a simple `.filter_by()` so is limited
        to “equality” comparisons against the columns of the model.
        Also, there is no way to sort the results. If you need sorting or
        more complex filtering, you are better served using a `db.select()`.

        **Examples**:

        ```python
        users = db.s.all(User)
        users = db.s.all(User, deleted=False)
        users = db.s.all(User, account_id=123, deleted=False)
        ```
        """
        return self.execute(select(Model).filter_by(**attrs)).scalars().all()

    def create(self, Model: t.Any, **attrs: t.Any) -> t.Any:
        """Creates a new object and adds it to the session.

        This is a shortcut for:

        ```python
        obj = Model(**attrs)
        db.s.add(obj)
        db.s.flush()
        ```

        Note that this does a `db.s.flush()`, so you must later call
        `db.s.commit()` to persist the new object.

        **Example**:

        ```python
        new_user = db.s.create(User, email='foo@example.com')
        db.s.commit()
        ```
        """
        obj = Model(**attrs)
        self.add(obj)
        self.flush()
        return obj

    def first(self, Model: t.Any, **attrs: t.Any) -> t.Any:
        """Returns the first object found with these attributes or `None`
        if there isn't one.

        The filtering is done with a simple `.filter_by()` so is limited
        to “equality” comparisons against the columns of the model.
        Also, there is no way to sort the results. If you need sorting or
        more complex filtering, you are better served using a `db.select()`.

        **Examples**:

        ```python
        user = db.s.first(User)
        user = db.s.first(User, deleted=False)
        ```
        """
        return self.execute(
            select(Model).filter_by(**attrs).limit(1)
        ).scalars().first()

    def first_or_create(self, Model: t.Any, **attrs) -> t.Any:
        """Tries to find an object and if none exists, it tries to create
        a new one first. Use this method when you expect the object to
        already exists but want to create it in case it doesn't.

        This does a `db.s.flush()`, so you must later call `db.s.commit()`
        to persist the new object (in case one has been created).

        **Examples**:

        ```python
        user1 = db.s.first_or_create(User, email='foo@example.com')
        user2 = db.s.first_or_create(User, email='foo@example.com')
        user1 is user2
        ```
        """
        obj = self.first(Model, **attrs)
        if obj:
            return obj
        return self.create_or_first(Model, **attrs)

    def create_or_first(self, Model: t.Any, **attrs: t.Any) -> t.Any:
        """Tries to create a new object, and if it fails because already exists,
        return the first it founds. For this to work one or more of the
        attributes must be unique so it does fail, otherwise you will be creating
        a new different object.

        Use this method when you expect that the object does not exists but want
        to avoid an exception in case it does.

        This does a `db.s.flush()`, so you must later call `db.s.commit()`
        to persist the new object (in case one has been created).

        **Examples**:

        ```python
        user1 = db.s.create_or_first(User, email='foo@example.com')
        user2 = db.s.create_or_first(User, email='foo@example.com')
        user1 is user2
        ```
        """
        try:
            return self.create(Model, **attrs)
        except IntegrityError:
            self.rollback()
        return self.first(Model, **attrs)


class PatchedScopedSession(scoped_session):
    def all(self, Model: t.Any, **attrs) -> t.List[t.Any]:
        return self.registry().all(Model, **attrs)

    def create(self, Model: t.Any, **attrs) -> t.Any:
        return self.registry().create(Model, **attrs)

    def first(self, Model: t.Any, **attrs) -> t.Any:
        return self.registry().first(Model, **attrs)

    def first_or_create(self, Model: t.Any, **attrs) -> t.Any:
        return self.registry().first_or_create(Model, **attrs)

    def create_or_first(self, Model: t.Any, **attrs) -> t.Any:
        return self.registry().create_or_first(Model, **attrs)
