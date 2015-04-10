.. _queries:
.. currentmodule:: sqlalchemy_wrapper

Select, Insert, Delete and other Queries
=============================================


Now that you have :ref:`declared models <models>` it's time to query the the database. We will be using the model definitions from the
:ref:`quickstart` chapter.


Inserting Records
----------------------------------------------

Before we can query something we will have to insert some data. Inserting data into the database is a three step process:

1. Create the Python object
2. Add it to the session
3. Commit the session

The session here is essentially a beefed up version of a database transaction. This is how it works:

.. sourcecode:: python

    >>> from yourapp import User
    >>> me = User('admin', 'admin@example.com')
    >>> db.add(me)
    >>> db.commit()

Alright, that was not hard. What happens at what point? Before you add the object to the session, SQLAlchemy basically does not plan on adding it to the transaction. That is good because you can still discard the changes. For example think about creating the post at a page but you only want to pass the post to the template for preview rendering instead of storing it in the database.

The :func:`~sqlalchemy.orm.session.Session.add` function call then adds the object. It will issue an `INSERT` statement for the database but because the transaction is still not committed you won't get an ID back immediately. If you do the commit, your user will have an ID:

.. sourcecode:: python

    >>> me.id
    1


Deleting Records
----------------------------------------------

Deleting records is very similar, instead of
:func:`~sqlalchemy.orm.session.Session.add` use
:func:`~sqlalchemy.orm.session.Session.delete`:

.. sourcecode:: python

    >>> db.delete(me)
    >>> db.commit()


Querying Records
----------------------------------------------

So how do we get data back out of our database? For this
SQLAlchemy-Wrapper provides a :attr:`~SQLALchemy.query` attribute. When you call it whith your :class:`Model` class you will get back a new query object over all records. You can then use methods like
:func:`~sqlalchemy.orm.query.Query.filter` to filter the records before you fire the select with :func:`~sqlalchemy.orm.query.Query.all` or :func:`~sqlalchemy.orm.query.Query.first`.

If you want to go by primary key you can also use :func:`~sqlalchemy.orm.query.Query.get`.

The following queries assume following entries in the database:

=========== =========== =====================
`id`        `username`  `email`
1           admin       admin@example.com
2           peter       peter@example.org
3           guest       guest@example.com
=========== =========== =====================

Retrieve a user by username:

.. sourcecode:: python

    >>> peter = db.query(User).filter_by(username='peter').first()
    >>> peter.id
    1
    >>> peter.email
    u'peter@example.org'

Same as above but for a non existing username gives `None`:

.. sourcecode:: python

    >>> missing = db.query(User).filter_by(username='missing').first()
    >>> missing is None
    True

Selecting a bunch of users by a more complex expression:

.. sourcecode:: python

    >>> db.query(User).filter(User.email.endswith('@example.com')).all()
    [<User u'admin'>, <User u'guest'>]

Ordering users by something:

.. sourcecode:: python

    >>> db.query(User).order_by(User.username)
    [<User u'admin'>, <User u'guest'>, <User u'peter'>]

Limiting the number of users returned:

.. sourcecode:: python

    >>> db.query(User).limit(1).all()
    [<User u'admin'>]

Getting user by primary key:

.. sourcecode:: python

    >>> db.query(User).get(1)
    <User u'admin'>

Getting the bigger id:

.. sourcecode:: python

    >>> db.query(db.func.max(User.id)).scalar()
    3


Queries in Views
----------------------------------------------

If you write a view function it's often very handy to return a 404
error (or some other error) for missing entries. Because this is a very common idiom, SQLAlchemy-Wrapper provides a helper for this exact purpose.

Instead of :meth:`~sqlalchemy.orm.query.Query.get` one can use :meth:`~Query.get_or_error` and instead of :meth:`~sqlalchemy.orm.query.Query.first`, :meth:`~Query.first_or_error`.
This will raise the error you give to it instead of returning `None`:

.. sourcecode:: python

    from werkzeug.exceptions import NotFound

    @app.route('/user/<username>')
    def show_user(username):
        user = db.query(User).filter_by(username=username).first_or_error(NotFound)
        return render_template('show_user.html', user=user)

