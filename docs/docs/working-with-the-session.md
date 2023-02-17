# Working with the session

The Session is the mean that you use to communicate with the database.
There are two main ways to use it:

## In a web application: Use the scoped session `db.s`

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

### Background job/tasks

Outside a web request cycle, like in a background job, you still can use the global session, but you must:

1. Call `db.engine.dispose()` when each new process is created.
2. Call `db.s.remove()` at the end of each job/task

Background jobs libraries, like Celery or RQ, use multiprocessing or `fork()`, to have several "workers" to run these jobs. When that happens, the pool of connections to the database is copied to the child processes, which does causes errors.

For that reason you should call `db.engine.dispose()` when each worker process is created, so that the engine creates brand new database connections local to that fork.

You also must remember to call `db.s.remove()` at the end of each job, so a new session is used each time.

With most background jobs libraries you can set them so it's done automatically, see:

- [Working with RQ](how-to/#rq)
- [Working with Celery](how-to/#celery)


## In a standalone script: Instantiate `db.Session`

Instantiating `db.Session` is the recommended way to work when the session is not shared like in a command-line script.

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


## API

::: sqla_wrapper.Session
    options:
        heading_level: 3
        members:
            - get
            - all
            - create
            - first
            - first_or_create
            - create_or_first

---

As always, I recommend reading the official [SQLAlchemy tutorial](https://docs.sqlalchemy.org/en/20/tutorial/orm_data_manipulation.html#tutorial-orm-data-manipulation) to learn more how to work with the session.
