# -*- coding: utf-8 -*-
import pytest

from orm.helpers import get_table_name


def test_get_table_name():
    assert get_table_name('Document') == 'documents'
    assert get_table_name('ToDo') == 'to_dos'
    assert get_table_name('UserTestCase') == 'user_test_cases'
    assert get_table_name('URL') == 'urls'
    assert get_table_name('HTTPRequest') == 'http_requests'

