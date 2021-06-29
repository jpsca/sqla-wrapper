import pytest

from sqla_wrapper import SQLAlchemy


@pytest.fixture
def db():
    return SQLAlchemy("sqlite://")
