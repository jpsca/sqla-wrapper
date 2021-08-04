# SQLA-Wrapper

A friendly wrapper for [modern SQLAlchemy](https://docs.sqlalchemy.org/en/14/glossary.html#term-2.0-style) and Alembic.

Includes:

- A `SQLAlchemy` wrapper, that does all the SQLAlchemy setup and gives you:
    - A preconfigured scoped session.
    - A model baseclass including some helper methods.
    - A helper for performant testing with a real database

- An `Alembic` wrapper that loads the config from your application instead of an ini file.

- A `sa` helper module, that imports all the functions and classes from `sqlalchemy`and `sqlalchemy.orm`,
so you don't need to repeat those imports everywhere.


## Why?

SQLAlchemy is great, but can be difficult to set up. With SQLA-Wrapper you can quickly start like:

```python
from sqlalchemy import *
from sqla_wrapper import Alembic, SQLAlchemy

db = SQLAlchemy("sqlite:///:memory:")
# You can also use separated host, name, etc.
# db = SQLAlchemy(user=…, password=…, host=…, port=…, name=…)

alembic = Alembic(db, "db/migrations")


class Base(db.Model):
    pass

class User(Base):
    __tablename__ = "users"
    id = sa.Column(Integer, primary_key=True)
    login = Column(String(80), unique=True)
    password = Column(String(80))
    deleted = Column(DateTime)

db.create_all()
dbs = db.session

users = dbs.execute(
    select(User).where(deleted == None)
).scalars().all()
# Or: users = User.all(dbs)
```


## Installation

Install the package using Pypi:

```bash
pip install sqla-wrapper
```


## Resources

- [Source code](https://github.com/jpsca/sqla-wrapper)
- [PyPI](https://pypi.org/project/sqla-wrapper/)
- [Change log](https://github.com/jpsca/sqla-wrapper/releases)

