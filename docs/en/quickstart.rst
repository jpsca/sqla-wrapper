.. _quickstart:

Quickstart
========================

.. currentmodule:: sqlalchemy_wrapper

SQLAlchemy-Wrapper makes incredibly easy to start using SQLAlchemy and readily extends for complex scenarios. For the complete guide, checkout out the API documentation on the :class:`SQLAlchemy` class.


.. sourcecode:: bash

    pip install sqlalchemy_wrapper

The SQLAlchemy class is used to instantiate a SQLAlchemy connection to a database.

.. sourcecode:: python

    from sqlalchemy_wrapper import SQLAlchemy

    db = SQLAlchemy(_uri_to_database_)

Once created, that object then contains all the functions and helpers from both :mod:`sqlalchemy` and :mod:`sqlalchemy.orm`. It also provides a class called `Model` that is a declarative base which can be used to declare models:

.. sourcecode:: python

    class User(db.Model):

        login = db.Column(db.Unicode, unique=True)
        passw_hash = db.Column(db.Unicode)

        profile_id = db.Column(db.Integer, db.ForeignKey(Profile.id))
        profile = db.relationship(Profile, backref=db.backref('user'))


If you are using Flask or other framework that uses the ``after_request`` and ``on_exception`` decorators, you have to commit the session, but you don’t have to remove it at the end of the request, SQLAlchemy-Wrapper does that for you (this works with Bottle’s and webpy’s hooks too).

.. note::

    In any other scenario **you have to** call ``db.session.remove()`` after each response or a memory leak will happen.


.. include:: connection-uri.rst.inc


A Minimal Application
----------------------------------------------

For the common case of having one Flask application all you have to do is to create your Flask application, load the configuration of choice and then create the :class:`SQLAlchemy` object by passing it the application.

.. sourcecode:: python

    from flask import Flask
    from sqlalchemy_wrapper import SQLAlchemy

    app = Flask(__name__)
    db = SQLAlchemy('sqlite://', app=app)

or

.. sourcecode:: python

    from flask import Flask
    from sqlalchemy_wrapper import SQLAlchemy

    db = SQLAlchemy()
    app = Flask(__name__)
    db.init_app(app)

Once created, you use that object to declare models:

.. sourcecode:: python

    class User(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        username = db.Column(db.String(80), unique=True)
        email = db.Column(db.String(120), unique=True)

        def __init__(self, username, email):
            self.username = username
            self.email = email

        def __repr__(self):
            return '<User %r>' % self.username

To create the initial database, just import the `db` object from a interactive Python shell and run the :meth:`SQLAlchemy.create_all` method to create the tables and database:

.. sourcecode:: python

    >>> from yourapplication import db
    >>> db.create_all()

Boom, and there is your database. Now to create some users:

.. sourcecode:: python

    >>> from yourapplication import User
    >>> admin = User('admin', 'admin@example.com')
    >>> guest = User('guest', 'guest@example.com')

But they are not yet in the database, so let's make sure they are:

.. sourcecode:: python

    >>> db.add(admin)
    >>> db.add(guest)
    >>> db.commit()

Accessing the data in database is easy as a pie:

.. sourcecode:: python

    >>> users = User.query.all()
    [<User u'admin'>, <User u'guest'>]
    >>> admin = User.query.filter_by(username='admin').first()
    <User u'admin'>


Simple Relationships
----------------------------------------------

SQLAlchemy connects to relational databases and what relational databases are really good at are relations. As such, we shall have an example of an application that uses two tables that have a relationship to each other:


.. sourcecode:: python

    from datetime import datetime


    class Post(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        title = db.Column(db.String(80))
        body = db.Column(db.Text)
        pub_date = db.Column(db.DateTime)

        category_id = db.Column(db.Integer,
            db.ForeignKey('category.id'))
        category = db.relationship('Category',
            backref=db.backref('posts', lazy='dynamic'))

        def __repr__(self):
            return '<Post %r>' % self.title


    class Category(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(50))

        def __init__(self, name):
            self.name = name

        def __repr__(self):
            return '<Category %r>' % self.name

First let's create some objects:

.. sourcecode:: python

    >>> py = Category('Python')
    >>> p = Post(title='Hello Python!', category=py)
    >>> db.add(py)
    >>> db.add(p)

Now because we declared `posts` as dynamic relationship in the backref it shows up as query:

.. sourcecode:: python

    >>> py.posts
    <sqlalchemy.orm.dynamic.AppenderBaseQuery object at 0x1027d37d0>

It behaves like a regular query object so we can ask it for all posts that are associated with our test “Python” category:

.. sourcecode:: python

    >>> py.posts.all()
    [<Post 'Hello Python!'>]


.. admonition:: Do not forget

    You should read the `SQLAlchemy documentation <http://docs.sqlalchemy.org/en/latest/orm/basic_relationships.html>`_ too.


Road to Enlightenment
----------------------------------------------

:class:`SQLAlchemy` gives you access to the following things:

-   all the functions and classes from :mod:`sqlalchemy` and :mod:`sqlalchemy.orm`
-   a preconfigured scoped session called `session`
-   the :attr:`~SQLAlchemy.metadata`
-   the :attr:`~SQLAlchemy.engine`
-   a :meth:`SQLAlchemy.create_all` and :meth:`SQLAlchemy.drop_all` methods to create and drop tables according to the models.
-   a :meth:`SQLAlchemy.query`, :meth:`SQLAlchemy.add`, :meth:`SQLAlchemy.delete`, :meth:`SQLAlchemy.flush`, :meth:`SQLAlchemy.commit` and , :meth:`SQLAlchemy.rollback` methods, as proxy for the ones in :meth:`SQLAlchemy.session`.
-   a :class:`Model` base class that is a configured declarative base.



