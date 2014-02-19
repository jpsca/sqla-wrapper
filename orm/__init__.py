# -*- coding: utf-8 -*-
"""
==========
O.R.M.
==========

A framework-independent wrapper for SQLAlchemy that makes it really easy and fun to use.

This library works with Python 2.6, 2.7 and pypy.


Example:

::

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


It does an automatic table naming (if no table name is defined using the `__tablename__` property) by pluralizing the class name with the `inflection` library. So, for example, a `User` model gets a table named `users`.


How to use
---------------------

The SQLAlchemy class is used to instantiate a SQLAlchemy connection to
a database.

::
    db = SQLAlchemy(_uri_to_database_)


The class also provides access to all the SQLAlchemy
functions from the `sqlalchemy` and `sqlalchemy.orm` modules.
So you can declare models like this:

::
    class User(db.Model):
        login = db.Column(db.String(80), unique=True)
        passw_hash = db.Column(db.String(80))
        profile_id = db.Column(db.Integer, db.ForeignKey(Profile.id))
        profile = db.relationship(Profile, backref=db.backref('user'))


In a web application you need to call `db.session.remove()` after each response, and `db.session.rollback()` if an error occurs. However, if you are using Flask or other framework that uses the `after_request` and `on_exception` decorators, these bindings can be done automatically (this works with Bottle's `hook` too):

::
    app = Flask(__name__)

    db = SQLAlchemy('sqlite://', app=app)

or::

    db = SQLAlchemy()

    app = Flask(__name__)

    db.init_app(app)


More examples
---------------------

Many databases, one web app
`````````````````````````````

::
    app = Flask(__name__)
    db1 = SQLAlchemy(URI1, app)
    db2 = SQLAlchemy(URI1, app)


Many web apps, one database
`````````````````````````````

::
    db = SQLAlchemy(URI1)

    app1 = Flask(__name__)
    app2 = Flask(__name__)
    db.init_app(app1)
    db.init_app(app2)


Aggegated selects
`````````````````````````````

::
    res = db.query(db.func.sum(Unit.price).label('price')).all()
    print res.price


------------------------------------------------------------------------------
MIT License (http://www.opensource.org/licenses/mit-license.php).
© 2012 by Lúcuma labs (http://lucumalabs.com).

"""
from orm.main import SQLAlchemy


__version__ = '1.1.0'

