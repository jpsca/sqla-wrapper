# coding=utf-8
"""
    ==================
    SQLAlchemy-Wrapper
    ==================

    A friendly wrapper for SQLAlchemy.

    :copyright: 2013-2017 by `Juan-Pablo Scaletti <http://jpscaletti.com>`_.
    :license: BSD, see LICENSE for more details.

    Some of the code was extracted and adapted from
    Flask-SQLAlchemy <http://flask-sqlalchemy.pocoo.org/>

"""
from .main import SQLAlchemy, BaseQuery, Model  # noqa
from .paginator import Paginator, sanitize_page_number  # noqa
from .helpers import get_debug_queries  # noqa

__version__ = '1.8.1'
