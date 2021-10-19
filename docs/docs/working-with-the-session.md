# Working with the session

The Session is the mean to communicate with the database.
There are two main ways to use it:


## Use the scoped session `db.s`

The "scoped_session" is really a proxy to a  session automatically scoped to the current thread.

This allows having a global session, so the session can be shared without the need to pass it explicitly.

A scoped session is the recommended way to work in a web application, however, you must remember to call `db.s.remove()` the session at the end of the request.

 Use your framework's "on request end" hook, to do that. For example, in Flask:

```python
@app.teardown_request
def remove_db_scoped_session(error=None):
    db.s.remove()
```

The `db.s.remove()` method close the current session and dispose it. A new session will be created when `db.s` is called again.


## Instantiate `db.Session`

You can use a context manager:

```python
with db.Session() as dbs:
    # work with the session here
```

When the session is created in this way, a database transaction is automatically initiated when required, and the `dbs.flush()`, `dbs.commit()`, and `dbs.rollback()` methods can be used as needed.

The session is automatically closed and returned to the session pool when the context manager block ends.

You can also create it without a context manager and close it manually:

```python
dbs = db.Session():
# work with the session here
dbs.close()
```

Instantiate `db.Session` is the recommended way to work when the session is not shared like in a  command-line script.


## API

SQLAlchemy default Session class has the method `.get(Model, pk)`
to query and return a record by its primary key.

This class extends the `sqlalchemy.orm.Session` class with some useful
active-record-like methods and a pagination helper.

::: sqla_wrapper.Session
    :members: all create first first_or_create create_or_first paginate

---

As always, I recommend reading the official [SQLAlchemy tutorial](https://docs.sqlalchemy.org/en/14/tutorial/orm_data_manipulation.html#tutorial-orm-data-manipulation) to learn more how to work with the session.
