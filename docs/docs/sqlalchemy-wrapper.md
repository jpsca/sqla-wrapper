# SQLAlchemy wrapper class

Compared to plain SQLAlchemy, the `SQLAlchemy` wrapper class gives you access to the following things:

- `db.engine`: An engine created with the `future=True` argument
- `db.Session`: A session class to instance, extended with some useful active-record-like methods
- `db.Model`: A declarative base class
- `db.create_all()` and `db.drop_all()` methods to create and drop tables according to the models.
