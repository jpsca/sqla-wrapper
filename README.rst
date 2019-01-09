===========================
SQLA-wrapper |travis|
===========================

.. |travis| image:: https://travis-ci.org/jpscaletti/sqla-wrapper.png
   :alt: Build Status
   :target: https://travis-ci.org/jpscaletti/sqla-wrapper

A friendly wrapper for SQLAlchemy.

.. sourcecode:: python

    from sqla_wrapper import SQLAlchemy

    db = SQLAlchemy('sqlite:///:memory:')

    class ToDo(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        ...

    db.create_all()
    
    db.add(Todo(...))
    db.commit()

    todos = ToDo.query.all()


Read the complete documentation here: http://sqlawrapper.lucuma.co

Since 2.0, only Python 3.6 or later are supported.
Please use the `1.9.1` version if your project runs on a previous Python version.

SQLAlchemy
======================

The things you need to know compared to plain SQLAlchemy are:

1.  The :class:`SQLAlchemy` gives you access to the following things:

    -   All the functions and classes from :mod:`sqlalchemy` and
        :mod:`sqlalchemy.orm`
    -   All the functions from a preconfigured scoped session (called ``_session``).
    -   The :attr:`~SQLAlchemy.metadata` and :attr:`~SQLAlchemy.engine`
    -   The methods :meth:`SQLAlchemy.create_all` and :meth:`SQLAlchemy.drop_all`
        to create and drop tables according to the models.
    -   a :class:`Model` baseclass that is a configured declarative base.

2.  All the functions from the session are available directly in the class, so you
    can do ``db.add``,  ``db.commit``,  ``db.remove``, etc.

3.  The :class:`Model` declarative base class behaves like a regular
    Python class but has a ``query`` attribute attached that can be used to
    query the model.

4.  The :class:`Model` class also auto generates ``_tablename__`` attributes, if you
    don't define one, based on the underscored and **pluralized** name of your classes.

5.  You have to commit the session and configure your app to remove it at
    the end of the request.


Run the tests
======================

You'll need `poetry` to install de development dependencies.

  poetry install

This command will automnatically create a virtual environment to run the project in.
Read more in the `Poetry site <https://poetry.eustace.io/>`_

To run the tests in your current Python version do::

    pytest tests

To run them in every supported Python version do::

    tox

It's also neccesary to run the coverage report to make sure all lines of code
are touch by the tests::

    make coverage

Our test suite `runs continuously on Travis CI <https://travis-ci.org/jpscaletti/sqla-wrapper>`_ with every update.


:copyright: 2013-2019 by `Juan-Pablo Scaletti <http://jpscaletti.com>`_.
:license: MIT, see LICENSE for more details.
