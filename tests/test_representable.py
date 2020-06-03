import pytest


def test_regular_pk(db):
    class Row(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(60), nullable=False)

    db.create_all()
    db.add(Row(name="a"))
    db.flush()
    row = db.query(Row).first()

    assert str(row) == "<Row #1>"


def test_inherited_pk(db):
    class IDMixin:
        id = db.Column(db.Integer, primary_key=True)

    class Row(IDMixin, db.Model):
        name = db.Column(db.String(60), nullable=False)

    db.create_all()
    db.add(Row(name="a"))
    db.flush()
    row = db.query(Row).first()

    assert str(row) == "<Row #1>"


def test_abstract_baseclass(db):
    class Base(db.Model):
        __abstract__ = True
        id = db.Column(db.Integer, primary_key=True)

    class Row(Base):
        name = db.Column(db.String(60), nullable=False)

    db.create_all()
    db.add(Row(name="a"))
    db.flush()
    row = db.query(Row).first()

    assert str(row) == "<Row #1>"


def test_composite_pk(db):
    class Spaceship(db.Model):
        make = db.Column(db.String, primary_key=True)
        model = db.Column(db.String, primary_key=True)
        name = db.Column(db.String(60), nullable=False)

    db.create_all()
    db.add(Spaceship(make="SpaceX", model="Falcon", name="Dragon"))
    db.flush()
    sp = db.query(Spaceship).first()

    assert str(sp) == "<Spaceship #SpaceX-Falcon>"


def test_unsave(db):
    class Row(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(60), nullable=False)

    db.create_all()
    row = Row(name="a")
    db.add(row)

    assert str(row) == "<Row #None>"


def test_custom_attrs_text(db):
    class Row(db.Model):
        __repr_attrs__ = ["name"]

        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(60), nullable=False)

    db.create_all()
    db.add(Row(name="My name"))
    db.flush()
    row = db.query(Row).first()

    assert str(row) == "<Row #1 'My name'>"


def test_custom_attrs_value(db):
    class Row(db.Model):
        __repr_attrs__ = ["value"]

        id = db.Column(db.Integer, primary_key=True)
        value = db.Column(db.Integer, nullable=False)

    db.create_all()
    db.add(Row(value=524))
    db.flush()
    row = db.query(Row).first()

    assert str(row) == "<Row #1 524>"


def test_custom_attrs_many(db):
    class Row(db.Model):
        __repr_attrs__ = ["make", "model"]

        id = db.Column(db.Integer, primary_key=True)
        make = db.Column(db.String(60), nullable=False)
        model = db.Column(db.String(60), nullable=False)

    db.create_all()
    db.add(Row(make="SpaceX", model="Falcon 9"))
    db.flush()
    row = db.query(Row).first()

    assert str(row) == "<Row #1 make:'SpaceX' model:'Falcon 9'>"


def test_custom_attrs_invalid(db):
    class Row(db.Model):
        __repr_attrs__ = ["blargh"]

        id = db.Column(db.Integer, primary_key=True)
        value = db.Column(db.Integer, nullable=False)

    db.create_all()
    db.add(Row(value=524))
    db.flush()
    row = db.query(Row).first()

    with pytest.raises(KeyError):
        assert str(row)


def test_default_max_repr(db):
    class Row(db.Model):
        __repr_attrs__ = ["name"]

        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.UnicodeText, nullable=False)

    db.create_all()
    db.add(Row(name="Lorem ipsum dolor sit amet, consectetur adipiscing elit. Pellentesque porttitor sollicitudin purus."))
    db.flush()
    row = db.query(Row).first()
    print(row)
    assert str(row) == "<Row #1 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Pellent...'>"


def test_custom_max_repr(db):
    class Row(db.Model):
        __repr_attrs__ = ["name"]
        __repr_max_length__ = 11

        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.UnicodeText, nullable=False)

    db.create_all()
    db.add(Row(name="Lorem ipsum dolor sit amet, consectetur adipiscing elit."))
    db.flush()
    row = db.query(Row).first()
    print(row)
    assert str(row) == "<Row #1 'Lorem ipsum...'>"


def test_overwritten_repr(db):
    class Row(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(60), nullable=False)

        def __repr__(self):
            return "Yeah"

    db.create_all()
    db.add(Row(name="a"))
    db.flush()
    row = db.query(Row).first()

    assert str(row) == "Yeah"
