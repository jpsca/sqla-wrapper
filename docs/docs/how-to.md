# How to ...?

In this section you can find how to do some common database tasks using SQLAlchemy and SQLA-wrapper. Is not a complete reference of what you can do with SQLAlchemy so you should read the official [SQLAlchemy tutorial](https://docs.sqlalchemy.org/en/14/tutorial/) to have a better understanding of it.

All examples assume that an SQLAlchemy instance has been created and stored in a global variable named `db`.


## Declaring models

`db` provides a `db.Model` class to be used as a declarative base class for your models.

```python
from sqlalchemy import Column, Integer, String
from myapp.models import db

class User(db.Model):
    id = Column(Integer, primary_key=True)
    name = Column(String(128))
```

`db` also includes all the functions and classes from `sqlalchemy` and `sqlalchemy.orm` so you don't need to import `Column`, `Integer`, `String`, etc. and can do this instead:

```python
from myapp.models import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128))
```

To learn more about how to define database models, consult the [SQLAlchemy ORM documentation](https://docs.sqlalchemy.org/en/14/orm/index.html).


## Inserting records

Inserting data into the database is a three step process:

1. Create the Python object
1. Add it to the session
1. Commit the session

```python
from myapp.models import User, db


```


## Working with background jobs

Use the global scoped session `db.s`. A new session will be created automatically for the thread running the background job so there is no risk of conflict.

However, you must remember to call `db.s.remove()` at the end to remove the scoped session.

```python
from ..models import db, MyModel

def background_job(obj_id):
  # Manipulate the data directly
  obj = db.s.get(MyModel, obj_id)
  obj.lorem = "ipsum"
  db.s.commit()

  # ... or call other code that also uses
  # the scoped session
  ...

  # Always remove the scoped session at the end
  db.s.remove()
```
