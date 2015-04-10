:orphan:

=============================================
SQLAlchemy-Wrapper
=============================================

.. container:: lead

    A friendly wrapper for SQLAlchemy.


Works with Python 2.7, 3.3+ and pypy.

Example:

.. code-block:: python

    from sqlalchemy_wrapper import SQLAlchemy

    db = SQLALchemy('postgresql://scott:tiger@localhost:5432/mydb')

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


SQLAlchemy-Wrapper was forked from `Flask-SQLAlchemy <https://pythonhosted.org/Flask-SQLAlchemy/>`_. Read about the goals of the project in the :ref:`about` section.


.. include:: contents.rst.inc
