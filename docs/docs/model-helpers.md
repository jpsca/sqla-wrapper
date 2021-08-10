# Model helpers

The `db.Model` baseclass is a configured with a few ActiveRecord-like utility methods:

```python
class Model:
    @classmethod
    def all(cls, dbs, **attrs):
        """Returns all the object found with these attributes."""

    @classmethod
    def create(cls, dbs, **attrs):
        """Creates a new object and adds it to the session."""

    @classmethod
    def first(cls, dbs, **attrs):
        """Returns the first object found with these attributes."""

    @classmethod
    def first_or_create(cls, dbs, **attrs):
        """Tries to find an object, and if none exists,
        it tries to creates a new one."""

    @classmethod
    def create_or_first(cls, dbs, **attrs):
        """Tries to create a new object, and if it fails
        because already exists, return the first it founds."""

    def update(self, dbs, **attrs):
        """Updates the object with the values of the attrs dict."""

    def delete(self, dbs):
        """Removes the object from the current session."""
```

Note that the first argument for each of these methods is your database session from `sqla_wrapper.SQLAlchemy().session`:

```python hl_lines="4"
from sqla_wrapper import SQLAlchemy

db = SQLAlchemy(DB_URL)
dbs = db.session
```

## Helpers

### `Model.all(dbs, **attrs)`

Returns all the object found with these attributes.
The filtering is done with a simple `.filter_by()` so is limited to the columns of the model.

Examples:

```python
users = User.all(dbs)
users = User.all(dbs, deleted=False)
users = User.all(dbs, account_id=123, deleted=False)
```

### `Model.create(dbs, **attrs)`

Creates a new object and adds it to the session. This is a shortcut for:

```python
obj = Model(**attrs)
dbs.add(obj)
dbs.flush()
```

Note that it doesn't do a `dbs.commit()`, you must do it in your call to persist the object

Examples:

```python
User.create(n)
```

### `Model.first(dbs, **attrs)`

Returns the first object found with these attributes.

Examples:

```python
```

### `Model.first_or_create(dbs, **attrs)`

Tries to find an object, and if none exists, it tries to creates a new one.

Examples:

```python
```

### `Model.create_or_first(dbs, **attrs)`

Tries to create a new object, and if it fails because already exists, return the first it founds.

Examples:

```python
```

### `obj.update(dbs, **attrs)`

Updates the object with the values of the attrs dict.

Examples:

```python
```

### `obj.delete(dbs)`

Removes the object from the current session.

