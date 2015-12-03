===========================
SQLAlchemy-Wrapper |travis|
===========================

.. |travis| image:: https://travis-ci.org/jpscaletti/sqlalchemy-wrapper.png
   :alt: Build Status
   :target: https://travis-ci.org/jpscaletti/sqlalchemy-wrapper

A friendly wrapper for SQLAlchemy.


.. sourcecode:: python

    from sqlalchemy_wrapper import SQLAlchemy

    db = SQLAlchemy('sqlite:///:memory:')

    class ToDo(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        ...

    db.create_all()
    todos = db.query(ToDo).all()


Read the complete documentation here: http://sqlawrapper.lucuma.co

SQLAlchemy-Wrapper was born as a framework-independent fork of `Flask-SQLAlchemy <https://pythonhosted.org/Flask-SQLAlchemy/>`_. Read about the goals of the project in the `About SQLAlchemy-Wrapper <http://sqlawrapper.lucuma.co/about.html>`_ section of the documentation.

Works with Python 2.7, 3.3+ and pypy.

Contributing
======================

#. Check for `open issues <https://github.com/jpscaletti/sqlalchemy-wrapper/issues>`_ or open
   a fresh issue to start a discussion around a feature idea or a bug.
#. Fork the `SQLAlchemy-Wrapper repository on Github <https://github.com/jpscaletti/sqlalchemy-wrapper>`_
   to start making your changes.
#. Write a test which shows that the bug was fixed or that the feature works
   as expected.
#. Send a pull request and bug the maintainer until it gets merged and published.
   :) Make sure to add yourself to ``AUTHORS``.


Run the tests
======================

We use some external dependencies, listed in ``requirements_tests.txt``::

    $  pip install -r requirements-tests.txt
    $  python setup.py install

To run the tests in your current Python version do::

    $  make test

To run them in every supported Python version do::

    $  tox

It's also neccesary to run the coverage report to make sure all lines of code
are touch by the tests::

    $  make coverage

Our test suite `runs continuously on Travis CI <https://travis-ci.org/jpscaletti/sqlalchemy-wrapper>`_ with every update.



:copyright: 2012-2015 by `Juan-Pablo Scaletti <http://jpscaletti.com>`_.
:license: BSD, see LICENSE for more details.

Some of the code was extracted and adapted from `Flask-SQLAlchemy <http://flask-sqlalchemy.pocoo.org/>`_

:copyright: 2010-2014 by Armin Ronacher.
:license: BSD, see LICENSE for more details.
