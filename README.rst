===========================
SQLAlchemy-Wrapper |travis|
===========================

.. image:: https://badges.gitter.im/Join%20Chat.svg
   :alt: Join the chat at https://gitter.im/lucuma/sqlalchemy-wrapper
   :target: https://gitter.im/lucuma/sqlalchemy-wrapper?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge

.. |travis| image:: https://travis-ci.org/lucuma/sqlalchemy-wrapper.png
   :alt: Build Status
   :target: https://travis-ci.org/lucuma/sqlalchemy-wrapper

A friendly wrapper for SQLAlchemy.

Works with Python 2.7, 3.3, 3.4 and pypy.

Example:

.. code-block:: python

    from sqlalchemy_wrapper import SQLAlchemy

    db = SQLALchemy('postgresql://scott:tiger@localhost:5432/mydatabase')

    class ToDo(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        title = db.Column(db.String(60), nullable=False)
        done = db.Column(db.Boolean, nullable=False, default=False)
        pub_date = db.Column(db.DateTime, nullable=False,
            default=datetime.utcnow)

    to_do = ToDo(title='Install SQLAlchemy-Wrapper', done=True)
    db.add(to_do)
    db.commit()

    completed = db.query(ToDo).order_by(Todo.pub_date.desc()).all()
    paginated = db.query(ToDo).paginate(page=2, per_page=10)


Read the complete documentation here: http://sqlawrapper.lucuma.co

______


Contributing
======================

#. Check for `open issues <https://github.com/lucuma/sqlalchemy-wrapper/issues>`_ or open
   a fresh issue to start a discussion around a feature idea or a bug.
#. Fork the `SQLAlchemy-Wrapper repository on Github <https://github.com/lucuma/sqlalchemy-wrapper>`_
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

Our test suite `runs continuously on Travis CI <https://travis-ci.org/lucuma/sqlalchemy-wrapper>`_ with every update.


______

SQLAlchemy-Wrapper was forked from `Flask-SQLAlchemy <https://pythonhosted.org/Flask-SQLAlchemy/>`_. Read about the goals of the project `here <http://sqlawrapper.lucuma.co/about.html>`_.

:copyright: 2012-2015 by `Juan-Pablo Scaletti <http://jpscaletti.com>`_.
:copyright: 2010 by Armin Ronacher.
:license: BSD, see LICENSE for more details.
