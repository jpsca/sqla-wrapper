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

    db = SQLALchemy('sqlite:///:memory:')

    class ToDo(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        ...

    db.create_all()
    todos = db.query(ToDo).all()


It can also :ref:`paginate <pagination>` the results for you.

SQLAlchemy-Wrapper was born as a framework-independent fork of `Flask-SQLAlchemy <https://pythonhosted.org/Flask-SQLAlchemy/>`_.
Read about the goals of the project in the :ref:`about` section.

Tested with Python 2.7, 3.3+ and pypy.

.. include:: contents.rst.inc
