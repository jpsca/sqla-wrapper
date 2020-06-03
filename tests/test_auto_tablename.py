def test_vanilla(db):
    class HTTPRequest(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        field = db.Column(db.String)

    db.create_all()

    assert HTTPRequest.__tablename__ == 'http_requests'


def test_primary_in_mixin(db):
    class IDMixin(object):
        id = db.Column(db.Integer, primary_key=True)

    class HTTPRequest(db.Model, IDMixin):
        field = db.Column(db.String)

    db.create_all()

    assert HTTPRequest.__tablename__ == 'http_requests'
    assert hasattr(HTTPRequest, 'id')
