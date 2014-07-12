# -*- coding: utf-8 -*-
from sqlalchemy_wrapper.helpers import _get_table_name


def test_get_table_name():
    assert _get_table_name('Document') == 'documents'
    assert _get_table_name('ToDo') == 'to_dos'
    assert _get_table_name('UserTestCase') == 'user_test_cases'
    assert _get_table_name('URL') == 'urls'
    assert _get_table_name('HTTPRequest') == 'http_requests'
