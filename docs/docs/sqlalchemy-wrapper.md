# SQLAlchemy wrapper class

Compared to plain SQLAlchemy, the `SQLAlchemy` wrapper class gives you access to the following things:

- `db.engine`: An engine created with the `future=True` argument
- `db.session`: A preconfigured scoped session
- `db.Model`: A baseclass that is a configured declarative base with a few extra methods (see below)
- `db.registry`: A registry instance
- `db.create_all()` and `db.drop_all()` methods to create and drop tables according to the models.

## Web applications

In a web application or a multithreaded environment you need to call `db.session.remove()` when a request/thread ends.

Use your framework's `on_teardown` hook (whatever the name), to do that. For example, in `Flask`:

```python
@app.teardown_appcontext
def remove_db_session(response=None):
    db.remove()
    return response
```
