# coding=utf-8
from __future__ import print_function

from sqlalchemy_wrapper import SQLAlchemy, Paginator


def create_test_model():
    db = SQLAlchemy('sqlite://')

    class Item(db.Model):
        id = db.Column(db.Integer, primary_key=True)

    class Part(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        item_id = db.Column(db.Integer, db.ForeignKey(Item.id))
        item = db.relationship('Item', backref='parts')

    db.create_all()

    for i in range(1, 26):
        item = Item()
        db.add(item)
    db.commit()

    item = db.query(Item).first()
    for j in range(1, 26):
        db.add(Part(item=item))
    db.commit()

    return db, Item, Part


def test_list_pagination():
    """The paginator is a helper class that can be used with any iterable
    object.
    """
    items = range(1, 491)
    p = Paginator(items, page=1, per_page=20)

    assert p.page == 1
    assert not p.has_prev
    assert p.has_next
    assert p.total == 490
    assert p.num_pages == 25
    assert p.next_num == 2
    assert list(p.pages) == [1, 2, 3, 4, None, 24, 25]

    p.page = 10
    assert list(p.pages) == [1, 2, None, 7, 8, 9, 10, 11, 12, 13, None, 24, 25]
    assert list(p) == list(range(181, 201))


def test_abstract_list_pagination():
    """Yes indeed, the paginator can be used too without anything to actually
    be paginated. How quaint!
    """
    p = Paginator(query=None, page=1, per_page=20, total=490)

    assert p.page == 1
    assert not p.has_prev
    assert p.has_next
    assert p.total == 490
    assert p.num_pages == 25
    assert p.next_num == 2
    assert list(p.pages) == [1, 2, 3, 4, None, 24, 25]

    p.page = 10
    assert list(p.pages) == [1, 2, None, 7, 8, 9, 10, 11, 12, 13, None, 24, 25]


def test_paginated_query():
    db, Item, Part = create_test_model()
    p = Paginator(db.query(Item), page=2, per_page=5)
    items_in_page = list(p)

    assert items_in_page[0].id == 6
    assert items_in_page[1].id == 7


def test_paginated_joined_query():
    db, Item, Part = create_test_model()
    item = db.query(Item).first()
    p = Paginator(item.parts, page=2, per_page=5)
    items_in_page = list(p)

    assert items_in_page[0].id == 6
    assert items_in_page[1].id == 7


def test_bool_paginator():
    assert Paginator(range(5))
    assert not Paginator([])
