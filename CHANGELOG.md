# Changelog

## v4 (TBR)

- Added a `Model.query()` class method. Now you can do `User.query().filter_by(name="bob)` in addition to `db.query(User).filter_by(name="bob)`. Even though the `Model.query` is more limited, it can be used for many of the simpler queries.

- Added four ActiveRecord-inspired class methods to the base Model:

    - `exists(**attrs)`
        Returns whether an object with these attributes exists.
    - `create(**attrs)`
        Create and persist a new record for the model, and returns it.
    - `create_or_first(**attrs)`
        Tries to create a new record, and if it fails, because already exists, return the first it founds.
    - `first(**attrs)`
        Returns the first object found with these attributes.

- Added two new methods to the base Model:

    - `save()`
        Adds the updated object to the current session and commits.
    - `delete()`
        Removes the object from the current session and commits.

- Now the base Model class generates a smart default __repr__ based on the class name and the primary key(s).

- Removes the paginator because it was outside of the scope of the package.
