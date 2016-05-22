# coding=utf-8
import threading

try:
    from sqlalchemy.engine.url import make_url
    from sqlalchemy.ext.declarative import declarative_base
    from sqlalchemy.orm import scoped_session, sessionmaker
    from sqlalchemy.schema import MetaData
except ImportError:  # pragma: no cover
    raise ImportError(
        'Unable to load the sqlalchemy package.'
        ' `SQLAlchemy-Wrapper` needs the SQLAlchemy library to run.'
        ' You can get download it from http://www.sqlalchemy.org/'
        ' If you\'ve already installed SQLAlchemy, then make sure you have '
        ' it in your PYTHONPATH.')

from .helpers import (
    _include_sqlalchemy, BaseQuery, Model, EngineConnector,
    _BoundDeclarativeMeta, connection_stack, get_debug_queries)


class SQLAlchemy(object):

    """This class is used to instantiate a SQLAlchemy connection to
    a database.

    .. sourcecode:: python

        db = SQLAlchemy(_uri_to_database_)

    The class also provides access to all the SQLAlchemy
    functions from the :mod:`sqlalchemy` and :mod:`sqlalchemy.orm` modules.
    So you can declare models like this:

    .. sourcecode:: python

        class User(db.Model):
            login = db.Column(db.String(80), unique=True)
            passw_hash = db.Column(db.String(80))

    In a web application or a multithreaded environment you need to
    call ``db.session.remove()`` after each response,
    and ``db.session.rollback()`` if an error occurs.

    However, there's no need to do it if your application object has an
    ``after_request`` and ``on_exception`` hooks, just pass your
    application object at creation:

    .. sourcecode:: python

        app = Flask(__name__)
        db = SQLAlchemy('sqlite://', app=app)

    or later:

    .. sourcecode:: python

        db = SQLAlchemy()

        app = Flask(__name__)
        db.init_app(app)

    .. admonition:: Check types carefully

       Don't perform type or ``isinstance`` checks against ``db.Table``, which
       emulates ``Table`` behavior but is not a class. ``db.Table`` exposes the
       ``Table`` interface, but is a function which allows omission of metadata.

    """

    def __init__(self, uri='sqlite://', app=None, echo=False,
                 pool_size=None, pool_timeout=None, pool_recycle=None,
                 convert_unicode=True, isolation_level=None,
                 record_queries=False, metadata=None,
                 query_cls=BaseQuery, model_class=Model, **session_options):
        self.uri = uri
        self.record_queries = record_queries
        self.info = make_url(uri)
        self.options = self._cleanup_options(
            echo=echo,
            pool_size=pool_size,
            pool_timeout=pool_timeout,
            pool_recycle=pool_recycle,
            convert_unicode=convert_unicode,
            isolation_level=isolation_level,
        )

        self.connector = None
        self._engine_lock = threading.Lock()

        session_options.setdefault('autoflush', True)
        session_options.setdefault('autocommit', False)
        session_options.setdefault('query_cls', query_cls)
        session_options.setdefault('bind', self.engine)
        self.session = self._create_scoped_session(**session_options)

        self.Model = self.make_declarative_base(model_class, metadata)
        self.Model.db = self
        self.Model.query = self.session.query

        self.app_path = ''
        if app is not None:
            self.init_app(app)

        _include_sqlalchemy(self)

        if connection_stack and record_queries:
            monkeypatch_flask_debugtoolbar()

    def _cleanup_options(self, **kwargs):
        options = dict([
            (key, val)
            for key, val in kwargs.items()
            if val is not None
        ])
        return self.apply_driver_hacks(options)

    def make_declarative_base(self, model_class, metadata=None):
        """Creates the declarative base."""
        return declarative_base(
            cls=model_class, name='Model',
            metadata=metadata, metaclass=_BoundDeclarativeMeta
        )

    def apply_driver_hacks(self, options):
        """This method is called before engine creation and used to inject
        driver specific hacks into the options.

        The options parameter is a dictionary of keyword arguments that will
        then be used to call the :mod:`sqlalchemy.create_engine()` function.

        The default implementation provides some saner defaults for things
        like pool sizes for MySQL and sqlite.
        """
        if self.info.drivername == 'mysql':
            self.info.query.setdefault('charset', 'utf8')
            options.setdefault('pool_size', 10)
            options.setdefault('pool_recycle', 7200)

        elif self.info.drivername == 'sqlite':
            no_pool = options.get('pool_size') == 0
            memory_based = self.info.database in (None, '', ':memory:')
            if memory_based and no_pool:
                raise ValueError(
                    'SQLite in-memory database with an empty queue'
                    ' (pool_size = 0) is not possible due to data loss.'
                )
        return options

    def _create_scoped_session(self, **kwargs):
        session = sessionmaker(**kwargs)
        return scoped_session(session)

    def init_app(self, app):
        """In a web application or a multithreaded environment you need to
        call ``db.session.remove()`` after each response,
        and ``db.session.rollback()`` if an error occurs.

        This callback can be used to setup the application's ``after_request``
        and ``on_exception`` hooks to do that automatically.

        Flask, Bottle and webpy are supported. Other frameworks might also
        apply if their hook syntax are the same.
        """
        self.app_path = getattr(app, 'root_path', '')
        if not hasattr(app, 'databases'):
            app.databases = []
        if isinstance(app.databases, list):
            if self in app.databases:
                return
            app.databases.append(self)

        def shutdown(response=None):
            self.session.remove()
            return response

        def rollback(error=None):
            try:
                self.session.rollback()
            except Exception:
                pass

        self.set_flask_hooks(app, shutdown, rollback)
        self.set_bottle_hooks(app, shutdown, rollback)
        self.set_webpy_hooks(app, shutdown, rollback)

    def set_flask_hooks(self, app, shutdown, rollback):
        """Setup the ``app.after_request`` and ``app.on_exception``
        hooks to call ``db.session.remove()`` after each response, and
        ``db.session.rollback()`` if an error occurs.
        """
        teardown = None
        # 0.9 and later
        if hasattr(app, 'teardown_appcontext'):
            teardown = app.teardown_appcontext
        # 0.7 to 0.8
        elif hasattr(app, 'teardown_request'):
            teardown = app.teardown_request
        # Older Flask versions
        elif hasattr(app, 'after_request'):
            teardown = app.after_request
        if teardown:
            teardown(shutdown)

        if hasattr(app, 'on_exception'):
            app.on_exception(rollback)

    def set_bottle_hooks(self, app, shutdown, rollback):
        """Setup the bottle-specific ``after_request`` to call
        ``db.session.remove()`` after each response.
        """
        if hasattr(app, 'hook'):
            app.hook('after_request')(shutdown)

    def set_webpy_hooks(self, app, shutdown, rollback):
        """Setup the webpy-specific ``web.unloadhook`` to call
        ``db.session.remove()`` after each response.
        """
        try:
            import web
        except ImportError:
            return
        if not hasattr(web, 'application'):
            return
        if not isinstance(app, web.application):
            return
        app.processors.append(0, web.unloadhook(shutdown))

    @property
    def engine(self):
        """Gives access to the engine.
        """
        with self._engine_lock:
            connector = self.connector
            if connector is None:
                connector = EngineConnector(self)
                self.connector = connector
            return connector.get_engine()

    @property
    def metadata(self):
        """Proxy for ``Model.metadata``.
        """
        return self.Model.metadata

    @property
    def query(self):
        """Proxy for ``self.session.query``.
        """
        return self.session.query

    def add(self, *args, **kwargs):
        """Proxy for ``self.session.add``.
        """
        return self.session.add(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """Proxy for ``self.session.delete``.
        """
        return self.session.delete(*args, **kwargs)

    def flush(self, *args, **kwargs):
        """Proxy for ``self.session.flush``.
        """
        return self.session.flush(*args, **kwargs)

    def commit(self, *args, **kwargs):
        """Proxy for ``self.session.commit``.
        """
        return self.session.commit(*args, **kwargs)

    def rollback(self, *args, **kwargs):
        """Proxy for ``self.session.rollback``.
        """
        return self.session.rollback(*args, **kwargs)

    def create_all(self, *args, **kwargs):
        """Creates all tables.
        """
        kwargs.setdefault('bind', self.engine)
        self.Model.metadata.create_all(*args, **kwargs)

    def drop_all(self, *args, **kwargs):
        """Drops all tables.
        """
        kwargs.setdefault('bind', self.engine)
        self.Model.metadata.drop_all(*args, **kwargs)

    def reflect(self, meta=None, *args, **kwargs):
        """Reflects tables from the database.
        """
        meta = meta or MetaData()
        kwargs.setdefault('bind', self.engine)
        meta.reflect(*args, **kwargs)
        return meta

    def get_engine(cls, current_app):
        """Proxy for compatibility with flask-debugtoolbar
        """
        databases = getattr(current_app, 'databases', None)
        if not databases:
            return None
        return databases[0].engine

    def __repr__(self):
        return "<SQLAlchemy('{0}')>".format(self.uri)


def monkeypatch_flask_debugtoolbar():
    try:
        import flask_debugtoolbar.panels.sqlalchemy
    except ImportError:
        return

    flask_debugtoolbar.panels.sqlalchemy.SQLAlchemy = SQLAlchemy
    flask_debugtoolbar.panels.sqlalchemy.get_debug_queries = get_debug_queries
    flask_debugtoolbar.panels.sqlalchemy.sqlalchemy_available = True
