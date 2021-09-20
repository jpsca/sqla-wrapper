# Working with the session

The Session is the mean to communicate with the database.
There are two main ways to use it:

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

Instantiate `db.Session` is the recommended way to work with command-line script or background jobs: create a Session local to each child process, work with that Session through the life of the “job”, and finally tear it down when the job is completed.

## Use the scoped session `db.s`

The "scoped_session" is really a registry that automatically generates a session scoped to the current thread.

This allows separated sections of the application to call upon a global scoped_session, so that those sections may share the same session without the need to pass it explicitly

This is the recommended way to work in a web application, however, you must remember to call `db.s.remove()` the session at the end of the request.

 Use your framework's "on request end" hook, to do that. For example, in Flask:

```python
@app.teardown_request
def remove_db_scoped_session(error=None):
    db.s.remove()
```

The `db.s.remove()` method close the current session and dispose it. A new session will be created when `db.s` is called again. For consitency, you can explicitly do it using your framework's "on request start" hook. For example, in Flask:

```python
@app.before_request
def init_db_scoped_session():
    db.s()
```

## Extensions

SQLAlchemy default Session has the method `dbs.get(Model, pk)` to query and return a record by its primary key.

SQLA-wrapper extends it with a few other ActiveRecord-like methods:

### `Session.all(Model, **attrs)`

Returns all the object found with these attributes.

The filtering is done with a simple `.filter_by()` so is limited to the columns of the model and basic filters. Also, there is no way to sort the results. If you need sorting or more complex filtering, you are better served using a `db.select()`.

Examples:

```python
users = dbs.all(User)
users = dbs.all(User, deleted=False)
users = dbs.all(User, account_id=123, deleted=False)
```

### `Session.create(Model, **attrs)`

Creates a new object and adds it to the session. This is a shortcut for:

```python
obj = Model(**attrs)
dbs.add(obj)
dbs.flush()
```

Note that this does a `dbs.flush()`, so you must later call `dbs.commit()` to persist the new object, You must later call `dbs.commit()` to persist the new object.

Examples:

```python
new_user = dbs.create(User, email='foo@example.com')
dbs.commit()
```

### `Session.first(Model, **attrs)`

Returns the first object found with these attributes or `None` if there isn't one.

Examples:

```python
user = dbs.first(User)
user = dbs.first(User, deleted=False)
```

### `Session.first_or_create(Model, **attrs)`

Tries to find an object and if none exists, it tries to creates a new one first. Use this method when you expect the object to already exists but want to create it in case it doesn't.

This does a `dbs.flush()`, so you must later call `dbs.commit()` to persist the new object (in case one has been created).

Examples:

```python
user1 = dbs.first_or_create(User, email='foo@example.com')
user2 = dbs.first_or_create(User, email='foo@example.com')
user1 is user2
```

### `Session.create_or_first(Model, **attrs)`

Tries to create a new object, and if it fails because already exists, return the first it founds. For this to work one or more of the attributes must be unique so it does fail, otherwise you will be creating a new different object.

Use this method when you expect that the object does not exists but want to avoid an exception in case it does.

This does a `dbs.flush()`, so you must later call `dbs.commit()` to persist the new object (in case one has been created).

Examples:

```python
user1 = dbs.create_or_first(User, email='foo@example.com')
user2 = dbs.create_or_first(User, email='foo@example.com')
user1 is user2
```

---

As always, I recommend reading the official [SQLAlchemy tutorial](https://docs.sqlalchemy.org/en/14/tutorial/orm_data_manipulation.html#tutorial-orm-data-manipulation) to learn more how to work with the session.
