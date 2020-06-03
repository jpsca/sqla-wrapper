import mock
import pytest
from sqlalchemy import pool
from sqlalchemy.orm import Query

from sqla_wrapper import SQLAlchemy


def create_test_model(db):
    class ToDo(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        title = db.Column(db.String(60), nullable=False)
        text = db.Column(db.Text)
        done = db.Column(db.Boolean, nullable=False, default=False)

        def __init__(self, title, text):
            self.title = title
            self.text = text

    return ToDo


def test_query(db):
    ToDo = create_test_model(db)
    db.create_all()

    db.add(ToDo("First", "The text"))
    db.add(ToDo("Second", "The text"))
    db.flush()

    titles = " ".join(x.title for x in db.query(ToDo).all())
    assert titles == "First Second"

    data = db.query(ToDo).filter(ToDo.title == "First").all()
    assert len(data) == 1


def test_api(db):
    assert db.metadata == db.Model.metadata
    assert db.query
    assert callable(db.drop_all)
    assert callable(db.rollback)
    assert callable(db.add)
    assert callable(db.add_all)
    assert callable(db.begin)
    assert callable(db.begin_nested)
    assert callable(db.commit)
    assert callable(db.connection)
    assert callable(db.delete)
    assert callable(db.execute)
    assert callable(db.expire)
    assert callable(db.expire_all)
    assert callable(db.expunge)
    assert callable(db.expunge_all)
    assert callable(db.flush)
    assert callable(db.invalidate)
    assert callable(db.is_modified)
    assert callable(db.merge)
    assert callable(db.prepare)
    assert callable(db.prune)
    assert callable(db.refresh)
    assert callable(db.rollback)
    assert callable(db.scalar)


def test_multiple_databases(uri1, uri2):
    db1 = SQLAlchemy(uri1)
    db2 = SQLAlchemy(uri2)
    ToDo1 = create_test_model(db1)
    ToDo2 = create_test_model(db2)
    db1.create_all()
    db2.create_all()

    db1.add(ToDo1("A", "a"))
    db1.add(ToDo1("B", "b"))
    db2.add(ToDo2("Q", "q"))
    db1.add(ToDo1("C", "c"))
    db1.commit()
    db2.commit()

    assert db1.query(ToDo1).count() == 3
    assert db2.query(ToDo2).count() == 1


def test_repr(uri1):
    db = SQLAlchemy(uri1)
    assert str(db) == f"<SQLAlchemy('{uri1}')>"


def test_aggregated_query(db):
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

    res = db.query(db.func.sum(Unit.price).label("price")).first()
    assert res.price == 43


def test_session_options(uri1):
    class _CustomPool(pool.StaticPool):
        _do_return_conn = mock.MagicMock()

    db = SQLAlchemy(uri1, poolclass=_CustomPool)
    db.create_all()

    _CustomPool._do_return_conn.assert_called_once()


def test_reconfigure(uri1):
    db = SQLAlchemy(uri1, echo=False)

    class Bucket(db.Model):
        id = db.Column(db.Integer, primary_key=True)

    db.create_all()
    db.add(Bucket())
    db.commit()

    class CustomQuery(Query):
        some_attr = 1

    db.reconfigure(query_cls=CustomQuery)
    assert isinstance(db.query(Bucket), CustomQuery)
    assert db.query(Bucket).some_attr == 1


def test_drop_all(db):
    ToDo = create_test_model(db)
    db.create_all()
    db.drop_all()

    with pytest.raises(Exception):
        db.query(ToDo).count()
