# SQLA-wrapper [![Build Status](https://travis-ci.org/jpsca/sqla-wrapper.png)](https://travis-ci.org/jpsca/sqla-wrapper) [![Coverage Status](https://coveralls.io/repos/github/jpsca/sqla-wrapper/badge.svg?branch=master)](https://coveralls.io/github/jpsca/sqla-wrapper?branch=master)

A friendly wrapper for SQLAlchemy.

## Why?

SQLAlchemy is great, but can be difficult to set up. With SQLA-Wrapper you can quickly start like:

```python
from sqla_wrapper import SQLAlchemy

db = SQLAlchemy('sqlite:///:memory:')

class User(db.Model):
    __tablename__ "users"
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
    __tablename__ "users"
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
    __tablename__ "users"
    id = db.Column(db.Integer, primary_key=True)
    ...

db.create_all()

db.add(User(...))
db.commit()

todos = db.query(User).all()
```

## Compared to SQLAlchemy

Compared to plain SQLAlchemy, you need to know that:

The `SQLAlchemy` gives you access to the following things:

- All the functions and classes from `sqlalchemy` and `sqlalchemy.orm`
- All the functions from a preconfigured scoped session (called `_session`).
- The `~SQLAlchemy.metadata` and `~SQLAlchemy.engine`
- The methods `SQLAlchemy.create_all` and `SQLAlchemy.drop_all` to create and drop tables according to the models.
- A `Model` baseclass that is a configured declarative base. This model has a few utility methods:

```python
class Model(Object):
    @classmethod
    def exists(cls, **attrs):
        """Returns whether an object with these attributes exists."""

    @classmethod
    def create(cls, **attrs):
        """Create and persist a new record for the model."""

    @classmethod
    def create_or_first(cls, **attrs):
        """Tries to create a new record, and if it fails
        because already exists, return the first it founds."""

    @classmethod
    def first(cls, **attrs):
        """Returns the first object found with these attributes."""
    
    def save(self):
        """Saves the updated model to the current entity db and commits."""

    def delete(self):
        """Removes the model from the current session and commits."""
```

This model class also generates a default __repr__ for your models, based on their class names an primary keys.
