# How to ...?

In this section you can find how to do some common database tasks using SQLAlchemy and SQLA-wrapper. Is not a complete reference of what you can do with SQLAlchemy so you should read the official [SQLAlchemy tutorial](https://docs.sqlalchemy.org/en/14/tutorial/) to have a better understanding of it.

All examples assume that an SQLAlchemy instance has been created and stored in a global variable named `db`.


## Declare models

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


## Insert an object to the database

Inserting data into the database is a three step process:

1. Create the Python object
1. Add it to the session
1. Commit the session

```python
from myapp.models import User, db

me = User(name="Me", login="hello")
db.s.add(me)
db.s.commit()
```

You can also use the [`db.s.create`](working-with-the-session/#api) helper method to merge the first two steps.

```python
from myapp.models import User, db

db.s.create(User, name="Me", login="hello")
db.s.commit()
```


## Get an object by its primary key

The [`db.s.get()`](working-with-the-session/#api) method can be used to retrieve an object by its primary key:

```python
from myapp.models import User, db

user = db.s.get(User, 2)
```


## Get the first object by its attributes

The [`db.s.first()`](working-with-the-session/#api) helper method can be used to retrieve an object by its primary key:

```python
from myapp.models import User, db

user = db.s.first(User, login="hello")
```


## Query the database

First, make a query using `db.select( ... )`, and then execute the query with `db.s.execute( ... )`.

```python
from myapp.models import User, db

users = db.s.execute(
  db.select(User)
  .where(User.email.endswith('@example.com'))
).scalars()

# You can now do `users.all()`, `users.first()`,
# `users.unique()`, etc.
```

The [results](https://docs.sqlalchemy.org/en/14/core/connections.html#sqlalchemy.engine.Result) from `db.s.execute()` are returned as a list of rows, where each row is a tuple, even if only one result per row was requested. The [`scalars()`](https://docs.sqlalchemy.org/en/14/core/connections.html#sqlalchemy.engine.ScalarResult) method conveniently extract the first result in each row.

The `select()` function it is very powerful and can do **a lot** more:
https://docs.sqlalchemy.org/en/14/tutorial/data_select.html#selecting-rows-with-core-or-orm



## Count the number of rows in a query

Like with regular SQL, use the `count` function:

```python
from myapp.models import User, db

num = db.s.execute(
  db.select(db,func.count(User.id))
  .where(User.email.endswith('@example.com'))
).scalar()
```

The `scalar()` method conveniently returns only the first object of the first row.



## Update an object

To update a database object, first retrieve it, modify it, and finally commit the session.

```python
from myapp.models import User, db

user = db.s.first(User, login="hello")
user.name = "me"
db.s.commit()
```


## Delete an object from the database

Deleting objects from the database is very similar to adding new ones, instead of `db.s.add()` use `db.s.delete()`:

```python
from myapp.models import User, db

user = db.s.first(User, login="hello")
db.s.delete(user)
db.s.commit()
```


## Run an arbitrary SQL statement

Use `db.text` to build a query and then run it with `db.s.execute`.

```python
from myapp.models import db

sql = db.text("SELECT * FROM user WHERE user.id = :user_id")
results = db.s.execute(sql, params={"user_id": 5}).all()
```

Parameters are specified by name, always using the format `:name`, no matter the database engine.

Is important to use `db.text()` instead of plain strings so the parameters are escaped protecting you from SQL injection attacks.


## Work with background jobs/tasks

1. Call `db.engine.dispose()` when each new process is created.
2. Call `db.s.remove()` at the end of each job/task

Background jobs libraries, like Celery or RQ, use multiprocessing or `fork()`, to have several "workers" to run these jobs. When that happens, the pool of connections to the database is copied to the child processes, which does causes errors.

For that reason you should call `db.engine.dispose()` when each worker process is created, so that the engine creates brand new database connections local to that fork.

You also must remember to call `db.s.remove()` at the end of each job, so a new session is used each time.

### RQ

RQ actually uses a `fork()` for *each* job. The best way to make sure you make the required cleanup is to use a custom `Worker` class:

```python
# foo/bar.py
import rq
from myapp.models import db

class Worker(rq.Worker):
    def perform_job(self, job, queue):
        db.engine.dispose()
        rv = super().perform_job(job, queue)
        db.s.remove()
        return rv

```

You can then use that custom class by starting the workers with the `--worker-class` argument:

```bash
rq worker --worker-class 'foo.bar.Worker'
```

### Celery

Use signals to register functions to run when the worker is ready and when each job/task finish.

```python
from celery.signals import task_postrun, worker_process_init
from myapp.models import db

@worker_process_init
def refresh_db_connections(*args, **kwargs):
    db.engine.dispose()

@task_postrun
def remove_db_scoped_session(*args, **kwargs):
    db.s.remove()

```
