import inflection
from sqlalchemy.orm import declarative_mixin, declared_attr


@declarative_mixin
class TablenameMixin:
    @declared_attr
    def __tablename__(cls):
        if not should_set_tablename(cls):
            del cls.__tablename__
            return None
        return get_table_name(cls.__name__)


def should_set_tablename(cls):
    """Determine whether ``__tablename__`` should be automatically generated
    for a model.
    """
    for base in cls.__mro__:
        if "__tablename__" not in base.__dict__:
            continue
        return not (base is cls or base.__dict__.get("__abstract__", False))
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
