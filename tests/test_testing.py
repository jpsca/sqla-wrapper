from sqlalchemy import select, func


def test_independence_1(dbs, TestModelB):
    stmt = select(func.count("*")).select_from(TestModelB)
    assert dbs.execute(stmt).scalar() == 1

    dbs.add(TestModelB(title="second"))
    dbs.flush()
    assert dbs.execute(stmt).scalar() == 2


def test_independence_2(dbs, TestModelB):
    stmt = select(func.count("*")).select_from(TestModelB)
    assert dbs.execute(stmt).scalar() == 1

    dbs.add(TestModelB(title="second"))
    dbs.flush()
    assert dbs.execute(stmt).scalar() == 2


def test_independence_3(dbs, TestModelB):
    stmt = select(func.count("*")).select_from(TestModelB)
    assert dbs.execute(stmt).scalar() == 1

    dbs.add(TestModelB(title="second"))
    dbs.flush()
    assert dbs.execute(stmt).scalar() == 2


def test_rollback(dbs, TestModelB):
    stmt = select(func.count("*")).select_from(TestModelB)
    assert dbs.execute(stmt).scalar() == 1

    dbs.add(TestModelB(title="second"))
    dbs.flush()
    dbs.rollback()
    assert dbs.execute(stmt).scalar() == 1
