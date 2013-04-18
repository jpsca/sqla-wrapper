
# O.R.M.

[![Build Status](https://travis-ci.org/lucuma/orm.png)](https://travis-ci.org/lucuma/orm)

A framework-independent wrapper for SQLAlchemy that makes it really easy and fun to use.

Example:

```python
from orm import SQLALchemy

db = SQLALchemy('postgresql://scott:tiger@localhost:5432/mydatabase')

class ToDo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(60), nullable=False)
    done = db.Column(db.Boolean, nullable=False, default=False)
    pub_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

to_do = ToDo(title='Install orm', done=True)
db.add(to_do)
db.commit()

all_todos = db.query(ToDo).order_by(Todo.pub_date.desc()).all()

```

It does an automatic table naming (if no name is defined) and, to the
base query class.


## How to use

The SQLAlchemy class is used to instantiate a SQLAlchemy connection to
a database.

```python
db = SQLAlchemy(_uri_to_database_)
```

The class also provides access to all the SQLAlchemy
functions from the `sqlalchemy` and `sqlalchemy.orm` modules.
So you can declare models like this:

```python
class User(db.Model):
    login = db.Column(db.String(80), unique=True)
    passw_hash = db.Column(db.String(80))
```

In a web application you need to call `db.session.remove()` after each response, and `db.session.rollback()` if an error occurs. However, if your application object has an `after_request` and/or an `on_exception`
decorator, just pass it to automatically make that binding. It works with Bottle's `hook` too.

```python
app = Flask(__name__)
db = SQLAlchemy('sqlite://', app=app)
```

or:

```python
db = SQLAlchemy()

app = Flask(__name__)
db.init_app(app)
```

## More examples

### Many databases, one web app

```python
app = Flask(__name__)
db1 = SQLAlchemy(URI1, app)
db2 = SQLAlchemy(URI1, app)
```

### Many web apps, one database

```python
db = SQLAlchemy(URI1)

app1 = Flask(__name__)
app2 = Flask(__name__)
db.init_app(app1)
db.init_app(app2)
```

### Aggegated selects

```python
res = db.query(db.func.sum(Unit.price).label('price')).all()
print res.price
```


---------------------------------------
[MIT License] (http://www.opensource.org/licenses/mit-license.php).

© 2013 by [Lúcuma labs] (http://lucumalabs.com).
