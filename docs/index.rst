:orphan:

=============================================
SQLA-Wrapper
=============================================

.. container:: lead

    A friendly wrapper for SQLAlchemy.


SQLAlchemy is great can be difficult to setup.

So, *instead* of having to write something like this:

.. sourcecode:: python

    from sqlalchemy import create_engine
    from sqlalchemy.ext.declarative import declarative_base
    from sqlalchemy.orm import sessionmaker, Column, Integer

    engine = create_engine('sqlite:///:memory:')
    Session = sessionmaker(bind=engine)
    session = 
    Model = declarative_base()

    class ToDo(Model):
        id = Column(Integer, primary_key=True)
        ...

    Model.metadata.create_all(engine)
    session = Session()
    todos = session.query(ToDo).all()

with SQLA-Wrapper you can write it like this:

.. sourcecode:: python

    from sqla_wrapper import SQLAlchemy

    db = SQLAlchemy('sqlite:///:memory:')

    class ToDo(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        ...

    db.create_all()
    todos = db.query(ToDo).all()


It can also :ref:`paginate <pagination>` the results for you.

----

Since 2.0, only Python 3.6 or later are supported.
Please use the `1.9.1` version if your project runs on a previous Python version.

.. include:: contents.rst.inc
