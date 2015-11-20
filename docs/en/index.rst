:orphan:

=============================================
SQLAlchemy-Wrapper
=============================================

.. container:: lead

    A friendly wrapper for SQLAlchemy.


SQLAlchemy is great but it is difficult to setup, specially for beginners.

So, *instead* of having to write something like this:

.. sourcecode:: python

    from sqlalchemy import create_engine
    from sqlalchemy.ext.declarative import declarative_base
    from sqlalchemy.orm import sessionmaker, Column, Integer

    engine = create_engine('sqlite:///:memory:')
    Session = sessionmaker(bind=engine)
    Model = declarative_base()

    class ToDo(Model):
        id = Column(Integer, primary_key=True)
        ...

    Model.metadata.create_all(engine)
    session = Session()
    todos = session.query(ToDo).all()

with SQLAlchemy-Wrapper you can write it like this:

.. sourcecode:: python

    from sqlalchemy_wrapper import SQLAlchemy

    db = SQLAlchemy('sqlite:///:memory:')

    class ToDo(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        ...

    db.create_all()
    todos = db.query(ToDo).all()


It can also :ref:`paginate <pagination>` the results for you.




Using it with Flask-DebugToolbar
----------------------------------

SQLAlchemy-Wrapper is fully compatible with Flask-DebugToolbar, but it needs an extra step for it to work propperly.

In order to see the queries on the Flask debug toolbar, you **must activate first the query recording using the argument record_queries**:

.. sourcecode:: python 
    
        db = SQLAlchemy(SQLALCHEMY_URI, app=app, record_queries=True)

(In Flask-SQLAlchemy this is done automatically if DEBUG is True... *I'll probably do something similar soon*)


SQLAlchemy-Wrapper was born as a framework-independent fork of `Flask-SQLAlchemy <https://pythonhosted.org/Flask-SQLAlchemy/>`_.
Read about the goals of the project in the :ref:`about` section.

Tested with Python 2.7, 3.3+ and pypy.

.. include:: contents.rst.inc



