def test_create(dbs, TestModelA):
    TestModelA.create(dbs, title="Remember")
    dbs.commit()
    obj = TestModelA.first(dbs)
    assert obj.title == "Remember"


def test_all(dbs, TestModelA):
    TestModelA.create(dbs, title="Lorem")
    TestModelA.create(dbs, title="Ipsum")
    dbs.commit()

    obj_list = TestModelA.all(dbs)
    assert len(obj_list) == 2


def test_create_or_first_using_create(dbs, TestModelA):
    obj1 = TestModelA.create_or_first(dbs, title="Lorem Ipsum")
    assert obj1
    dbs.commit()

    obj2 = TestModelA.create_or_first(dbs, title="Lorem Ipsum")
    assert obj1 == obj2


def test_create_or_first_using_first(dbs, TestModelA):
    obj1 = TestModelA.create(dbs, title="Lorem Ipsum")
    assert obj1
    dbs.commit()

    obj2 = TestModelA.create_or_first(dbs, title="Lorem Ipsum")
    assert obj1 == obj2


def test_first_or_create_using_first(dbs, TestModelA):
    obj1 = TestModelA.create(dbs, title="Lorem Ipsum")
    assert obj1
    dbs.commit()

    obj2 = TestModelA.first_or_create(dbs, title="Lorem Ipsum")
    assert obj1 == obj2


def test_first_or_create_using_create(dbs, TestModelA):
    assert TestModelA.first_or_create(dbs, id=1, title="Lorem Ipsum")
    dbs.commit()

    obj = TestModelA.first_or_create(dbs, title="Lorem Ipsum")
    assert obj and obj.id == 1


def test_update(dbs, TestModelA):
    obj = TestModelA.create(dbs, title="Remember")
    obj.update(dbs, title="lorem ipsum")

    updated = TestModelA.first(dbs)
    assert updated.title == "lorem ipsum"


def test_delete(dbs, TestModelA):
    obj = TestModelA.create(dbs, title="Remember")
    dbs.commit()
    assert TestModelA.first(dbs)
    obj.delete(dbs)
    dbs.commit()
    assert TestModelA.first(dbs) is None
