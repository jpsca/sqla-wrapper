.. _models:

Declaring models
=============================================

Generally SQLAlchemy-Wrapper behaves like a properly configured declarative base from the :mod:`~sqlalchemy.ext.declarative` extension. As such we recommend reading the `SQLAlchemy docs <http://docs.sqlalchemy.org/en/latest/orm/tutorial.html>`_ for a full reference. However the most common use cases are also documented here.

Things to keep in mind:

-   The baseclass for all your models is called `db.Model`. It's stored on the SQLAlchemy instance you have to create. See :ref:`quickstart` for more details.
-   Some parts that are required in SQLAlchemy are optional in SQLAlchemy-Wrapper. For instance the table name is automatically set for you (unless overridden) by pluralizing the class name with the `inflection <http://inflection.readthedocs.org>`_ library. So, for example, a ``UserEmail`` model gets a table named ``user_emails``.


Simple Example
----------------------------------------------

A very simple example:

.. sourcecode:: python

    class User(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        username = db.Column(db.String(80), unique=True)
        email = db.Column(db.String(120), unique=True)

        def __init__(self, username, email, **kwargs):
            self.username = username
            self.email = email
            super(Model).__init__(self, **kwargs)

        def __repr__(self):
            return '<User %r>' % self.username

You don't need a custom `__init__` method because all your models have one that takes keyword arguments, but you can add your own `__init__` and then call the one from `db.Model` using `super`.

Use :class:`~sqlalchemy.Column` to define a column. The name of the column is the name you assign it to. If you want to use a different name in the table you can provide an optional first argument which is a string with the desired column name.

Primary keys are marked with ``primary_key=True``. Multiple keys can be marked as primary keys in which case they become a compound primary key.

The types of the column are the first argument to :class:`~sqlalchemy.Column`. You can either provide them directly or call them to further specify them (like providing a length). The following
types are the most common:

=================== =====================================
`Integer`           an integer
`String` (size)     a string with a maximum length
`Text`              some longer unicode text
`DateTime`          date and time expressed as Python
                    :mod:`~datetime.datetime` object.
`Float`             stores floating point values
`Boolean`           stores a boolean value
`LargeBinary`       stores large arbitrary binary data
=================== =====================================


One-to-Many Relationships
----------------------------------------------

The most common relationships are one-to-many relationships. Because
relationships are declared before they are established you can use strings to refer to classes that are not created yet (for instance if `Person` defines a relationship to `Article` which is declared later in the file).

Relationships are expressed with the :func:`~sqlalchemy.orm.relationship` function. However the foreign key has to be separately declared with the :class:`sqlalchemy.schema.ForeignKey` class:

.. sourcecode:: python

    class Person(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(50))
        addresses = db.relationship('Address', backref='person',
                                    lazy='dynamic')

    class Address(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        email = db.Column(db.String(50))
        person_id = db.Column(db.Integer, db.ForeignKey('person.id'))


What does ``db.relationship()`` do? That function returns a new property that can do multiple things. In this case we told it to point to the `Address` class and load multiple of those. How does it know that this will return more than one address? Because SQLAlchemy guesses a useful default from your declaration. If you would want to have a one-to-one relationship you can pass ``uselist=False`` to
:func:`~sqlalchemy.orm.relationship`.

So what do `backref` and `lazy` mean? `backref` is a simple way to also declare a new property on the `Address` class. You can then also use ``my_address.person`` to get to the person at that address. `lazy` defines when SQLAlchemy will load the data from the database:

-   ``'select'`` (which is the default) means that SQLAlchemy will load the data as necessary in one go using a standard select statement.
-   ``'joined'`` tells SQLAlchemy to load the relationship in the same query as the parent using a `JOIN` statement.
-   ``'subquery'`` works like ``'joined'`` but instead SQLAlchemy will use a subquery.
-   ``'dynamic'`` is special and useful if you have many items. Instead of loading the items SQLAlchemy will return another query object which you can further refine before loading the items. This is usually what you want if you expect more than a handful of items for this relationship.

How do you define the lazy status for backrefs? By using the
:func:`~sqlalchemy.orm.backref` function:

.. sourcecode:: python

    class User(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(50))
        addresses = db.relationship('Address',
            backref=db.backref('person', lazy='joined'), lazy='dynamic')


Many-to-Many Relationships
----------------------------------------------

If you want to use many-to-many relationships you will need to define a helper table that is used for the relationship. For this helper table it is strongly recommended to *not* use a model but an actual table:

.. sourcecode:: python

    tags = db.Table('tags',
        db.Column('tag_id', db.Integer, db.ForeignKey('tag.id')),
        db.Column('page_id', db.Integer, db.ForeignKey('page.id'))
    )

    class Page(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        tags = db.relationship('Tag', secondary=tags,
            backref=db.backref('pages', lazy='dynamic'))

    class Tag(db.Model):
        id = db.Column(db.Integer, primary_key=True)

Here we configured `Page.tags` to be a list of tags once loaded because we don't expect too many tags per page. The list of pages per tag (`Tag.pages`) however is a dynamic backref. As mentioned above this means that you will get a query object back you can use to fire a select yourself.



Mixins
----------------------------------------------

As the SQLAchemy models are Python classes, you can build them by resuing the code from other classes. In object-oriented programming, that is called a `mixin`.


.. sourcecode:: python

    class BaseMixin(object):
        id = db.Column(db.Integer, primary_key=True)

        def by_id(self, pk):
            return db.query(self.__class__).get(pk)


    class Model1(BaseMixin, db.Model):
        field = db.Column(db.Unicode)


    class Model2(BaseMixin, db.Model):
        field = db.Column(db.Unicode)


In this example `Model1` and `Model2` doesn't have to declare a primary key since is coming from the `BaseMixin`. `BaseMixin` however will not generate a table in the database because it doesn't inherit from `db.Model`.

In your models, be careful to put `db.Model` *last* in the list of inherited classes or they will not be intialized properly.

The example is very simple, but you can include in your mixins many fields, methods, validators and so on. You could even generate them dynamically.
