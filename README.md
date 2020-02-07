# SQLA-wrapper [![Build Status](https://travis-ci.org/jpscaletti/sqla-wrapper.png)](https://travis-ci.org/jpscaletti/sqla-wrapper)

A friendly wrapper for SQLAlchemy.

Docs: https://jpscaletti.com/sqla-wrapper

## Why?

SQLAlchemy is great can be difficult to set up. With SQLA-Wrapper you can quickly start like:

```python
from sqla_wrapper import SQLAlchemy

db = SQLAlchemy('sqlite:///:memory:')

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ...

db.create_all()
todos = db.query(User.id, User.title).all()
```

*instead* of having to write something like:

```python
# Who's going to remember all of this?
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Column, Integer

engine = create_engine('sqlite:///:memory:')
Session = sessionmaker(bind=engine)
session = Session()
Model = declarative_base()

class User(Model):
    id = Column(Integer, primary_key=True)
    ...

Model.metadata.create_all(engine)
session = Session()
todos = session.query(User).all()
```

## Installation

Install the package using Pypi:

```bash
python -m pip install sqla-wrapper
```


## Basic usage

```python
from sqla_wrapper import SQLAlchemy

db = SQLAlchemy('sqlite:///:memory:')

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ...

db.create_all()

db.add(User(...))
db.commit()

todos = db.query(User).all()
```

**NOTE: The `Model.query()` syntax of Flask-SQLAlchemy is a bad practice and thus is NOT supported. Use `db.query(Model)` instead.**. 


## Compared to SQLAlchemy

Compared to plain SQLAlchemy, you need to know that:

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
