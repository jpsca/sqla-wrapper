============
ORM |travis|
============

.. |travis| image:: https://travis-ci.org/lucuma/orm.png
   :alt: Build Status
   :target: https://travis-ci.org/lucuma/orm

A framework-independent wrapper for SQLAlchemy that makes it really easy and fun to use.

Works with Python 2.6, 2.7, 3.3, 3.4 and pypy.

Example:

.. code:: python

    from orm import SQLALchemy

    db = SQLALchemy('postgresql://scott:tiger@localhost:5432/mydatabase')

    class ToDo(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        title = db.Column(db.String(60), nullable=False)
        done = db.Column(db.Boolean, nullable=False, default=False)
        pub_date = db.Column(db.DateTime, nullable=False,
            default=datetime.utcnow)

    to_do = ToDo(title='Install orm', done=True)
    db.add(to_do)
    db.commit()

    completed = db.query(ToDo).order_by(Todo.pub_date.desc()).all()


It does an automatic table naming (if no table name is already defined using the ``__tablename__`` property) by pluralizing the class name with the `inflection <http://inflection.readthedocs.org>`_ library. So, for example, a ``User`` model gets a table named ``users``.


How to use
========================

The SQLAlchemy class is used to instantiate a SQLAlchemy connection to
a database.

.. code:: python

    db = SQLAlchemy(_uri_to_database_)


The class also provides access to all the SQLAlchemy
functions from the ``sqlalchemy`` and ``sqlalchemy.orm`` modules.
So you can declare models like this:

.. code:: python

    class User(db.Model):
        login = db.Column(db.String(80), unique=True)
        passw_hash = db.Column(db.String(80))
        profile_id = db.Column(db.Integer, db.ForeignKey(Profile.id))
        profile = db.relationship(Profile, backref=db.backref('user'))


In a web application you need to call ``db.session.remove()`` after each response, and ``db.session.rollback()`` if an error occurs. However, if you are using Flask or other framework that uses the `after_request` and ``on_exception`` decorators, these bindings it is done automatically (this works with Bottle's ``hook`` too):

.. code:: python

    app = Flask(__name__)

    db = SQLAlchemy('sqlite://', app=app)

or

.. code:: python

    db = SQLAlchemy()

    app = Flask(__name__)

    db.init_app(app)


More examples
------------------------

Many databases, one web app
`````````````````````````````

.. code:: python

    app = Flask(__name__)
    db1 = SQLAlchemy(URI1, app)
    db2 = SQLAlchemy(URI2, app)


Many web apps, one database
`````````````````````````````

.. code:: python

    db = SQLAlchemy(URI1)

    app1 = Flask(__name__)
    app2 = Flask(__name__)
    db.init_app(app1)
    db.init_app(app2)


Aggegated selects
`````````````````````````````

.. code:: python

    res = db.query(db.func.sum(Unit.price).label('price')).all()
    print res.price


Mixins
`````````````````````````````

.. code:: python

    class IDMixin(object):
        id = db.Column(db.Integer, primary_key=True)

    class Model(IDMixin, db.Model):
        field = db.Column(db.Unicode)


Pagination
------------------------

All the results can be easily paginated

.. code:: python

    users = db.query(User).paginate(page=2, per_page=20)
    print(list(users))  # [User(21), User(22), User(23), ... , User(40)]


The paginator object it's an iterable that returns only the results for that page, so you use it in your templates in the same way than the original result:

.. code:: html+jinja

    {% for item in paginated_items %}
        <li>{{ item.name }}</li>
    {% endfor %}


Rendering the pages
`````````````````````````````

Below your results is common that you want it to render the list of pages.

The ``paginator.pages`` property is an iterator that returns the page numbers, but sometimes not all of them: if there are more than 11 pages, the result will be one of these, depending of what is the current page:


.. image:: docs/_static/paginator1.png
   :class: center

.. image:: docs/_static/paginator2.png
   :class: center

.. image:: docs/_static/paginator3.png
   :class: center


Skipped page numbers are represented as ``None``.

How many items are displayed can be controlled calling ``paginator.iter_pages`` instead.

This is one way how you could render such a pagination in your templates:

.. sourcecode:: html+jinja

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

______

:copyright: © 2012 by `Juan Pablo Scaletti <http://jpscaletti.com>`_.
:license: BSD, see LICENSE for more details.
