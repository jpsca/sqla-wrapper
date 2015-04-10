.. _pagination:

Pagination
=============================================

All the results can be easily paginated

.. sourcecode:: python

    >>> users = db.query(User).paginate(page=2, per_page=20)
    >>> print(list(users))
    [User(21), User(22), User(23), ... , User(40)]


The paginator object it's an iterable that returns only the results for that page, so you use it in your templates in the same way than the original result:

.. sourcecode:: html+jinja

    {% for item in paginated_items %}
        <li>{{ item.name }}</li>
    {% endfor %}

You can also use it standalone with any iterable

.. sourcecode:: python

    from sqlalchemy_wrapper import Paginator

    pusers = Paginator(db.query(User), page=2, per_page=20)
    pnumbers = Paginator(range(100), page=1, per_page=10)
    pempty = Paginator([])

You can even fake the total number of items by using a ``total`` parameter:

.. sourcecode:: python

    >>> items = Paginator([], total=300)
    >>> print(items.num_pages)
    30


Rendering the page numbers
----------------------------------------------

Below your results is common that you want to render the list of pages for quick navigation.

However, *all page numbers* are sometimes too many to display.

The :attr:`~Paginator.pages` property is an iterator that returns the page numbers, but sometimes not all of them: if there are more than 11 pages, the result will be similar to one of these, depending of what page you are currently on:


.. figure:: _static/paginator1.png
   :align: center

.. figure:: _static/paginator2.png
   :align: center

.. figure:: _static/paginator3.png
   :align: center


Skipped page numbers are represented as ``None``.

This is one way how you could render such a pagination in your templates:

.. sourcecode:: html+jinja
   :emphasize-lines: 12, 13, 20, 22, 23

    {% macro render_paginator(paginator, endpoint) %}
      <p>Showing {{ paginator.showing }} or {{ paginator.total }}</p>

      <ol class="paginator">
      {%- if paginator.has_prev %}
        <li><a href="{{ url_for(endpoint, page=paginator.prev_num) }}"
         rel="me prev">«</a></li>
      {% else %}
        <li class="disabled"><span>«</span></li>
      {%- endif %}

      {%- for page in paginator.pages %}
        {% if page %}
          {% if page != paginator.page %}
            <li><a href="{{ url_for(endpoint, page=page) }}"
             rel="me">{{ page }}</a></li>
          {% else %}
            <li class="current"><span>{{ page }}</span></li>
          {% endif %}
        {% else %}
          <li><span class=ellipsis>…</span></li>
        {% endif %}
      {%- endfor %}

      {%- if paginator.has_next %}
        <li><a href="{{ url_for(endpoint, page=paginator.next_num) }}"
         rel="me next">»</a></li>
      {% else %}
        <li class="disabled"><span>»</span></li>
      {%- endif %}
      </ol>
    {% endmacro %}

How many items are displayed on which part can be controlled using the parameters of :func:`~Paginator.iter_pages`, that returns a custom iterable, similar to ``pages``.

.. sourcecode:: python

    >>> pg = Paginator(range(1, 20), page=10)
    >>> [p for p in pg.iter_pages(left_edge=2, left_current=2, right_current=5, right_edge=2)]
    [1, 2, None, 8, 9, 10, 11, 12, 13, 14, 15, None, 19, 20]
