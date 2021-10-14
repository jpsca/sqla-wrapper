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


## Extensions

SQLAlchemy default Session has the method `db.s.get(Model, pk)` to query and return a record by its primary key.

SQLA-wrapper extends it with a few other ActiveRecord-like methods:

### `Session.all(Model, **attrs)`

Returns all the object found with these attributes.

The filtering is done with a simple `.filter_by()` so is limited to the columns of the model and basic filters. Also, there is no way to sort the results. If you need sorting or more complex filtering, you are better served using a `db.select()`.

Examples:

```python
users = db.s.all(User)
users = db.s.all(User, deleted=False)
users = db.s.all(User, account_id=123, deleted=False)
```

### `Session.create(Model, **attrs)`

Creates a new object and adds it to the session. This is a shortcut for:

```python
obj = Model(**attrs)
db.s.add(obj)
db.s.flush()
```

Note that this does a `db.s.flush()`, so you must later call `db.s.commit()` to persist the new object, You must later call `db.s.commit()` to persist the new object.

Examples:

```python
new_user = db.s.create(User, email='foo@example.com')
db.s.commit()
```

### `Session.first(Model, **attrs)`

Returns the first object found with these attributes or `None` if there isn't one.

Examples:

```python
user = db.s.first(User)
user = db.s.first(User, deleted=False)
```

### `Session.first_or_create(Model, **attrs)`

Tries to find an object and if none exists, it tries to creates a new one first. Use this method when you expect the object to already exists but want to create it in case it doesn't.

This does a `db.s.flush()`, so you must later call `db.s.commit()` to persist the new object (in case one has been created).

Examples:

```python
user1 = db.s.first_or_create(User, email='foo@example.com')
user2 = db.s.first_or_create(User, email='foo@example.com')
user1 is user2
```

### `Session.create_or_first(Model, **attrs)`

Tries to create a new object, and if it fails because already exists, return the first it founds. For this to work one or more of the attributes must be unique so it does fail, otherwise you will be creating a new different object.

Use this method when you expect that the object does not exists but want to avoid an exception in case it does.

This does a `db.s.flush()`, so you must later call `db.s.commit()` to persist the new object (in case one has been created).

Examples:

```python
user1 = db.s.create_or_first(User, email='foo@example.com')
user2 = db.s.create_or_first(User, email='foo@example.com')
user1 is user2
```

---

As always, I recommend reading the official [SQLAlchemy tutorial](https://docs.sqlalchemy.org/en/14/tutorial/orm_data_manipulation.html#tutorial-orm-data-manipulation) to learn more how to work with the session.
