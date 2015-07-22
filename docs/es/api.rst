.. _api:

Referencia del API
=============================================

.. module:: sqlalchemy_wrapper

Esta parte de la documentación muestra todas las clases y funciones públicas en SQLAlchemy-Wrapper.


Configuración
----------------------------------------------

.. autoclass:: SQLAlchemy
   :members:


.. include:: connection-uri.rst.inc


Modelos
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


Paginador
----------------------------------------------

.. autoclass:: Paginator
   :members:

.. autofunction:: sanitize_page_number
