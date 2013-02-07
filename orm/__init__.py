    # -*- coding: utf-8 -*-
"""
    ==========
    ORM
    ==========

    A framework-independent wrapper for SQLAlchemy that makes it
    really easy and fun to use.

    Example:

    .. sourcecode:: python

        from orm import SQLALchemy

        db = SQLALchemy('postgresql://scott:tiger@localhost:5432/mydatabase')

        class ToDo(db.Model):
            id = db.Column(db.Integer, primary_key=True)
            title = db.Column(db.String(60), nullable=False)
            done = db.Column(db.Boolean, nullable=False, default=False)
            pub_date = db.Column(db.DateTime, nullable=False,
                default=datetime.utcnow)

        to_do = ToDo(title='Install orm', done=True)
        db.add(to_do)
        db.commit()

        completed = db.query(ToDo).order_by(Todo.pub_date.desc()).all()

    It does an automatic table naming (if no name is defined) and, to the
    base query class.

    ---------------------------------------
    MIT License (http://www.opensource.org/licenses/mit-license.php).
    © 2013 by Lúcuma labs (http://lucumalabs.com).

"""
import os
import threading

try:
    import sqlalchemy
except ImportError:
    raise ImportError('Unable to load the sqlalchemy package.'
        ' `orm` needs the SQLAlchemy library to run.'
        ' You can get download it from http://www.sqlalchemy.org/'
        ' If you\'ve already installed SQLAlchemy, then make sure you have '
        ' it in your PYTHONPATH.')
from sqlalchemy.engine.url import make_url
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.schema import MetaData

from .helpers import (create_scoped_session, include_sqlalchemy, Model,
    EngineConnector)


__version__ = '1.0'


class SQLAlchemy(object):
    """This class is used to instantiate a SQLAlchemy connection to
    a database.

        db = SQLAlchemy(_uri_to_database_)

    The class also provides access to all the SQLAlchemy
    functions from the :mod:`sqlalchemy` and :mod:`sqlalchemy.orm` modules.
    So you can declare models like this::

        class User(db.Model):
            login = db.Column(db.String(80), unique=True)
            passw_hash = db.Column(db.String(80))

    In a web application you need to call `db.session.remove()`
    after each response, and `db.session.rollback()` if an error occurs.
    If your application object has a `after_request` and `on_exception
    decorators, just pass that object at creation::

        app = Flask(__name__)
        db = SQLAlchemy('sqlite://', app=app)

    or later::

        db = SQLAlchemy()

        app = Flask(__name__)
        db.init_app(app)

    """

    def __init__(self, uri='sqlite://', app=None, echo=False, pool_size=None,
            pool_timeout=None, pool_recycle=None):
        self.uri = uri
        self.info = make_url(uri)

        self.options = self.build_options_dict(echo=echo, pool_size=pool_size,
            pool_timeout=pool_timeout, pool_recycle=pool_recycle)
        self.apply_driver_hacks()
        
        self.connector = None
        self._engine_lock = threading.Lock()
        self.session = create_scoped_session(self)

        self.Model = declarative_base(cls=Model, name='Model')
        self.Model.db = self
        
        if app is not None:
            self.init_app(app)
        
        include_sqlalchemy(self)

    def apply_driver_hacks(self):
        if self.info.drivername == 'mysql':
            self.info.query.setdefault('charset', 'utf8')
            self.options.setdefault('pool_size', 10)
            self.options.setdefault('pool_recycle', 7200)
        
        elif self.info.drivername == 'sqlite':
            pool_size = self.options.get('pool_size')
            if self.info.database in (None, '', ':memory:') and pool_size == 0:
                raise ValueError('SQLite in-memory database with an '
                    'empty queue (pool_size = 0) is not possible due to '
                    'data loss.')

    def build_options_dict(self, **kwargs):
        options = {'convert_unicode': True}
        for key, value in kwargs.items():
            if value is not None:
                options[key] = value
        return options

    def init_app(self, app):
        """This callback can be used to initialize an application for the
        use with this database setup. In a web application or a multithreaded
        environment, never use a database without initialize it first, 
        or connections will leak.

        """
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
            except (Exception), e:
                pass

        self.set_flask_hooks(app, shutdown, rollback)
        self.set_bottle_hooks(app, shutdown, rollback)

    def set_flask_hooks(self, app, shutdown, rollback):
        if hasattr(app, 'after_request'):
            app.after_request(shutdown)
        if hasattr(app, 'on_exception'):
            app.on_exception(rollback)

    def set_bottle_hooks(self, app, shutdown, rollback):
        if hasattr(app, 'hook'):
            app.hook('after_request')(shutdown)
    
    @property
    def query(self):
        return self.session.query
    
    def add(self, *args, **kwargs):
        return self.session.add(*args, **kwargs)

    def flush(self, *args, **kwargs):
        return self.session.flush(*args, **kwargs)
    
    def commit(self):
        return self.session.commit()
    
    def rollback(self):
        return self.session.rollback()
    
    @property
    def metadata(self):
        """Returns the metadata"""
        return self.Model.metadata

    @property
    def engine(self):
        """Gives access to the engine. """
        with self._engine_lock:
            connector = self.connector
            if connector is None:
                connector = EngineConnector(self)
                self.connector = connector
            return connector.get_engine()
    
    def create_all(self):
        """Creates all tables. """
        self.Model.metadata.create_all(bind=self.engine)
    
    def drop_all(self):
        """Drops all tables. """
        self.Model.metadata.drop_all(bind=self.engine)

    def reflect(self, meta=None):
        """Reflects tables from the database. """
        meta = meta or MetaData()
        meta.reflect(bind=self.engine)
        return meta

    def __repr__(self):
        return '<%s(%r)>' % (self.__class__.__name__, self.uri)

