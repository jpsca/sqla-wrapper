# SQLA-wrapper

A friendly wrapper for [SQLAlchemy v2](https://docs.sqlalchemy.org/en/14/glossary.html#term-2.0-style) (v1.4 or later)

Includes:

- A `SQLAlchemy` wrapper, that does all the SQLAlchemy setup and gives you:
    - A preconfigured scoped session.
    - A model baseclass including some helper methods.
    - A helper for performant testing with a real database

- An `Alembic` wrapper that loads the config from your application instead of an ini file.

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
    __tablename__ = "users"
    id = sa.Column(sa.Integer, primary_key=True)
    login = sa.Column(sa.String(80), unique=True)
    password = sa.Column(sa.String(80))
    deleted = sa.Column(sa.DateTime)

db.create_all()
dbs = db.session

users = dbs.execute(
    sa.select(User)
    .where(deleted == None)
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
- `db.session`: A preconfigured scoped session
- `db.Model`: A baseclass that is a configured declarative base with a few extra methods (see below)
- `db.registry`: A registry instance
- `db.create_all()` and `db.drop_all()` methods to create and drop tables according to the models.

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
    def first_or_create(cls, **attrs):
        """Tries to find a record, and if none exists
        it tries to creates a new one."""

    @classmethod
    def create_or_first(cls, **attrs):
        """Tries to create a new record, and if it fails
        because already exists, return the first it founds."""

    def update(self, **attrs):
        """Updates the record with the contents of the attrs dict
        and commits."""

    def delete(self):
        """Removes the model from the current session and commits."""
```

## sa module

This library includes a `sa` module from which you can import any of the functions or classes from `sqlalchemy` and `sqlalchemy.orm`.

Instead of doing:

```python
from sqlalchemy import Column, DateTime, ForeignKey, String, select
from sqlalchemy.orm import relationship
from .base import Base, dbs

class Tag(Base):
    __tablename__ = "tags"
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
    __tablename__ = "tags"
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
