# SQLAlchemy wrapper

The `SQLAlchemy` wrapper class is a *light* wrapper over regular SQLAlchemy, mainly to simplify the configuration.

A `SQLAlchemy` instance gives you access to the following things:

- `db.engine`: An engine created with the `future=True` argument
- A scoped session `db.s` and a `db.Session` class to manually create one, both extended with some useful active-record-like methods. (See ["Working with the session"](working-with-the-session).)
- `db.Model`: A declarative base class
- `db.create_all()` and `db.drop_all()` methods to create and drop tables according to the models.
- `db.test_transaction()`: A helper for performant testing with a real database. (See ["Testing with a real database"](testing-with-a-real-database).)


## Set up

The only required argument is the connection URI. You can give it directly:

```python
from sqla_wrapper import SQLAlchemy

db = SQLAlchemy("postgresql://scott:tiger@localhost/test")
```

or as separated host, user, password, database name, etc. parameters, and SQLA-Wrapper will build the URI for you.

```python
from sqla_wrapper import SQLAlchemy

db = SQLAlchemy(
    dialect="postgresql",
    user="scott",
    password="tiger",
    host="localhost",
    name="test",
)
```

 After the setup, you will be interacting mostly directly with SQLAlchemy so I recommend reading the official [SQLAlchemy tutorial](https://docs.sqlalchemy.org/en/14/tutorial/index.html) if you haven't done it yet.

Beyond the URI, the class also accepts an `engine_options` and a `session_options` dictionary to pass special options when creating the engine and/or the session.


## Declaring models

A `SQLAlchemy` instance provides a `db.Model` class to be used as a declarative base class for your models.

```python
from sqlalchemy import Column, Integer, String
from .base import db

class User(db.Model):
    id = Column(Integer, primary_key=True)
    name = Column(String(128))
```

The instance also includes all the functions and classes from `sqlalchemy` and `sqlalchemy.orm` so you don't need to import `Column`, `Integer`, `String`, etc. and do this instead:

```python
from .base import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128))
```

To learn more about how to define database models, consult the [SQLAlchemy ORM documentation](https://docs.sqlalchemy.org/en/14/orm/index.html).


## API

::: sqla_wrapper.SQLAlchemy
    :members:
