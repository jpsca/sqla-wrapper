import shutil
from pathlib import Path
from tempfile import mkdtemp

import pytest

from sqla_wrapper import SQLAlchemy


@pytest.fixture()
def db():
    return SQLAlchemy("sqlite://")


@pytest.fixture()
def dst(request):
    """Return a real temporary folder path which is unique to each test
    function invocation. This folder is deleted after the test has finished.
    """
    dst = mkdtemp()
    dst = Path(dst).resolve()
    request.addfinalizer(lambda: shutil.rmtree(dst, ignore_errors=True))
    return dst
