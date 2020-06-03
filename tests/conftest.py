import pytest

from sqla_wrapper import SQLAlchemy


@pytest.fixture(scope="session")
def uri1():
    return "sqlite://"


@pytest.fixture(scope="session")
def uri2():
    return "sqlite://"


@pytest.fixture
def db(uri1):
    return SQLAlchemy(uri1)
