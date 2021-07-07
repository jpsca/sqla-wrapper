from sqlalchemy import *  # noqa
from sqla_wrapper import Alembic


def _create_test_model1(db):
    class TestModel1(db.Model):
        __tablename__ = "test_model_1"
        id = Column(Integer, primary_key=True)
        name = Column(String(50), nullable=False)

    return TestModel1


def _create_test_model2(db):
    class TestModel2(db.Model):
        __tablename__ = "test_model_2"
        id = Column(Integer, primary_key=True)
        name = Column(String(50), nullable=False)

    return TestModel2


def test_mkdir(db, dst):
    script_path = dst / "migrations"
    Alembic(db, script_path=script_path, init=True)
    assert script_path.is_dir()
    assert (script_path / "script.py.mako").is_file()


def test_no_mkdir(db, dst):
    script_path = dst / "migrations"
    script_path.mkdir()
    tmpl_path = script_path / "script.py.mako"
    tmpl_path.touch()

    Alembic(db, script_path=script_path, init=False)
    assert script_path.is_dir()
    assert tmpl_path.is_file()


def test_mkdir_exists(db, dst):
    script_path = dst / "migrations"
    script_path.mkdir()
    tmpl_path = script_path / "script.py.mako"
    tmpl_path.touch()

    Alembic(db, script_path=script_path, init=True)
    assert script_path.is_dir()
    assert tmpl_path.is_file()


def test_revision(db, dst):
    _create_test_model1(db)
    alembic = Alembic(db, script_path=dst, init=True, file_template="%%(rev)s_%%(slug)s")
    alembic.rev_id = lambda: "1234"
    alembic.revision("test")

    revpath = dst / "1234_test.py"
    assert revpath.is_file()
    rev_src = revpath.read_text()
    assert "revision = '1234'" in rev_src
    assert "op.create_table" in rev_src


def test_empty_revision(db, dst):
    _create_test_model1(db)
    alembic = Alembic(db, script_path=dst, init=True, file_template="%%(rev)s_%%(slug)s")
    alembic.rev_id = lambda: "1234"
    alembic.revision("test", empty=True)

    revpath = dst / "1234_test.py"
    rev_src = revpath.read_text()
    assert "op.create_table" not in rev_src


def test_head(db, dst):
    _create_test_model1(db)
    alembic = Alembic(db, script_path=dst, init=True)
    alembic.revision("test1")
    alembic.upgrade()
    _create_test_model2(db)
    rev2 = alembic.revision("test2")

    assert alembic.head() == rev2


def test_upgrade(db, dst):
    _create_test_model1(db)
    alembic = Alembic(db, script_path=dst, init=True)
    rev1 = alembic.revision("test1")

    assert alembic.current() is None
    alembic.upgrade()
    assert alembic.current() == rev1


def test_upgrade_sql(db, dst, capsys):
    _create_test_model1(db)
    alembic = Alembic(db, script_path=dst, init=True)
    alembic.revision("test1")
    alembic.upgrade(":head", sql=True)

    stdout, _ = capsys.readouterr()
    assert "CREATE TABLE test_model_1" in stdout


def test_downgrade(db, dst):
    _create_test_model1(db)
    alembic = Alembic(db, script_path=dst, init=True)
    rev1 = alembic.revision("test1")
    alembic.upgrade()
    _create_test_model2(db)
    rev2 = alembic.revision("test2")
    alembic.upgrade()

    assert alembic.current() == rev2
    alembic.downgrade()
    assert alembic.current() == rev1
    alembic.upgrade()
    alembic.downgrade(-2)
    assert alembic.current() is None
    alembic.upgrade()
    assert alembic.current() == rev2
    alembic.downgrade(1)
    assert alembic.current() == rev1


def test_downgrade_sql(db, dst, capsys):
    _create_test_model1(db)
    alembic = Alembic(db, script_path=dst, init=True)
    rev1 = alembic.revision("test1")
    alembic.upgrade()
    alembic.downgrade(f"{rev1.revision}:-1", sql=True)

    stdout, _ = capsys.readouterr()
    assert "DROP TABLE test_model_1" in stdout


def test_history(db, dst):
    _create_test_model1(db)
    alembic = Alembic(db, script_path=dst, init=True)
    rev1 = alembic.revision("test1")
    alembic.upgrade()
    _create_test_model2(db)
    rev2 = alembic.revision("test2")

    assert alembic.history() == [rev1, rev2]
    assert alembic.history(end="current") == [rev1]
    alembic.upgrade()
    assert alembic.history(start="current") == [rev2]


def test_stamp(db, dst):
    _create_test_model1(db)
    alembic = Alembic(db, script_path=dst, init=True)
    rev1 = alembic.revision("test1")
    alembic.stamp()
    assert alembic.current() == rev1


def test_stamp_sql(db, dst, capsys):
    _create_test_model1(db)
    alembic = Alembic(db, script_path=dst, init=True)
    rev1 = alembic.revision("test1")
    alembic.stamp(sql=True)

    stdout, _ = capsys.readouterr()
    stmt = f"INSERT INTO alembic_version (version_num) VALUES ('{rev1.revision}');"
    assert stmt in stdout
    assert "CREATE TABLE test_model_1" not in stdout
