---
template: home.html
---

SQLA-Wrapper is a wrapper for SQLAlchemy and Alembic that simplifies many aspects of its setup.

It works with the [newer 2.0 style query API introduced in SQLAlchemy 1.4](https://docs.sqlalchemy.org/en/14/glossary.html#term-2.0-style), and can be used with most web frameworks.

## Includes

- A [`SQLAlchemy` wrapper](/sqlalchemy-wrapper), that does all the SQLAlchemy setup and gives you:
    - A preconfigured scoped session.
    - A model baseclass including some helper methods.
    - A helper for performant testing with a real database

- An [`Alembic` wrapper](/alembic-wrapper) that loads the config from your application instead of from a separated ini file.

- A [`sa` shortcut module](/sa-shortcut-module), that imports all the functions and classes from `sqlalchemy`and `sqlalchemy.orm`,
so you don't need to repeat those imports everywhere.


## Example

The next example creates a SQLite database and an `Alembic` object for migrations. Then, declares a `users` table, inserts an user, and finally prints the users to the console.

```python
from sqlalchemy import *
from sqla_wrapper import Alembic, SQLAlchemy

db = SQLAlchemy("sqlite:///db.sqlite")
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

dbs.add(User(login="scott", password="tiger"))
dbs.commit()

users = dbs.execute(
    select(User).where(deleted == None)
).scalars().all()
# Or: users = User.all(dbs)

print(users)
```

## Installation

Install the package using `pip`. The `SQLAlchemy` and `Alembic` libraries will be installed as dependencies.

```bash
pip install sqla-wrapper
```

## Resources

- [Source code (MIT Licensed)](https://github.com/jpsca/sqla-wrapper)
- [PyPI](https://pypi.org/project/sqla-wrapper/)
- [Change log](https://github.com/jpsca/sqla-wrapper/releases)
