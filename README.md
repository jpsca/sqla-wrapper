# SQLA-wrapper [![Build Status](https://travis-ci.org/jpscaletti/sqla-wrapper.png)](https://travis-ci.org/jpscaletti/sqla-wrapper)

A friendly wrapper for SQLAlchemy.


## Installation

Install the package using Pypi:

```bash
pip install sqla-wrapper
```

There is another package on Pypi called `SQLAlchemy-Wrapper` which is
deprecated (do not use it\!). Use `sqla-wrapper` instead.


## Basic usage

```python
from sqla_wrapper import SQLAlchemy

db = SQLAlchemy('sqlite:///:memory:')

class ToDo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ...

db.create_all()

db.add(Todo(...))
db.commit()

# Sorry, we don't support the `Model.query` syntax yet
todos = db.query(ToDo).all()
```

Read the complete documentation here: https://jpscaletti.com/sqla-wrapper

Since 2.0, only Python 3.6 or later are supported. Please use the 1.9.1 version if your project runs on a previous Python version.

Our test suite [runs continuously on Travis CI](https://travis-ci.org/jpscaletti/sqla-wrapper) with every update.


## SQLAlchemy

The things you need to know compared to plain SQLAlchemy are:

1.  The `SQLAlchemy` gives you access to the following things:
      - All the functions and classes from `sqlalchemy` and
        `sqlalchemy.orm`
      - All the functions from a preconfigured scoped session (called
        `_session`).
      - The `~SQLAlchemy.metadata` and `~SQLAlchemy.engine`
      - The methods `SQLAlchemy.create_all` and `SQLAlchemy.drop_all` to
        create and drop tables according to the models.
      - a `Model` baseclass that is a configured declarative base.
2.  All the functions from the session are available directly in the
    class, so you can do `db.add`, `db.commit`, `db.remove`, etc.
3.  The `Model` declarative base class behaves like a regular Python
    class but has a `query` attribute attached that can be used to query
    the model.
4.  The `Model` class also auto generates `_tablename__` attributes, if
    you don't define one, based on the underscored and **pluralized**
    name of your classes.
5.  You have to commit the session and configure your app to remove it
    at the end of the request.

---

Copyright 2013 by [Juan-Pablo Scaletti](http://jpscaletti.com).

