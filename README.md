**NOTE**: [SQLalchemy v2.0](https://docs.sqlalchemy.org/en/14/glossary.html#term-2.0-style) [SQLalchemy v2.0](https://docs.sqlalchemy.org/en/14/glossary.html#term-2.0-style) will be a significant shift for a wide variety of important SQLAlchemy usage patterns in both the Core and ORM components.

As a consequence, version 5 is no longer compatible with previous versions and requires SQLAlchemy 1.4 (the first one compatible with the new changes) or later

----

# SQLA-wrapper

A friendly wrapper for SQLAlchemy.

Included:

- A `SQLAlchemy` class, that does all the SQLAlchemy setup and gives you:
    - A preconfigured scoped session.
    - A model baseclass with helper methods, that also cam auto-fill the `__tablename__` attribute for you.
- A `Paginator` helper class, for simple pagination of query results (using `offset` and `limit`,) or any iterable.
- A `sa` helper module, that imports all the functions and classes from `sqlalchemy`and `sqlalchemy.orm`,
so you don't need to repeat those imports everywhere.


### Why?

SQLAlchemy is great, but can be difficult to set up. With SQLA-Wrapper you can quickly start like:

```python
from sqla_wrapper import SQLAlchemy, sa

db = SQLAlchemy("sqlite:///:memory:")
# You can also use separated host, name, etc.
# db = SQLAlchemy(user=…, password=…, host=…, port=…, name=…)

class Base(db.Model):
    pass

class User(Base):
    id = sa.Column(sa.Integer, primary_key=True)
    …

db.create_all()
dbs = db.session

users = dbs.execute(
    sa.select(User)
    .where(deleted == False)
).scalars().all()
```


### Installation

Install the package using Pypi:

```bash
pip install sqla-wrapper
```


## SQLAlchemy class

Compared to plain SQLAlchemy, the `SQLAlchemy` class gives you access to the following things:

- `db.engine`: An engine created with the `future=True` argument
- `db.registry`: A registry instance
- `db.Model`: A baseclass that is a configured declarative base with a few extra methods (see below)
- `db.create_all()` and `db.drop_all()` methods to create and drop tables according to the models.
- `db.session`: A preconfigured scoped session

### Using it in a web application

In a web application or a multithreaded environment you need to call `db.session.remove()` when a request/thread ends. Use your framework's `on_teardown` hook (whatever the name), to do that. For example, in `Flask`:

```python
@app.teardown_appcontext
def remove_db_session(response=None):
    db.remove()
    return response
```

### Model baseclass

The `Model` baseclass is a configured with a few ActiveRecord-like utility methods:

```python
class Model:
    @classmethod
    def all(cls, **attrs):
        """Returns all the object found with these attributes."""

    @classmethod
    def create(cls, **attrs):
        """Create and commits a new record for the model."""

    @classmethod
    def first(cls, **attrs):
        """Returns the first object found with these attributes."""

    @classmethod
    def create_or_first(cls, **attrs):
        """Tries to create a new record, and if it fails
        because already exists, return the first it founds."""

    @classmethod
<<<<<<< HEAD
    def first(cls, **attrs):
        """Returns the first object found with these attributes."""

    def save(self):
        """Saves the updated model to the current entity db and commits."""
=======
    def first_or_create(cls, **attrs):
        """Tries to find a record, and if none exists
        it tries to creates a new one."""

    def update(self, **attrs):
        """Updates the record with the contents of the attrs dict
        and commits."""
>>>>>>> 3169e6c (Update README and version)

    def delete(self):
        """Removes the model from the current session and commits."""
```

### Table names

Like always, you can specify a table name in your models using `__tablename__`. But if you don't, the `Model` base class will do it for you pluralizing the class name (thank you to the excellent `inflection` library.)

This also works as expected skipping abstract and/or inherited classes that should not have their own tables.


## Paginator helper class

...


## sa module helper

This library includes a `sa` module that imports all the functions and classes from `sqlalchemy` and `sqlalchemy.orm`,
so you don't need to repeat those imports everywhere.

Instead of doing:

```python
from sqlalchemy import Column, DateTime, ForeignKey, String, select
from sqlalchemy.orm import relationship
from .base import Base, dbs

class Tag(Base):
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False)
    user_id = Column(ForeignKey("users.id"))
    user = relationship("User", back_populates="tags")

    @classmethod
    def get_all(cls):
        return dbs.execute(
            select(cls).order_by(cls.published_at.desc())
        ).scalars().all()
```

You can use:

```python
from .base import Base, dbs, sa

class Tag(Base):
    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String, nullable=False)
    created_at = sa.Column(sa.DateTime, nullable=False)
    user_id = sa.Column(sa.ForeignKey("users.id"))
    user = sa.relationship("User", back_populates="tags")

    @classmethod
    def get_all(cls):
        return dbs.execute(
            sa.select(cls).order_by(cls.published_at.desc())
        ).scalars().all()
```

