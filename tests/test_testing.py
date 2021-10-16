from sqlalchemy import func, select


def test_independence_1(db, dbs, TestModelB):
    stmt = select(func.count("*")).select_from(TestModelB)
    assert db.s.execute(stmt).scalar() == 1

    db.s.add(TestModelB(title="second"))
    db.s.flush()
    assert db.s.execute(stmt).scalar() == 2


def test_independence_2(db, dbs, TestModelB):
    stmt = select(func.count("*")).select_from(TestModelB)
    assert db.s.execute(stmt).scalar() == 1

    db.s.add(TestModelB(title="second"))
    db.s.flush()
    assert db.s.execute(stmt).scalar() == 2


def test_independence_3(db, dbs, TestModelB):
    stmt = select(func.count("*")).select_from(TestModelB)
    assert db.s.execute(stmt).scalar() == 1

    db.s.add(TestModelB(title="second"))
    db.s.flush()
    assert db.s.execute(stmt).scalar() == 2


def test_rollback(db, dbs, TestModelB):
    stmt = select(func.count("*")).select_from(TestModelB)
    assert db.s.execute(stmt).scalar() == 1

    db.s.add(TestModelB(title="second"))
    db.s.flush()
    db.s.rollback()
    assert db.s.execute(stmt).scalar() == 1
