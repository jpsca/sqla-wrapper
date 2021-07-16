import shutil
from pathlib import Path
from tempfile import mkdtemp
from typing import Any, Optional

import pytest

from sqla_wrapper import SQLAlchemy
from sqlalchemy import Column, Integer, String, event, text
from sqlalchemy.orm import Session


@pytest.fixture()
def db() -> SQLAlchemy:
    return SQLAlchemy("sqlite://")


@pytest.fixture()
def dst() -> Optional[Path]:
    """Return a real temporary folder path which is unique to each test
    function invocation. This folder is deleted after the test has finished.
    """
    dst = mkdtemp()
    dst = Path(dst).resolve()
    yield dst
    shutil.rmtree(dst, ignore_errors=True)


@pytest.fixture(scope="session")
def _db() -> SQLAlchemy:
    db = SQLAlchemy(
        dialect="postgresql",
        user="postgres",
        password="postgres",
        name="dbtest",
    )
    return db


@pytest.fixture(scope="session")
def TestModelA(_db: SQLAlchemy) -> Any:
    class TestModelA(_db.Model):
        __tablename__ = "test_model_a"
        id = Column(Integer, primary_key=True)
        title = Column(String(50), nullable=False, unique=True)

        def __repr__(self):
            return f"<TestModelA #{self.id} title='{self.title}'>"

    return TestModelA


@pytest.fixture(scope="session")
def TestModelB(_db: SQLAlchemy) -> Any:
    class TestModelB(_db.Model):
        __tablename__ = "test_model_b"
        id = Column(Integer, primary_key=True)
        title = Column(String(50), nullable=False, unique=True)

        def __repr__(self):
            return f"<TestModelB #{self.id} title='{self.title}'>"

    return TestModelB


@pytest.fixture(scope="session")
def _dbsetup(_db: SQLAlchemy, TestModelA: Any, TestModelB: Any) -> None:
    _db.create_all()
    TestModelB.create(_db.session, title="first")
    _db.session.commit()
    yield
    _db.drop_all()


@pytest.fixture()
def dbs(_db: SQLAlchemy, _dbsetup: None) -> Session:
    tt = _db.test_transaction(savepoint=True)
    yield tt.session
    tt.close()
