"""Paginator

A helper class for simple pagination of any iterable, like a
SQLAlchemy query, a list, or any iterable.
"""
from math import ceil


__all__ = ("Paginator", "sanitize_page_number")


DEFAULT_START_PAGE = 1
DEFAULT_PER_PAGE = 20
DEFAULT_PADDING = 0


class Paginator(object):
    """Helper class for paginate data.
    You can construct it from any SQLAlchemy query object or other iterable.

    Arguments are:

        query:
            Iterable to paginate. Can be a query, a list or any
            other iterable.
        page:
            Current page. If the value is the string
        per_page:
            Max number of items to display on each page.
        total:
            Total number of items. If provided, no attempt wll be made to
            calculate it from the `query` argument.
        padding:
            Number of elements of the next page to show.
        on_error:
            Used if the page number is too big for the total number
            of items. Raised if it's an exception, called otherwise.
            `None` by default.

    """

    showing = 0
    total = 0

    def __init__(
        self,
        query,
        page=DEFAULT_START_PAGE,
        per_page=DEFAULT_PER_PAGE,
        total=None,
        padding=DEFAULT_PADDING,
        on_error=None,
    ):
        self.query = query

        # The number of items to be displayed on a page.
        assert isinstance(per_page, int) and (
            per_page > 0
        ), "`per_page` must be a positive integer"
        self.per_page = per_page

        # The total number of items matching the query.
        if total is None:
            try:
                total = query.count()
            except (TypeError, AttributeError):
                total = query.__len__()
        self.total = total

        # The current page number (1 indexed)
        if page == "last":
            page = self.num_pages
        if page == "first":
            page = 1
        self.page = page = sanitize_page_number(page)

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
    def total_pages(self):
        """Alias to `num_pages`"""
        return self.num_pages

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
        """Returns a `Paginator` object for the previous page."""
        if self.has_prev:
            return Paginator(self.query, self.page - 1, per_page=self.per_page)

    @property
    def next(self):
        """Returns a `Paginator` object for the next page."""
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

    def get_range(self, sep=u" - "):
        return sep.join([str(self.start_index + 1), str(self.end_index + 1)])

    @property
    def items(self):
        offset = (self.page - 1) * self.per_page
        offset = max(offset - self.padding, 0)
        limit = self.per_page + self.padding
        if self.page > 1:
            limit = limit + self.padding

        if hasattr(self.query, "limit") and hasattr(self.query, "offset"):
            return self.query.limit(limit).offset(offset)

        return self.query[offset : offset + limit]

    def __iter__(self):
        for i in self.items:
            yield i

    def pages(self):
        """Iterates over the page numbers in the pagination."""
        return self.get_pages()

    def get_pages(self, showmax=12):
        """Return a list of the page numbers in the pagination. The `showmax`
        parameter control how many numbers are shown at most.

        Depending of the page number and the showmax value, there are several
        possible scenarios, but the these rules are followed:

        1. The first, last and current pages are always returned.
        2. After those three, the remaining slots are filled around the
        current page, after the first page, and before the last page, in that
        order, in turns.
        3. Skipped page numbers are represented as `None`. We never skip just
        one page, so the final number of pages shown could be less than
        the value of `showmax`.

        Examples:

            [ (1), 2, 3, 4, 5, 6, None, 10, 11, 12, 13, 14, 15 ]
            [ 1, (2), 3, 4, 5, 6, 7, None, 11, 12, 13, 14, 15 ]
            [ 1, 2, (3), 4, 5, 6, 7, None, 11, 12, 13, 14, 15 ]
            [ 1, 2, 3, (4), 5, 6, 7, 8, None, 12, 13, 14, 15 ]
            [ 1, 2, 3, 4, (5), 6, 7, 8, None, 12, 13, 14, 15 ]
            [ 1, 2, 3, 4, 5, (6), 7, 8, 9, None, 13, 14, 15 ]
            [ 1, 2, 3, 4, 5, 6, (7), 8, 9, None, 13, 14, 15 ]
            [ 1, 2, None, 5, 6, 7, (8), 9, 10, None, 13, 14, 15 ]
            [ 1, 2, 3, None, 6, 7, 8, (9), 10, 11, None, 14, 15 ]
            [ 1, 2, 3, None, 7, 8, 9, (10), 11, 12, 13, 14, 15 ]
            [ 1, 2, 3, 4, None, 8, 9, 10, (11), 12, 13, 14, 15 ]
            [ 1, 2, 3, 4, None, 8, 9, 10, 11, (12), 13, 14, 15 ]
            [ 1, 2, 3, 4, 5, None, 9, 10, 11, 12, (13), 14, 15 ]
            [ 1, 2, 3, 4, 5, None, 9, 10, 11, 12, 13, (14), 15 ]
            [ 1, 2, 3, 4, 5, 6, None, 10, 11, 12, 13, 14, (15) ]

        This is one way how you could render such a pagination in the template:

        ```jinja
          <p>Showing {{ pg.showing }} or {{ pg.total }}</p>
          <ol class="pg">
          {%- if pg.has_prev %}
            <li><a href="{{ url_for(endpoint, page=pg.prev_num) }}"
             rel="me prev">«</a></li>
          {% else %}
            <li class="disabled"><span>«</span></li>
          {%- endif %}

          {%- for page in pg.pages %}
            {% if page %}
              {% if page != pg.page %}
                <li><a href="{{ url_for(endpoint, page=page) }}"
                 rel="me">{{ page }}</a></li>
              {% else %}
                <li class="current"><span>{{ page }}</span></li>
              {% endif %}
            {% else %}
              <li><span class=ellipsis>…</span></li>
            {% endif %}
          {%- endfor %}

          {%- if pg.has_next %}
            <li><a href="{{ url_for(endpoint, page=pg.next_num) }}"
             rel="me next">»</a></li>
          {% else %}
            <li class="disabled"><span>»</span></li>
          {%- endif %}
          </ol>
        ```

        """
        assert showmax >= 4
        if self.num_pages <= showmax:
            return list(range(1, self.num_pages + 1))

        left, center, right = self._get_page_groups(showmax)
        return self._merge_page_groups(left, center, right)

    def _get_page_groups(self, showmax):
        left = [1]
        center = [self.page]
        right = [self.num_pages]

        def full():
            return len(list(set(left + center + right))) >= showmax

        while True:
            if full():
                break
            value = center[0] - 1
            if value:
                center = [value] + center

            if full():
                break
            value = center[-1] + 1
            if value <= self.num_pages:
                center = center + [value]

            if full():
                break
            left = left + [left[-1] + 1]

            if full():
                break
            value = right[0] - 1
            if value:
                right = [value] + right

        return left, center, right

    def _merge_page_groups(self, left, center, right):
        pages = left[:]

        if pages[-1] == center[0] - 2:
            if len(pages) > 1:
                pages = pages[:-1]

        if pages[-1] < center[0] - 1:
            pages.append(None)

        pages += center

        if pages[-1] == right[0] - 2:
            if len(right) > 1:
                right = right[1:]

        if pages[-1] < right[0] - 1:
            pages.append(None)

        pages += right

        return sorted_dedup(pages)


def sorted_dedup(iterable):
    """Sorted deduplication without removing the
    possibly duplicated `None` values."""
    dedup = []
    visited = set()
    for item in iterable:
        if item is None:
            dedup.append(item)
        elif item not in visited:
            dedup.append(item)
            visited.add(item)

    return dedup


def sanitize_page_number(page, default=DEFAULT_START_PAGE):
    """A helper function for cleanup a `page` argument. Cast a string to
    integer and check that the final value is positive.
    If the value is not valid, returns the default value.
    """
    if not page:
        return default
    try:
        page = int(page)
    except (ValueError, TypeError):
        return default
    if isinstance(page, int) and (page > 0):
        return page
    return default
