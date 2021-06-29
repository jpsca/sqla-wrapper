from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import declarative_mixin


def get_active_record_mixin(dbs):  # noqa: C901
    @declarative_mixin
    class ActiveRecordMixin:
        @classmethod
        def all(cls, **attrs):
            """Returns all the object found with these attributes."""
            return dbs.execute(select(cls).filter_by(**attrs)).scalars().all()

        @classmethod
        def create(cls, **attrs):
            """Create and commits a new record for the model."""
            obj = cls(**attrs)
            dbs.add(obj)
            dbs.commit()
            return obj

        @classmethod
        def first(cls, **attrs):
            """Returns the first object found with these attributes."""
            return dbs.execute(select(cls).filter_by(**attrs)).scalars().first()

        @classmethod
        def first_or_create(cls, **attrs):
            """Tries to find a record, and if none exists
            it tries to creates a new one.
            """
            obj = cls.first(**attrs)
            if obj:
                return obj
            return cls.create_or_first(**attrs)

        @classmethod
        def create_or_first(cls, **attrs):
            """Tries to create a new record, and if it fails
            because already exists, return the first it founds.
            """
            try:
                return cls.create(**attrs)
            except IntegrityError:
                dbs.rollback()
                return cls.first(**attrs)

        def update(self, **attrs):
            """Updates the record with the contents of the attrs dict
            and commits."""
            for name in attrs:
                setattr(self, name, attrs[name])
            dbs.commit()
            return self

        def delete(self):
            """Removes the object from the current session and commits."""
            dbs.delete(self)
            dbs.commit()

    return ActiveRecordMixin
