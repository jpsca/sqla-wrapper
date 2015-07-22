:orphan:

=============================================
SQLAlchemy-Wrapper
=============================================

.. container:: lead

    Un empaque amigable para SQLAlchemy.


SQLAlchemy is genial pero por todas sus opciones se hace dificil saber como usarlo, sobre todo al verlo por primera vez.

Esta biblioteca existe para cambiar eso. *En vez* de tener que escribir algo como:

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

con SQLAlchemy-Wrapper puedes simplemente hacer:

.. sourcecode:: python

    from sqlalchemy_wrapper import SQLAlchemy

    db = SQLALchemy('sqlite:///:memory:')

    class ToDo(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        ...

    db.create_all()
    todos = db.query(ToDo).all()

También puede :ref:`paginar <pagination>` los resultados por ti.

SQLAlchemy-Wrapper nacio como un clon de `Flask-SQLAlchemy <https://pythonhosted.org/Flask-SQLAlchemy/>`_ pero independiente de cualquier framework y con algunas opiniones diferentes.
Lee más sobre los objetivos del proyecto en la sección de :ref:`about`.

Testeado con Python 2.7, 3.3+ y pypy.

.. include:: contents.rst.inc
