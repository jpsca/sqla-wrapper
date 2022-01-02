import pytest
from sqlalchemy import select

from sqla_wrapper import Alembic


def _create_test_model1(memdb):
    class TestModel1(memdb.Model):
        __tablename__ = "test_model_1"
        id = memdb.Column(memdb.Integer, primary_key=True)
        name = memdb.Column(memdb.String(50), nullable=False)

    return TestModel1


def _create_test_model2(memdb):
    class TestModel2(memdb.Model):
        __tablename__ = "test_model_2"
        id = memdb.Column(memdb.Integer, primary_key=True)
        name = memdb.Column(memdb.String(50), nullable=False)

    return TestModel2


def test_autoinit(memdb, dst):
    path = dst / "migrations"
    Alembic(memdb, path=path)
    assert path.is_dir()
    assert (path / "script.py.mako").is_file()


def test_autoinit_exists(memdb, dst):
    path = dst / "migrations"
    path.mkdir()
    tmpl_path = path / "script.py.mako"
    tmpl_path.touch()

    Alembic(memdb, path=path)
    assert path.is_dir()
    assert tmpl_path.is_file()


def test_revision(memdb, dst):
    _create_test_model1(memdb)
    alembic = Alembic(
        memdb, path=dst, file_template="%%(rev)s_%%(slug)s"
    )
    alembic.rev_id = lambda: "1234"
    alembic.revision("test")

    revpath = dst / "1234_test.py"
    assert revpath.is_file()
    rev_src = revpath.read_text()
    assert "revision = '1234'" in rev_src
    assert "op.create_table" in rev_src


def test_empty_revision(memdb, dst):
    _create_test_model1(memdb)
    alembic = Alembic(
        memdb, path=dst, file_template="%%(rev)s_%%(slug)s"
    )
    alembic.rev_id = lambda: "1234"
    alembic.revision("test", empty=True)

    revpath = dst / "1234_test.py"
    rev_src = revpath.read_text()
    assert "op.create_table" not in rev_src


def test_upgrade(memdb, dst):
    _create_test_model1(memdb)
    alembic = Alembic(memdb, path=dst)
    rev1 = alembic.revision("test1")

    assert alembic.get_current() is None
    alembic.upgrade()
    assert alembic.get_current() == rev1


def test_upgrade_sql(memdb, dst, capsys):
    _create_test_model1(memdb)
    alembic = Alembic(memdb, path=dst)
    alembic.revision("test1")
    alembic.upgrade(":head", sql=True)

    stdout, _ = capsys.readouterr()
    assert "CREATE TABLE test_model_1" in stdout


def test_upgrade_range_no_sql(memdb, dst):
    _create_test_model1(memdb)
    alembic = Alembic(memdb, path=dst)
    alembic.revision("test1")

    with pytest.raises(ValueError):
        alembic.upgrade(":head", sql=False)


def test_upgrade_sql_no_range(memdb, dst):
    _create_test_model1(memdb)
    alembic = Alembic(memdb, path=dst)
    alembic.revision("test1")

    with pytest.raises(ValueError):
        alembic.upgrade("head", sql=True)


def test_downgrade(memdb, dst):
    _create_test_model1(memdb)
    alembic = Alembic(memdb, path=dst)
    rev1 = alembic.revision("test1")
    alembic.upgrade()
    _create_test_model2(memdb)
    rev2 = alembic.revision("test2")
    alembic.upgrade()

    assert alembic.get_current() == rev2
    alembic.downgrade()
    assert alembic.get_current() == rev1
    alembic.upgrade()
    alembic.downgrade(-2)
    assert alembic.get_current() is None
    alembic.upgrade()
    assert alembic.get_current() == rev2
    alembic.downgrade(1)
    assert alembic.get_current() == rev1


def test_downgrade_sql(memdb, dst, capsys):
    _create_test_model1(memdb)
    alembic = Alembic(memdb, path=dst)
    rev1 = alembic.revision("test1")
    alembic.upgrade()
    alembic.downgrade(f"{rev1.revision}:-1", sql=True)

    stdout, _ = capsys.readouterr()
    assert "DROP TABLE test_model_1" in stdout


def test_downgrade_range_no_sql(memdb, dst):
    _create_test_model1(memdb)
    alembic = Alembic(memdb, path=dst)
    rev1 = alembic.revision("test1")
    alembic.upgrade()

    with pytest.raises(ValueError):
        alembic.downgrade(f"{rev1.revision}:-1", sql=False)


def test_downgrade_sql_no_range(memdb, dst):
    _create_test_model1(memdb)
    alembic = Alembic(memdb, path=dst)
    alembic.revision("test1")
    alembic.upgrade()

    with pytest.raises(ValueError):
        alembic.downgrade("-1", sql=True)


def test_get_history(memdb, dst):
    _create_test_model1(memdb)
    alembic = Alembic(memdb, path=dst)
    rev1 = alembic.revision("test1")
    alembic.upgrade()
    _create_test_model2(memdb)
    rev2 = alembic.revision("test2")

    print("rev1, rev2", rev1, rev2)
    assert alembic.get_history() == [rev1, rev2]
    assert alembic.get_history(end="current") == [rev1]
    alembic.upgrade()
    assert alembic.get_history(start="current") == [rev2]


def test_print_history(memdb, dst, capsys):
    _create_test_model1(memdb)
    alembic = Alembic(memdb, path=dst)
    rev1 = alembic.revision("test1")
    alembic.upgrade()
    _create_test_model2(memdb)
    rev2 = alembic.revision("test2")

    alembic.history()
    stdout, _ = capsys.readouterr()
    assert f"<base> -> {rev1.revision}, test1\n" in stdout
    assert f"{rev1.revision} -> {rev2.revision} (head), test2" in stdout


def test_print_history_verbose(memdb, dst, capsys):
    _create_test_model1(memdb)
    alembic = Alembic(memdb, path=dst)
    rev1 = alembic.revision("test1")
    alembic.upgrade()
    _create_test_model2(memdb)
    rev2 = alembic.revision("test2")

    alembic.history(verbose=True)
    stdout, _ = capsys.readouterr()
    assert f"Rev: {rev1.revision}\nParent: <base>\n" in stdout
    assert f"Rev: {rev2.revision} (head)\nParent: {rev1.revision}\n" in stdout


def test_stamp(memdb, dst):
    _create_test_model1(memdb)
    alembic = Alembic(memdb, path=dst)
    rev1 = alembic.revision("test1")
    alembic.stamp()
    assert alembic.get_current() == rev1


def test_stamp_sql(memdb, dst, capsys):
    _create_test_model1(memdb)
    alembic = Alembic(memdb, path=dst)
    rev1 = alembic.revision("test1")
    alembic.stamp(sql=True)

    stdout, _ = capsys.readouterr()
    stmt = f"INSERT INTO alembic_version (version_num) VALUES ('{rev1.revision}');"
    assert stmt in stdout
    assert "CREATE TABLE test_model_1" not in stdout


def test_print_current(memdb, dst, capsys):
    _create_test_model1(memdb)
    alembic = Alembic(memdb, path=dst)
    rev1 = alembic.revision("test1")
    alembic.upgrade()
    _create_test_model2(memdb)
    alembic.revision("test2")

    alembic.current()
    stdout, _ = capsys.readouterr()
    assert f"<base> -> {rev1.revision}, test1\n" in stdout


def test_print_current_verbose(memdb, dst, capsys):
    _create_test_model1(memdb)
    alembic = Alembic(memdb, path=dst)
    rev1 = alembic.revision("test1")
    alembic.upgrade()
    _create_test_model2(memdb)
    alembic.revision("test2")

    alembic.current(verbose=True)
    stdout, _ = capsys.readouterr()
    assert f"Rev: {rev1.revision}\nParent: <base>\n" in stdout


def test_no_current(memdb, dst, capsys):
    alembic = Alembic(memdb, path=dst)
    alembic.current()
    stdout, _ = capsys.readouterr()
    assert not stdout


def test_get_head(memdb, dst):
    _create_test_model1(memdb)
    alembic = Alembic(memdb, path=dst)
    alembic.revision("test1")
    alembic.upgrade()
    _create_test_model2(memdb)
    rev2 = alembic.revision("test2")

    assert alembic.get_head() == rev2


def test_print_head(memdb, dst, capsys):
    _create_test_model1(memdb)
    alembic = Alembic(memdb, path=dst)
    rev1 = alembic.revision("test1")
    alembic.upgrade()
    _create_test_model2(memdb)
    rev2 = alembic.revision("test2")

    alembic.head()
    stdout, _ = capsys.readouterr()
    assert f"{rev1.revision} -> {rev2.revision} (head), test2" in stdout


def test_print_head_verbose(memdb, dst, capsys):
    _create_test_model1(memdb)
    alembic = Alembic(memdb, path=dst)
    rev1 = alembic.revision("test1")
    alembic.upgrade()
    _create_test_model2(memdb)
    rev2 = alembic.revision("test2")

    alembic.head(verbose=True)
    stdout, _ = capsys.readouterr()
    assert f"Rev: {rev2.revision} (head)\nParent: {rev1.revision}\n" in stdout


def test_no_head(memdb, dst, capsys):
    alembic = Alembic(memdb, path=dst)
    alembic.head()
    stdout, _ = capsys.readouterr()
    assert not stdout


def test_create_all(memdb, dst):
    path = dst / "migrations"
    path.mkdir()
    Model = _create_test_model1(memdb)
    alembic = Alembic(memdb, path)
    rev1 = alembic.revision("test")
    alembic.create_all()

    with memdb.Session() as session:
        session.execute(select(Model)).all()
    assert alembic.get_current() == rev1


def test_get_proper_cli(memdb, dst):
    alembic = Alembic(memdb, path=dst)
    alembic.get_proper_cli()


def test_get_click_cli(memdb, dst, capsys):
    alembic = Alembic(memdb, path=dst)
    cli = alembic.get_click_cli()

    cli(args=["--help"], prog_name="cli", standalone_mode=False)
    stdout, _ = capsys.readouterr()
    assert "  current  " in stdout
    assert "  downgrade  " in stdout
    assert "  head  " in stdout
    assert "  history  " in stdout
    assert "  init  " in stdout
    assert "  revision  " in stdout
    assert "  stamp  " in stdout
    assert "  upgrade  " in stdout


def test_get_flask_cli(memdb, dst, capsys):
    alembic = Alembic(memdb, path=dst)
    cli = alembic.get_flask_cli()

    cli(args=["--help"], prog_name="cli", standalone_mode=False)
    stdout, _ = capsys.readouterr()
    assert "  current  " in stdout
    assert "  downgrade  " in stdout
    assert "  head  " in stdout
    assert "  history  " in stdout
    assert "  init  " in stdout
    assert "  revision  " in stdout
    assert "  stamp  " in stdout
    assert "  upgrade  " in stdout
