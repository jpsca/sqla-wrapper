import shutil
from datetime import datetime
from pathlib import Path
from tempfile import mkdtemp

import pytest

from sqla_wrapper import SQLAlchemy


@pytest.fixture()
def memdb() -> SQLAlchemy:
    return SQLAlchemy("sqlite://")


@pytest.fixture()
def dst():
    """Return a real temporary folder path which is unique to each test
    function invocation. This folder is deleted after the test has finished.
    """
    dst = mkdtemp()
    dst = Path(dst).resolve()
    yield dst
    shutil.rmtree(dst, ignore_errors=True)


@pytest.fixture(scope="session")
def db() -> SQLAlchemy:
    return SQLAlchemy(
        dialect="postgresql",
        user="postgres",
        password="postgres",
        name="dbtest",
    )


@pytest.fixture(scope="session")
def TestModelA(db):
    class TestModelA(db.Model):
        __tablename__ = "test_model_a"
        id = db.Column(db.Integer, primary_key=True)
        title = db.Column(db.String(50), nullable=False, unique=True)
        created_at = db.Column(db.DateTime, default=datetime.utcnow)

    return TestModelA


@pytest.fixture(scope="session")
def TestModelB(db):
    class TestModelB(db.Model):
        __tablename__ = "test_model_b"
        id = db.Column(db.Integer, primary_key=True)
        title = db.Column(db.String(50), nullable=False, unique=True)

    return TestModelB


@pytest.fixture(scope="session")
def dbsetup(db, TestModelA, TestModelB):
    db.drop_all()
    db.create_all()
    with db.Session() as dbs:
        dbs.create(TestModelB, title="first")
        dbs.commit()
    yield
    db.drop_all()


@pytest.fixture()
def dbs(db, dbsetup):
    tt = db.test_transaction(savepoint=True)
    yield db.s
    tt.close()
