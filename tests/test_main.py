# coding=utf-8
from datetime import datetime
import mock
import pytest

from sqlalchemy_wrapper import SQLAlchemy


URI1 = 'sqlite://'
URI2 = 'sqlite://'


def create_test_model(db):

    class ToDo(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        title = db.Column(db.String(60), nullable=False)
        text = db.Column(db.Text)
        done = db.Column(db.Boolean, nullable=False, default=False)
        pub_date = db.Column(db.DateTime, nullable=False,
                             default=datetime.utcnow)

        def __init__(self, title, text):
            self.title = title
            self.text = text

    return ToDo


def test_define_table():
    db = SQLAlchemy(URI1)
    db.Table('foobar',
             db.Column('foo', db.UnicodeText),
             db.Column('bar', db.UnicodeText))
    db.Table('fizzbuzz', db.metadata,
             db.Column('fizz', db.Integer),
             db.Column('buzz', db.Integer))
    db.create_all()


def test_init_app():
    class FakeApp(object):
        pass

    app = FakeApp()
    db = SQLAlchemy(URI1, app)
    assert app.databases
    db.init_app(app)
    assert len(app.databases) == 1


def test_flask_hooks_0_9():
    teardown_appcontext_spy = mock.Mock()

    class AppWithTearDownAppContext(object):
        def teardown_appcontext(self, f):
            teardown_appcontext_spy()

    app = AppWithTearDownAppContext()
    SQLAlchemy(URI1, app=app)
    assert teardown_appcontext_spy.call_count


def test_flask_hooks_0_8():
    teardown_request_spy = mock.Mock()

    class AppWithTearDownRequest(object):
        def teardown_request(self, f):
            teardown_request_spy()

    app = AppWithTearDownRequest()
    SQLAlchemy(URI1, app=app)
    assert teardown_request_spy.call_count


def test_flask_hooks_old():
    after_request_spy = mock.Mock()
    on_exception_spy = mock.Mock()

    class App(object):
        def after_request(self, f):
            after_request_spy()

        def on_exception(self, f):
            on_exception_spy()

    app = App()
    SQLAlchemy(URI1, app=app)
    assert after_request_spy.call_count
    assert on_exception_spy.call_count


def test_bottle_hooks():
    hook_spy = mock.Mock()

    class App(object):
        def hook(self, name):
            def decorator(f):
                hook_spy()
            return decorator

    app = App()
    SQLAlchemy(URI1, app=app)
    assert hook_spy.call_count


def test_query():
    db = SQLAlchemy(URI1)
    ToDo = create_test_model(db)
    db.create_all()

    db.add(ToDo('First', 'The text'))
    db.add(ToDo('Second', 'The text'))
    db.flush()

    titles = ' '.join(x.title for x in db.query(ToDo).all())
    assert titles == 'First Second'

    data = db.query(ToDo).filter(ToDo.title == 'First').all()
    assert len(data) == 1


def test_api():
    db = SQLAlchemy()
    assert db.metadata == db.Model.metadata
    db.drop_all()
    db.reflect()
    db.rollback()


def test_model_helpers():
    db = SQLAlchemy()

    class Row(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(60), nullable=False)
        created_at = db.Column(db.DateTime, nullable=False,
                               default=datetime.utcnow)

    db.create_all()
    db.add(Row(name='a'))
    db.flush()
    row = db.query(Row).first()

    assert str(row) == '<Row>'
    assert dict(row)['name'] == 'a'


def test_driver_hacks():
    with pytest.raises(ValueError):
        SQLAlchemy('sqlite://', pool_size=0)


def test_multiple_databases():
    db1 = SQLAlchemy(URI1)
    db2 = SQLAlchemy(URI2)
    ToDo1 = create_test_model(db1)
    ToDo2 = create_test_model(db2)
    db1.create_all()
    db2.create_all()

    db1.add(ToDo1('A', 'a'))
    db1.add(ToDo1('B', 'b'))
    db2.add(ToDo2('Q', 'q'))
    db1.add(ToDo1('C', 'c'))
    db1.commit()
    db2.commit()

    assert db1.query(ToDo1).count() == 3
    assert db2.query(ToDo2).count() == 1


def test_repr():
    db = SQLAlchemy(URI1)
    assert str(db) == "<SQLAlchemy('%s')>" % URI1


def test_aggregated_query():
    db = SQLAlchemy(URI1)

    class Unit(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(60))
        price = db.Column(db.Integer)

    db.create_all()
    db.add(Unit(price=25))
    db.add(Unit(price=5))
    db.add(Unit(price=10))
    db.add(Unit(price=3))
    db.commit()

    res = db.query(db.func.sum(Unit.price).label('price')).first()
    assert res.price == 43


def test_id_mixin():
    db = SQLAlchemy(URI1)

    class IDMixin(object):
        id = db.Column(db.Integer, primary_key=True)

    class Model(db.Model, IDMixin):
        field = db.Column(db.String)

    db.create_all()

    assert Model.__tablename__ == 'models'
    assert hasattr(Model, 'id')


def test_get_engine():
    class FakeApp(object):
        pass

    app1 = FakeApp()
    app2 = FakeApp()
    db = SQLAlchemy(URI1, app=app1)

    assert SQLAlchemy().get_engine(app1) == db.engine
    assert SQLAlchemy().get_engine(app2) is None
