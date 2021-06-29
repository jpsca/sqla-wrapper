from sqlalchemy import Column, Integer, String, Text


def get_test_model(db):
    class Note(db.Model):
        __tablename__ = "notes"
        id = Column(Integer, primary_key=True)
        title = Column(String(60), nullable=False, unique=True)
        text = Column(Text)

    db.create_all()
    return Note


def test_create(db):
    Note = get_test_model(db)
    Note.create(title="Remember", text="Write tests.")
    snote = Note.first()
    assert snote.title == "Remember"
    assert snote.text == "Write tests."


def test_all(db):
    Note = get_test_model(db)
    Note.create(title="Lorem")
    Note.create(title="Ipsum")

    note_list = Note.all()
    assert len(note_list) == 2


def test_create_or_first_using_create(db):
    Note = get_test_model(db)
    note1 = Note.create_or_first(title="Lorem Ipsum")
    note2 = Note.create_or_first(title="Lorem Ipsum")

    assert note1
    assert note1 == note2


def test_create_or_first_using_first(db):
    Note = get_test_model(db)
    note1 = Note.create(title="Lorem Ipsum")
    note2 = Note.create_or_first(title="Lorem Ipsum")

    assert note1
    assert note1 == note2


def test_first_or_create_using_first(db):
    Note = get_test_model(db)
    note1 = Note.create(title="Lorem Ipsum")
    note2 = Note.first_or_create(title="Lorem Ipsum")

    assert note1
    assert note1 == note2


def test_first_or_create_using_create(db):
    Note = get_test_model(db)
    note1 = Note.first_or_create(title="Lorem Ipsum")
    note2 = Note.first_or_create(title="Lorem Ipsum")

    assert note1
    assert note1 == note2


def test_update(db):
    Note = get_test_model(db)
    note = Note.create(title="Remember", text="Write tests.")
    note.update(title="lorem", text="ipsum")

    snote = Note.first()
    assert snote.title == "lorem"
    assert snote.text == "ipsum"


def test_delete(db):
    Note = get_test_model(db)
    note = Note.create(title="Remember")

    assert Note.first()
    note.delete()
    assert Note.first() is None
