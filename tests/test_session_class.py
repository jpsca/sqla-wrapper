def test_create(dbs, TestModelA):
    dbs.create(TestModelA, title="Remember")
    dbs.commit()
    obj = dbs.first(TestModelA)
    assert obj.title == "Remember"


def test_all(dbs, TestModelA):
    dbs.create(TestModelA, title="Lorem")
    dbs.create(TestModelA, title="Ipsum")
    dbs.commit()

    obj_list = dbs.all(TestModelA)
    assert len(obj_list) == 2


def test_create_or_first_using_create(dbs, TestModelA):
    obj1 = dbs.create_or_first(TestModelA, title="Lorem Ipsum")
    assert obj1
    dbs.commit()

    obj2 = dbs.create_or_first(TestModelA, title="Lorem Ipsum")
    assert obj1 == obj2


def test_create_or_first_using_first(dbs, TestModelA):
    obj1 = dbs.create(TestModelA, title="Lorem Ipsum")
    assert obj1
    dbs.commit()

    obj2 = dbs.create_or_first(TestModelA, title="Lorem Ipsum")
    assert obj1 == obj2


def test_first_or_create_using_first(dbs, TestModelA):
    obj1 = dbs.create(TestModelA, title="Lorem Ipsum")
    assert obj1
    dbs.commit()

    obj2 = dbs.first_or_create(TestModelA, title="Lorem Ipsum")
    assert obj1 == obj2


def test_first_or_create_using_create(dbs, TestModelA):
    assert dbs.first_or_create(TestModelA, id=1, title="Lorem Ipsum")
    dbs.commit()

    obj = dbs.first_or_create(TestModelA, title="Lorem Ipsum")
    assert obj and obj.id == 1
