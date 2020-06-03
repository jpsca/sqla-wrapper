def get_test_model(db):
    class Note(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        title = db.Column(db.String(60), nullable=False, unique=True)
        text = db.Column(db.Text)

    db.create_all()
    return Note


def test_create(db):
    Note = get_test_model(db)
    Note.create(title="Remember", text="Write tests.")
    snote = db.query(Note).first()
    assert snote.title == "Remember"
    assert snote.text == "Write tests."


def test_save(db):
    Note = get_test_model(db)
    note = Note.create(title="Remember", text="Write tests.")
    note.title = "TO DO"
    note.save()
    snote = db.query(Note).first()
    assert snote.title == "TO DO"


def test_exists(db):
    Note = get_test_model(db)
    note = Note.create(title="Remember", text="Write tests.")

    assert not Note.exists(title="meh")
    assert Note.exists(title=note.title)


def test_create_or_first(db):
    Note = get_test_model(db)
    note1 = Note.create_or_first(title="Lorem Ipsum")
    note2 = Note.create_or_first(title="Lorem Ipsum")

    assert note1
    assert note1 == note2


def test_delete(db):
    Note = get_test_model(db)
    note = Note.create(title="Remember")
    assert db.query(Note).first()
    note.delete()
    assert db.query(Note).first() is None
