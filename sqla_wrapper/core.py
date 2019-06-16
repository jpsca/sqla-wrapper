import sqlalchemy
from sqlalchemy.engine.url import make_url
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker, Session
from sqlalchemy.util import get_cls_kwargs

from .base_query import BaseQuery
from .model import Model, DefaultMeta
from .session_proxy import SessionProxyMixin


class SQLAlchemy(SessionProxyMixin):
    """This class is used to easily instantiate a SQLAlchemy connection to
    a database, to provide a base class for your models, and to get a session
    to interact with them.

    .. sourcecode:: python

        db = SQLAlchemy(_uri_to_database_)

        class User(db.Model):
            login = Column(String(80), unique=True)
            passw_hash = Column(String(80))

    .. warning:: **IMPORTANT**

        In a web application or a multithreaded environment you need to call
        ``session.remove()`` when a request/thread ends. Use your framework's
        ``after_request`` hook, to do that. For example, in `Flask`:

        .. sourcecode:: python

            app = Flask(…)
            db = SQLAlchemy(…)

            @app.teardown_appcontext
            def shutdown(response=None):
                db.remove()
                return response

    Use the ``db`` to interact with the data:

    .. sourcecode:: python

        user = User('tiger')
        db.add(user)
        db.commit()
        # etc

    To query, you can use ``db.query``

    .. sourcecode:: python

        db.query(User).all()
        db.query(User).filter_by(login == 'tiger').first()
        # etc.

    .. tip:: **Scoping**

        By default, sessions are scoped to the current thread, but he SQLAlchemy
        documentation recommends scoping the session to something more
        application-specific if you can, like a web request in a web app.

        To do that, you can use the ``scopefunc`` argument, passing a function that
        returns something unique (and hashable) like a request.

    """

    def __init__(self, url='sqlite://', *, metadata=None, metaclass=None,
                 model_class=Model, scopefunc=None, **options):
        self.url = url
        self.info = make_url(url)
        self.scopefunc = scopefunc

        self.Model = self._make_declarative_base(model_class, metadata, metaclass)
        self._update_options(options)
        self.engine = sqlalchemy.create_engine(url, **self.engine_options)
        self.Session = sessionmaker(bind=self.engine, **self.session_options)
        self._session = scoped_session(self.Session, scopefunc)

        _include_sqlalchemy(self)

    def _update_options(self, options):
        session_options = {}

        for arg in get_cls_kwargs(Session):
            if arg in options:
                session_options[arg] = options.pop(arg)

        options.setdefault('echo', False)
        self.engine_options = options

        session_options.setdefault('autoflush', True)
        session_options.setdefault('autocommit', False)
        session_options.setdefault('query_cls', BaseQuery)
        self.session_options = session_options

    def _make_declarative_base(self, model_class, metadata=None, metaclass=None):
        """Creates the declarative base."""
        return declarative_base(
            cls=model_class, name='Model',
            metadata=metadata,
            metaclass=metaclass if metaclass else DefaultMeta
        )

    @property
    def metadata(self):
        """Proxy for ``Model.metadata``."""
        return self.Model.metadata

    def create_all(self, *args, **kwargs):
        """Creates all tables."""
        kwargs.setdefault('bind', self.engine)
        self.Model.metadata.create_all(*args, **kwargs)

    def drop_all(self, *args, **kwargs):
        """Drops all tables."""
        kwargs.setdefault('bind', self.engine)
        self.Model.metadata.drop_all(*args, **kwargs)

    def reconfigure(self, **kwargs):
        """Updates the session options."""
        self._session.remove()
        self.session_options.update(**kwargs)
        self._session.configure(**self.session_options)

    def __repr__(self):
        return "<SQLAlchemy('{}')>".format(self.url)


def _include_sqlalchemy(obj):
    for module in sqlalchemy, sqlalchemy.orm:
        for key in module.__all__:
            if not hasattr(obj, key):
                setattr(obj, key, getattr(module, key))
    # Note: obj.Table does not attempt to be a SQLAlchemy Table class.
    obj.Table = _make_table(obj)
    obj.event = sqlalchemy.event


def _make_table(db):
    def _make_table(*args, **kwargs):
        if len(args) > 1 and isinstance(args[1], db.Column):
            args = (args[0], db.metadata) + args[1:]
        return sqlalchemy.Table(*args, **kwargs)
    return _make_table
