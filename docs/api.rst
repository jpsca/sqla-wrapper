.. _api:

API
=============================================

.. module:: sqlalchemy_wrapper

This part of the documentation documents all the public classes and
functions in SQLAlchemy-Wrapper.


Configuration
----------------------------------------------

.. autoclass:: SQLAlchemy
   :members:


Connection URI Format
``````````````````````````````````````````````

For a complete list of connection URIs head over to the SQLAlchemy documentation under (`Supported Databases <http://www.sqlalchemy.org/docs/core/engines.html>`_).  This here shows some common connection strings.

SQLAlchemy indicates the source of an Engine as a URI combined with
optional keyword arguments to specify options for the Engine. The form of the URI is::

    dialect+driver://username:password@host:port/database

Many of the parts in the string are optional. If no driver is specified the default one is selected (make sure to *not* include the ``+`` in that case).

Postgres::

    postgresql://scott:tiger@localhost/mydatabase

MySQL::

    mysql://scott:tiger@localhost/mydatabase

Oracle::

    oracle://scott:tiger@127.0.0.1:1521/sidname

SQLite (note the four leading slashes)::

    sqlite:////absolute/path/to/foo.db


Models
----------------------------------------------

.. autoclass:: BaseQuery
   :members: get_or_error, first_or_error, paginate

   .. method:: all()

      Return the results represented by this query as a list.  This
      results in an execution of the underlying query.

   .. method:: order_by(*criterion)

      apply one or more ORDER BY criterion to the query and return the
      newly resulting query.

   .. method:: limit(limit)

      Apply a LIMIT  to the query and return the newly resulting query.

   .. method:: offset(offset)

      Apply an OFFSET  to the query and return the newly resulting
      query.

   .. method:: first()

      Return the first result of this query or `None` if the result
      doesn‘t contain any rows.  This results in an execution of the
      underlying query.


Utilities
----------------------------------------------

.. autoclass:: Paginator
   :members:

.. autofunction:: sanitize_page_number
