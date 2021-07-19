import pytest
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
    alembic = Alembic(
        db, script_path=dst, init=True, file_template="%%(rev)s_%%(slug)s"
    )
    alembic._rev_id = lambda: "1234"
    alembic.revision("test")

    revpath = dst / "1234_test.py"
    assert revpath.is_file()
    rev_src = revpath.read_text()
    assert "revision = '1234'" in rev_src
    assert "op.create_table" in rev_src


def test_empty_revision(db, dst):
    _create_test_model1(db)
    alembic = Alembic(
        db, script_path=dst, init=True, file_template="%%(rev)s_%%(slug)s"
    )
    alembic._rev_id = lambda: "1234"
    alembic.revision("test", empty=True)

    revpath = dst / "1234_test.py"
    rev_src = revpath.read_text()
    assert "op.create_table" not in rev_src


def test_upgrade(db, dst):
    _create_test_model1(db)
    alembic = Alembic(db, script_path=dst, init=True)
    rev1 = alembic.revision("test1")

    assert alembic._current() is None
    alembic.upgrade()
    assert alembic._current() == rev1


def test_upgrade_sql(db, dst, capsys):
    _create_test_model1(db)
    alembic = Alembic(db, script_path=dst, init=True)
    alembic.revision("test1")
    alembic.upgrade(":head", sql=True)

    stdout, _ = capsys.readouterr()
    assert "CREATE TABLE test_model_1" in stdout


def test_upgrade_range_no_sql(db, dst):
    _create_test_model1(db)
    alembic = Alembic(db, script_path=dst, init=True)
    alembic.revision("test1")

    with pytest.raises(ValueError):
        alembic.upgrade(":head", sql=False)


def test_upgrade_sql_no_range(db, dst):
    _create_test_model1(db)
    alembic = Alembic(db, script_path=dst, init=True)
    alembic.revision("test1")

    with pytest.raises(ValueError):
        alembic.upgrade("head", sql=True)


def test_downgrade(db, dst):
    _create_test_model1(db)
    alembic = Alembic(db, script_path=dst, init=True)
    rev1 = alembic.revision("test1")
    alembic.upgrade()
    _create_test_model2(db)
    rev2 = alembic.revision("test2")
    alembic.upgrade()

    assert alembic._current() == rev2
    alembic.downgrade()
    assert alembic._current() == rev1
    alembic.upgrade()
    alembic.downgrade(-2)
    assert alembic._current() is None
    alembic.upgrade()
    assert alembic._current() == rev2
    alembic.downgrade(1)
    assert alembic._current() == rev1


def test_downgrade_sql(db, dst, capsys):
    _create_test_model1(db)
    alembic = Alembic(db, script_path=dst, init=True)
    rev1 = alembic.revision("test1")
    alembic.upgrade()
    alembic.downgrade(f"{rev1.revision}:-1", sql=True)

    stdout, _ = capsys.readouterr()
    assert "DROP TABLE test_model_1" in stdout


def test_downgrade_range_no_sql(db, dst):
    _create_test_model1(db)
    alembic = Alembic(db, script_path=dst, init=True)
    rev1 = alembic.revision("test1")
    alembic.upgrade()

    with pytest.raises(ValueError):
        alembic.downgrade(f"{rev1.revision}:-1", sql=False)


def test_downgrade_sql_no_range(db, dst):
    _create_test_model1(db)
    alembic = Alembic(db, script_path=dst, init=True)
    alembic.revision("test1")
    alembic.upgrade()

    with pytest.raises(ValueError):
        alembic.downgrade("-1", sql=True)


def test_get_history(db, dst):
    _create_test_model1(db)
    alembic = Alembic(db, script_path=dst, init=True)
    rev1 = alembic.revision("test1")
    alembic.upgrade()
    _create_test_model2(db)
    rev2 = alembic.revision("test2")

    assert alembic._history() == [rev1, rev2]
    assert alembic._history(end="current") == []
    alembic.upgrade()
    assert alembic._history(start="current") == [rev1, rev2]


def test_print_history(db, dst, capsys):
    _create_test_model1(db)
    alembic = Alembic(db, script_path=dst, init=True)
    rev1 = alembic.revision("test1")
    alembic.upgrade()
    _create_test_model2(db)
    rev2 = alembic.revision("test2")

    alembic.history()
    stdout, _ = capsys.readouterr()
    assert f"<base> -> {rev1.revision}, test1\n" in stdout
    assert f"{rev1.revision} -> {rev2.revision} (head), test2" in stdout


def test_print_history_verbose(db, dst, capsys):
    _create_test_model1(db)
    alembic = Alembic(db, script_path=dst, init=True)
    rev1 = alembic.revision("test1")
    alembic.upgrade()
    _create_test_model2(db)
    rev2 = alembic.revision("test2")

    alembic.history(verbose=True)
    stdout, _ = capsys.readouterr()
    assert f"Rev: {rev1.revision}\nParent: <base>\n" in stdout
    assert f"Rev: {rev2.revision} (head)\nParent: {rev1.revision}\n" in stdout


def test_stamp(db, dst):
    _create_test_model1(db)
    alembic = Alembic(db, script_path=dst, init=True)
    rev1 = alembic.revision("test1")
    alembic.stamp()
    assert alembic._current() == rev1


def test_stamp_sql(db, dst, capsys):
    _create_test_model1(db)
    alembic = Alembic(db, script_path=dst, init=True)
    rev1 = alembic.revision("test1")
    alembic.stamp(sql=True)

    stdout, _ = capsys.readouterr()
    stmt = f"INSERT INTO alembic_version (version_num) VALUES ('{rev1.revision}');"
    assert stmt in stdout
    assert "CREATE TABLE test_model_1" not in stdout


def test_print_current(db, dst, capsys):
    _create_test_model1(db)
    alembic = Alembic(db, script_path=dst, init=True)
    rev1 = alembic.revision("test1")
    alembic.upgrade()
    _create_test_model2(db)
    alembic.revision("test2")

    alembic.current()
    stdout, _ = capsys.readouterr()
    assert f"<base> -> {rev1.revision}, test1\n" in stdout


def test_print_current_verbose(db, dst, capsys):
    _create_test_model1(db)
    alembic = Alembic(db, script_path=dst, init=True)
    rev1 = alembic.revision("test1")
    alembic.upgrade()
    _create_test_model2(db)
    alembic.revision("test2")

    alembic.current(verbose=True)
    stdout, _ = capsys.readouterr()
    assert f"Rev: {rev1.revision}\nParent: <base>\n" in stdout


def test_no_current(db, dst, capsys):
    alembic = Alembic(db, script_path=dst, init=True)
    alembic.current()
    stdout, _ = capsys.readouterr()
    assert not stdout


def test_get_head(db, dst):
    _create_test_model1(db)
    alembic = Alembic(db, script_path=dst, init=True)
    alembic.revision("test1")
    alembic.upgrade()
    _create_test_model2(db)
    rev2 = alembic.revision("test2")

    assert alembic._head() == rev2


def test_print_head(db, dst, capsys):
    _create_test_model1(db)
    alembic = Alembic(db, script_path=dst, init=True)
    rev1 = alembic.revision("test1")
    alembic.upgrade()
    _create_test_model2(db)
    rev2 = alembic.revision("test2")

    alembic.head()
    stdout, _ = capsys.readouterr()
    assert f"{rev1.revision} -> {rev2.revision} (head), test2" in stdout


def test_print_head_verbose(db, dst, capsys):
    _create_test_model1(db)
    alembic = Alembic(db, script_path=dst, init=True)
    rev1 = alembic.revision("test1")
    alembic.upgrade()
    _create_test_model2(db)
    rev2 = alembic.revision("test2")

    alembic.head(verbose=True)
    stdout, _ = capsys.readouterr()
    assert f"Rev: {rev2.revision} (head)\nParent: {rev1.revision}\n" in stdout


def test_no_head(db, dst, capsys):
    alembic = Alembic(db, script_path=dst, init=True)
    alembic.head()
    stdout, _ = capsys.readouterr()
    assert not stdout


def test_get_pyceo_cli(db, dst):
    alembic = Alembic(db, script_path=dst, init=True)
    alembic.get_pyceo_cli()


def test_get_click_cli(db, dst):
    alembic = Alembic(db, script_path=dst, init=True)
    alembic.get_click_cli()
