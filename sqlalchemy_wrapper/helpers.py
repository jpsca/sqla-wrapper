# coding=utf-8
from operator import itemgetter
import sys
import threading
import time

import inflection
import sqlalchemy
from sqlalchemy.event import listen
from sqlalchemy.orm import Query

from .paginator import Paginator


# the best timer function for the platform
if sys.platform == 'win32':
    _timer = time.clock
else:
    _timer = time.time

try:
    from flask import _app_ctx_stack as connection_stack
except ImportError:
    connection_stack = None


def _tablemaker(db):
    def make_sa_table(*args, **kwargs):
        if len(args) > 1 and isinstance(args[1], db.Column):
            args = (args[0], db.metadata) + args[1:]
        return sqlalchemy.Table(*args, **kwargs)

    return make_sa_table


def _include_sqlalchemy(db):
    for module in sqlalchemy, sqlalchemy.orm:
        for key in module.__all__:
            if not hasattr(db, key):
                setattr(db, key, getattr(module, key))
    db.Table = _tablemaker(db)
    db.event = sqlalchemy.event


def _get_table_name(classname):
    return inflection.pluralize(inflection.underscore(classname))


class BaseQuery(Query):
    """The default query object used for models. This can be subclassed and
    replaced for individual models by setting the :attr:`~SQLAlchemy.query_cls`
    attribute.

    This is a subclass of a standard SQLAlchemy
    :class:`~sqlalchemy.orm.query.Query` class and has all the methods of a
    standard query as well.
    """

    def get_or_error(self, uid, error):
        """Like :meth:`get` but raises an error if not found instead of
        returning `None`.
        """
        rv = self.get(uid)
        if rv is None:
            if isinstance(error, Exception):
                raise error
            return error()
        return rv

    def first_or_error(self, error):
        """Like :meth:`first` but raises an error if not found instead of
        returning `None`.
        """
        rv = self.first()
        if rv is None:
            if isinstance(error, Exception):
                raise error
            return error()
        return rv

    def paginate(self, **kwargs):
        """Paginate this results.

        Returns an :class:`Paginator` object.
        """
        return Paginator(self, **kwargs)


class ModelTableNameDescriptor(object):

    def __get__(self, obj, type):
        tablename = type.__dict__.get('__tablename__')
        if not tablename:
            tablename = _get_table_name(type.__name__)
            setattr(type, '__tablename__', tablename)
        return tablename


class EngineConnector(object):

    def __init__(self, sqla):
        self._sqla = sqla
        self._engine = None
        self._connected_for = None
        self._lock = threading.Lock()

    def get_engine(self):
        with self._lock:
            uri = self._sqla.uri
            info = self._sqla.info
            options = self._sqla.options
            echo = options.get('echo')
            if (uri, echo) == self._connected_for:
                return self._engine
            self._engine = engine = sqlalchemy.create_engine(info, **options)
            self._connected_for = (uri, echo)

            if connection_stack and self._sqla.record_queries:
                EngineDebug(self._engine, self._sqla).register()
            return engine


class Model(object):
    """Baseclass for custom user models.
    """

    __tablename__ = ModelTableNameDescriptor()

    def __iter__(self):
        """Returns an iterable that supports .next()
        so we can do dict(sa_instance).
        """
        for k in self.__dict__.keys():
            if not k.startswith('_'):
                yield (k, getattr(self, k))

    def __repr__(self):
        return '<%s>' % self.__class__.__name__


class DebugQueryTuple(tuple):
    statement = property(itemgetter(0))
    parameters = property(itemgetter(1))
    start_time = property(itemgetter(2))
    end_time = property(itemgetter(3))
    context = property(itemgetter(4))

    @property
    def duration(self):
        return self.end_time - self.start_time

    def __repr__(self):
        return '<query statement="%s" parameters=%r duration=%.03f>' % (
            self.statement,
            self.parameters,
            self.duration
        )


def _frame_context(frm):
    return '{filename}:{lineno} ({blueprint})'.format(
        filename=frm.f_code.co_filename,
        lineno=frm.f_lineno,
        blueprint=frm.f_code.co_name
    )


def _calling_context(app_path):
    frm = sys._getframe(1)
    frames = [frm]
    while frm.f_back is not None:
        if frm.f_code.co_filename.startswith(app_path):
            return _frame_context(frm)
        frm = frm.f_back
        frames.append(frm)

    # The call was made from a library?
    for frm in frames:
        filepath = frm.f_code.co_filename
        if '/sqlalchemy/' not in filepath:
            if '/sqlalchemy-wrapper/' not in filepath:
                return _frame_context(frm)

    return '<unknown>'


class EngineDebug(object):
    """Sets up handlers for two events that let us track the execution time of queries."""

    def __init__(self, engine, sqla):
        self.engine = engine
        self.sqla = sqla

    def register(self):
        listen(self.engine, 'before_cursor_execute', self.before_cursor_execute)
        listen(self.engine, 'after_cursor_execute', self.after_cursor_execute)

    def before_cursor_execute(self, conn, cursor, statement,
                              parameters, context, executemany):
        if connection_stack.top is not None:
            context._query_start_time = _timer()

    def after_cursor_execute(self, conn, cursor, statement,
                             parameters, context, executemany):
        ctx = connection_stack.top
        if ctx is not None:
            queries = getattr(ctx, 'sqlalchemy_queries', None)
            if queries is None:
                queries = []
                setattr(ctx, 'sqlalchemy_queries', queries)
            debug_query = (
                statement, parameters, context._query_start_time,
                _timer(), _calling_context(self.sqla.app_path)
            )
            queries.append(DebugQueryTuple(debug_query))


def get_debug_queries():
    """
    Return a list of named tuples with the following attributes:

    :statement:
        The SQL statement issued
    :parameters:
        The parameters for the SQL statement
    :start_time:
    :end_time:
        Time the query started / the results arrived.  Please keep in mind
        that the timer function used depends on your platform. These
        values are only useful for sorting or comparing.  They do not
        necessarily represent an absolute timestamp.
    :duration:
        Time the query took in seconds
    :context:
        A string giving a rough estimation of where in your application
        query was issued.  The exact format is undefined so don't try
        to reconstruct filename or function name.
    """
    return getattr(connection_stack.top, 'sqlalchemy_queries', [])
