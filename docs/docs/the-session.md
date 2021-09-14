# The Session


## Extensions

A `db.Session` is a configured with a few ActiveRecord-like extensions:

### `Session.all(**attrs)`

Returns all the object found with these attributes.
The filtering is done with a simple `.filter_by()` so is limited to the columns of the model.

Examples:

```python
users = User.all(dbs)
users = User.all(deleted=False)
users = User.all(account_id=123, deleted=False)
```

### `Session.create(**attrs)`

Creates a new object and adds it to the session. This is a shortcut for:

```python
obj = Session(**attrs)
dbs.add(obj)
dbs.flush()
```

Note that it doesn't do a `dbs.commit()`, you must do it in your call to persist the object

Examples:

```python
User.create(n)
```

### `Session.first(**attrs)`

Returns the first object found with these attributes.

Examples:

```python
```

### `Session.first_or_create(**attrs)`

Tries to find an object, and if none exists, it tries to creates a new one.

Examples:

```python
```

### `Session.create_or_first(**attrs)`

Tries to create a new object, and if it fails because already exists, return the first it founds.

Examples:

```python
```


## Web applications
