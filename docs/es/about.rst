.. _about:

Sobre SQLAlchemy-Wrapper
=============================================

Objetivos del proyecto
----------------------------------------------
- Hacer muy sencillo empezar con SQLAlchemy
- Ser independiente de cualquier framework web
- Dejar que puedas reusar tu conocimiento de SQLALchemy, en vez de ocultar su sintaxis


Licencia
----------------------------------------------

SQLAlchemy-Wrapper está bajo una licencia BSD. Básicamente significa: haz lo que quiers con ella siempre y cuando el aviso de copyright permanezca, las condiciones no se modifiquen y el texto de descargo siga presente.

Mira el archivo `LICENSE` para más detalles.


¿Y por que no Flask-SQLAlchemy?
----------------------------------------------

SQLAlchemy-Wrapper was forked from `Flask-SQLAlchemy <https://pythonhosted.org/Flask-SQLAlchemy/>`_.

Flask-SQLAlchemy needs a Flask app to get the connection URI and a request context in order to run. This can be cumbersome for testing or standalone scripts.

Flask-SQLAlchemy also introduces a new syntax for queries (eg. ``User.query.filter_by(username='peter')``) that at first might seem more usable but instead forces you to return to the standard syntax (``db.query(User)``) for things like aggregated selects, sql functions, etc. And the standard syntax does not have the paginator or the special methods (eg. ``get_or_404``).

For all these reasons we prefer to use SQLAlchemy-Wrapper even in Flask applications.
