import inflection
import sqlalchemy as sa
from sqlalchemy.ext.declarative import DeclarativeMeta, declared_attr
from sqlalchemy.schema import _get_table_key


class NameMeta:
    def __init__(cls, name, bases, dic):
        if should_set_tablename(cls):
            cls.__tablename__ = get_table_name(cls.__name__)

        super().__init__(name, bases, dic)

        # __table_cls__ has run at this point
        # if no table was created, use the parent table
        if (
            "__tablename__" not in cls.__dict__
            and "__table__" in cls.__dict__
            and cls.__dict__["__table__"] is None
        ):
            del cls.__table__

    def __table_cls__(cls, *args, **kwargs):
        """This is called by SQLAlchemy during mapper setup. It determines the
        final table object that the model will use.

        If no primary key is found, that indicates single-table inheritance,
        so no table will be created and ``__tablename__`` will be unset.
        """
        # check if a table with this name already exists
        # allows reflected tables to be applied to model by name
        key = _get_table_key(args[0], kwargs.get("schema"))

        if key in cls.metadata.tables:
            return sa.Table(*args, **kwargs)

        # if a primary key or constraint is found, create a table for
        # joined-table inheritance
        for arg in args:
            if (isinstance(arg, sa.Column) and arg.primary_key) or isinstance(
                arg, sa.PrimaryKeyConstraint
            ):
                return sa.Table(*args, **kwargs)

        # if no base classes define a table, return one
        # ensures the correct error shows up when missing a primary key
        for base in cls.__mro__[1:-1]:
            if "__table__" in base.__dict__:
                break
        else:
            return sa.Table(*args, **kwargs)

        # single-table inheritance, use the parent tablename
        if "__tablename__" in cls.__dict__:
            del cls.__tablename__


class DefaultMeta(NameMeta, DeclarativeMeta):
    pass


def should_set_tablename(cls):
    """Determine whether ``__tablename__`` should be automatically generated
    for a model.

    - If no class in the MRO sets a name, one should be generated.
    - If a declared attr is found, it should be used instead.
    - If a name is found, it should be used if the class is a mixin, otherwise
      one should be generated.
    - Abstract models should not have one generated.

    Later, `__table_cls__()` will determine if the model looks like single or
    joined-table inheritance.
    If no primary key is found, the name will be unset.
    """
    if cls.__dict__.get("__abstract__", False) or not any(
        isinstance(b, DeclarativeMeta) for b in cls.__mro__[1:]
    ):
        return False

    for base in cls.__mro__:
        if "__tablename__" not in base.__dict__:
            continue

        if isinstance(base.__dict__["__tablename__"], declared_attr):
            return False

        return not (
            base is cls
            or base.__dict__.get("__abstract__", False)
            or not isinstance(base, DeclarativeMeta)
        )
    return True


def get_table_name(class_name):
    """Generates a table name based on a pluralized and underscored
    class name.
    >>> get_table_name('Document')
    'documents'
    >>> get_table_name('ToDo')
    'to_dos'
    >>> get_table_name('UserTestCase')
    'user_test_cases'
    >>> get_table_name('URL')
    'urls'
    >>> get_table_name('HTTPRequest')
    'http_requests'
    """
    return inflection.pluralize(inflection.underscore(class_name))
