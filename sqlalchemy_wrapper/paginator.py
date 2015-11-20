# coding=utf-8
"""
    ==========
    Paginator
    ==========

    A helper class for pagination of any iterable, like a SQLAlchemy query
    result or a list.

"""
from math import ceil

from ._compat import xrange, string_types

DEFAULT_PER_PAGE = 10


def sanitize_page_number(page):
    """A helper function for cleanup a ``page`` argument. Cast a string to
    integer and check that the final value is positive.
    If the value is not valid returns 1.
    """
    if isinstance(page, string_types) and page.isdigit():
        page = int(page)
    if isinstance(page, int) and (page > 0):
        return page
    return 1


class Paginator(object):
    """Helper class for paginate data.
    You can construct it from any SQLAlchemy query object or other iterable.
    """
    showing = 0
    total = 0

    def __init__(self, query, page=1, per_page=DEFAULT_PER_PAGE, total=None,
                 padding=0, on_error=None):
        """
        :query:
            Iterable to paginate. Can be a query results object, a list or any
            other iterable.
        :page:
            Current page.
        :per_page:
            Max number of items to display on each page.
        :total:
            Total number of items. If provided, no attempt wll be made to
            calculate it from the ``query`` argument.
        :padding:
            Number of elements of the next page to show.
        :on_error:
            Used if the page number is too big for the total number
            of items. Raised if it's an exception, called otherwise.
            ``None`` by default.
        """
        self.query = query

        # The number of items to be displayed on a page.
        assert isinstance(per_page, int) and (per_page > 0), \
            '`per_page` must be a positive integer'
        self.per_page = per_page

        # The total number of items matching the query.
        if total is None:
            try:
                # For counting no need to waste time with ordering
                total = query.order_by(None).count()
            except (TypeError, AttributeError):
                total = query.__len__()
        self.total = total

        # The current page number (1 indexed)
        page = sanitize_page_number(page)
        if page == 'last':
            page = self.num_pages
        self.page = page

        # The number of items in the current page (could be less than per_page)
        if total > per_page * page:
            showing = per_page
        else:
            showing = total - per_page * (page - 1)
        self.showing = showing

        if showing == 0 and on_error:
            if isinstance(on_error, Exception):
                raise on_error
            return on_error()

        self.padding = padding

    def __bool__(self):
        return self.total > 0

    __nonzero__ = __bool__

    @property
    def num_pages(self):
        """The total number of pages."""
        return int(ceil(self.total / float(self.per_page)))

    @property
    def is_paginated(self):
        """True if a more than one page exists."""
        return self.num_pages > 1

    @property
    def has_prev(self):
        """True if a previous page exists."""
        return self.page > 1

    @property
    def has_next(self):
        """True if a next page exists."""
        return self.page < self.num_pages

    @property
    def next_num(self):
        """Number of the next page."""
        return self.page + 1

    @property
    def prev_num(self):
        """Number of the previous page."""
        return self.page - 1

    @property
    def prev(self):
        """Returns a :class:`Paginator` object for the previous page."""
        if self.has_prev:
            return Paginator(self.query, self.page - 1, per_page=self.per_page)

    @property
    def next(self):
        """Returns a :class:`Paginator` object for the next page."""
        if self.has_next:
            return Paginator(self.query, self.page + 1, per_page=self.per_page)

    @property
    def start_index(self):
        """0-based index of the first element in the current page."""
        return (self.page - 1) * self.per_page

    @property
    def end_index(self):
        """0-based index of the last element in the current page."""
        end = self.start_index + self.per_page - 1
        return min(end, self.total - 1)

    def get_range(self, sep=u' - '):
        return sep.join([str(self.start_index + 1), str(self.end_index + 1)])

    @property
    def items(self):
        offset = (self.page - 1) * self.per_page
        offset = max(offset - self.padding, 0)
        limit = self.per_page + self.padding
        if self.page > 1:
            limit = limit + self.padding

        if hasattr(self.query, 'limit') and hasattr(self.query, 'offset'):
            return self.query.limit(limit).offset(offset)

        return self.query[offset:offset + limit]

    def __iter__(self):
        for i in self.items:
            yield i

    @property
    def pages(self):
        """Iterates over the page numbers in the pagination."""
        return self.iter_pages()

    def iter_pages(self, left_edge=2, left_current=3, right_current=4, right_edge=2):
        """Iterates over the page numbers in the pagination.  The four
        parameters control the thresholds how many numbers should be produced
        from the sides:

        .. code::

            1..left_edge
            None
            (current - left_current), current, (current + right_current)
            None
            (num_pages - right_edge)..num_pages

        Example:

        .. sourcecode:: python

            >>> pg = Paginator(range(1, 20), page=10)
            >>> [p for p in pg.iter_pages(left_edge=2, left_current=2, right_current=5, right_edge=2)]
            [1, 2, None, 8, 9, 10, 11, 12, 13, 14, 15, None, 19, 20]

        Skipped page numbers are represented as ``None``.
        This is one way how you could render such a pagination in the template:

        .. sourcecode:: html+jinja

            {% macro render_paginator(paginator, endpoint) %}
              <p>Showing {{ paginator.showing }} or {{ paginator.total }}</p>
              <ol class="paginator">
              {%- if paginator.has_prev %}
                <li><a href="{{ url_for(endpoint, page=paginator.prev_num) }}"
                 rel="me prev">«</a></li>
              {% else %}
                <li class="disabled"><span>«</span></li>
              {%- endif %}

              {%- for page in paginator.pages %}
                {% if page %}
                  {% if page != paginator.page %}
                    <li><a href="{{ url_for(endpoint, page=page) }}"
                     rel="me">{{ page }}</a></li>
                  {% else %}
                    <li class="current"><span>{{ page }}</span></li>
                  {% endif %}
                {% else %}
                  <li><span class=ellipsis>…</span></li>
                {% endif %}
              {%- endfor %}

              {%- if paginator.has_next %}
                <li><a href="{{ url_for(endpoint, page=paginator.next_num) }}"
                 rel="me next">»</a></li>
              {% else %}
                <li class="disabled"><span>»</span></li>
              {%- endif %}
              </ol>
            {% endmacro %}

        """
        last = 0
        for num in xrange(1, self.num_pages + 1):
            is_active_page = (
                num <= left_edge
                or (
                    (num >= self.page - left_current) and
                    (num < self.page + right_current)
                )
                or (
                    (num > self.num_pages - right_edge)
                )
            )
            if is_active_page:
                if last + 1 != num:
                    yield None
                yield num
                last = num
