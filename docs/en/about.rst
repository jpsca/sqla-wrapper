.. _about:

About SQLAlchemy-Wrapper
=============================================

Goals
----------------------------------------------
- Make really easy to setup SQLAlchemy
- Be framework independent
- Do not hide SQLAlchemy syntax


License
----------------------------------------------

SQLAlchemy-Wrapper is under a BSD license. It basically means: do whatever you want with it as long as the copyright in SQLAlchemy-Wrapper sticks around, the conditions are not modified and the disclaimer is present.

See `LICENSE` for more details.


What about Flask-SQLAlchemy?
----------------------------------------------

SQLAlchemy-Wrapper was born as a framework-independent fork of `Flask-SQLAlchemy <https://pythonhosted.org/Flask-SQLAlchemy/>`_, but there are other reasons to use it instead:

Flask-SQLAlchemy needs a Flask app to get the connection URI and a request context in order to run. This can be cumbersome for testing or standalone scripts.

Flask-SQLAlchemy also introduces a new syntax for queries (eg. ``User.query.filter_by(username='peter')``) that at first might seem more usable but instead forces you to return to the standard syntax (``db.query(User)``) for things like aggregated selects, sql functions, etc. And the standard syntax does not have the paginator or the special methods (eg. ``get_or_404``).

For all these reasons we prefer to use SQLAlchemy-Wrapper even in Flask applications.
