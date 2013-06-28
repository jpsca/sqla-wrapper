==========
O.R.M.
==========

A framework-independent wrapper for SQLAlchemy that makes it really easy and fun to use.

Example:

.. sourcecode:: python

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

It does an automatic table naming (if no name is defined) by pluralizing the class name using the `inflector` library. So, for example, a `User` model gets a table named `users`.

