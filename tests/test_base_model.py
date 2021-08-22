def test_fill(dbs, TestModelA):
    obj = dbs.create(TestModelA, title="Remember")
    obj.fill(title="lorem ipsum")
    dbs.commit()

    updated = dbs.first(TestModelA)
    assert updated.title == "lorem ipsum"
