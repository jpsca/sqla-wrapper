---
template: home.html
---
# SQLA-Wrapper

SQLA-Wrapper is a wrapper for SQLAlchemy and Alembic that simplifies many aspects of its setup.

It works with the [newer 2.0 style query API introduced in SQLAlchemy 1.4](https://docs.sqlalchemy.org/en/14/glossary.html#term-2.0-style), and can be used with most web frameworks.

## Includes

- A [SQLAlchemy wrapper](sqlalchemy-wrapper), that does all the SQLAlchemy setup and gives you:
    - A session class to instance and a scoped_session, both extended with some useful active-record-like methods.
    - A declarative base class
    - A helper for performant testing with a real database

    ```python
    from sqla_wrapper import SQLAlchemy

    db = SQLAlchemy("sqlite:///db.sqlite", **options)
    # You can also use separated host, name, etc.
    # db = SQLAlchemy(user=…, password=…, host=…, port=…, name=…)
    ```

- An [Alembic wrapper](alembic-wrapper) that loads the config from your application instead of from separated `alembic.ini` and `env.py` files.

    ```python
    from sqla_wrapper import Alembic, SQLAlchemy

    db = SQLAlchemy(…)
    alembic = Alembic(db, "db/migrations")
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
