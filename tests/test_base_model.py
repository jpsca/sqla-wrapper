def test_fill(dbs, TestModelA):
    obj = dbs.create(TestModelA, title="Remember")
    obj.fill(title="lorem ipsum")
    dbs.commit()

    updated = dbs.first(TestModelA)
    assert updated.title == "lorem ipsum"


def test_repr(dbs, TestModelA):
    obj = dbs.create(TestModelA, title="Hello world")
    dbs.commit()

    repr = str(obj)
    assert f"<TestModelA #{id(obj)}" in repr
    assert f"\n id = {obj.id}" in repr
    assert "\n title = 'Hello world'" in repr
