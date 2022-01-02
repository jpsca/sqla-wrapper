"""Paginator

A helper class for simple pagination of any iterable, like a
SQLAlchemy query, a list, or any iterable.
"""
from __future__ import annotations

from math import ceil
from typing import Any, Iterable, Iterator, List, Optional, Tuple, Union


__all__ = ("Paginator", "sanitize_page_number")


DEFAULT_START_PAGE = 1
DEFAULT_PER_PAGE = 20
DEFAULT_PADDING = 0


class Paginator:
    """Helper class for paginate data.
    You can construct it from any iterable.

    **Arguments**:

    - **query**:
        Items to paginate.
    - **page**:
        Number of the current page (first page is `1`)
        It can be a number, a string with a number, or
        the strings "first" or "last".
    - **per_page**:
        Max number of items to display on each page.
    - **total**:
        Total number of items. If not provided, the length
        of the iterable will be used.
    - **padding**:
        Number of elements of the previous and next page to show.
        For example, if `per_page` is 10 and `padding` is 2,
        every page will show 14 items, the first two from the
        previous page and the last two for the next one.
        This extra items will be repeated again on their own pages.

    """

    total = 0

    def __init__(
        self,
        query: Any,
        *,
        page: Union[int, str] = DEFAULT_START_PAGE,
        per_page: int = DEFAULT_PER_PAGE,
        total: Optional[int] = None,
        padding: int = DEFAULT_PADDING,
    ) -> None:
        self.query = query

        # The number of items to be displayed on a page.
        assert isinstance(per_page, int) and (
            per_page > 0
        ), "`per_page` must be a positive integer"
        self.per_page = per_page

        # The total number of items.
        if total is None:
            total = len(query)
        self.total = total

        # The current page number (1 indexed)
        if page == "last":
            page = self.num_pages
        if page == "first":
            page = 1
        self.page = page = sanitize_page_number(page)
        if page > self.num_pages:
            page = self.num_pages

        self.padding = padding

    def __bool__(self) -> bool:
        return self.total > 0

    __nonzero__ = __bool__

    @property
    def num_pages(self) -> int:
        """The total number of pages."""
        return int(ceil(self.total / float(self.per_page)))

    @property
    def total_pages(self) -> int:
        """Alias to `num_pages`"""
        return self.num_pages

    @property
    def is_paginated(self) -> bool:
        """True if a more than one page exists."""
        return self.num_pages > 1

    @property
    def showing(self) -> int:
        """The number of items in the current page
        Could be less than `per_page` if we are in the
        last page, or more if `padding` > 0.
        """
        so_far = self.per_page * self.page + self.padding
        so_far = min(so_far, self.total)
        if self.page > 1:
            so_far += self.padding
        prev_pages = self.per_page * (self.page - 1)
        return so_far - prev_pages

    @property
    def has_prev(self) -> bool:
        """True if a previous page exists."""
        return self.page > 1

    @property
    def has_next(self) -> bool:
        """True if a next page exists."""
        return self.page < self.num_pages

    @property
    def next_num(self) -> int:
        """Number of the next page."""
        return self.page + 1

    @property
    def prev_num(self) -> int:
        """Number of the previous page."""
        return self.page - 1

    @property
    def prev(self) -> Optional[Paginator]:
        """Returns a `Paginator` object for the previous page."""
        if self.has_prev:
            return Paginator(self.query, page=self.page - 1, per_page=self.per_page)
        return None

    @property
    def next(self) -> Optional[Paginator]:
        """Returns a `Paginator` object for the next page."""
        if self.has_next:
            return Paginator(self.query, page=self.page + 1, per_page=self.per_page)
        return None

    @property
    def start_index(self) -> int:
        """0-based index of the first element in the current page."""
        return (self.page - 1) * self.per_page

    @property
    def end_index(self) -> int:
        """0-based index of the last element in the current page."""
        end = self.start_index + self.per_page - 1
        return min(end, self.total - 1)

    @property
    def offset(self) -> int:
        offset = (self.page - 1) * self.per_page
        return max(offset - self.padding, 0)

    @property
    def limit(self) -> int:
        limit = self.per_page + self.padding
        if self.page > 1:
            limit = limit + self.padding
        return limit

    @property
    def items(self) -> Iterable:
        """Return the items to for the current page."""
        offset = self.offset
        return self.query[offset : offset + self.limit]

    @property
    def pages(self) -> List:
        """Proxy to get_pages()"""
        return self.get_pages()

    def __iter__(self) -> Iterator:
        for i in self.items:
            yield i

    def get_range(self, sep=u" - ") -> str:
        """Return a string with the 1-based index range
        of items in the page (ignoring the padding). Useful
        for displaying "Showing x - y items of z".

        **Examples**:

        ```python
        p = Paginator(range(100), per_page=10, page=1)
        p.get_range()
        '1 - 10'

        p = Paginator(range(100), per_page=10, page=5)
        p.get_range()
        '41 - 50'
        ```

        """
        return sep.join([str(self.start_index + 1), str(self.end_index + 1)])

    def get_pages(self, showmax: int = 12) -> List:
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

        **Examples**:

        ```python
        [ (1), 2, 3, 4, 5, 6, None, 10, 11, 12, 13 ]
        [ 1, 2, None, 5, 6, 7, (8), 9, 10, None, 13, 14, 15 ]
        [ 1, 2, (3), 4, 5 ]
        ```

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

    def _get_page_groups(self, showmax: int) -> Tuple[List[int], List[int], List[int]]:
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

    def _merge_page_groups(
        self,
        left: List[int],
        center: List[int],
        right: List[int],
    ) -> List[Union[int, None]]:
        pages: List[Optional[int]] = []

        pages += left
        if pages and center:
            if pages[-1] == center[0] - 2:
                if len(pages) > 1:
                    pages = pages[:-1]

            if (
                pages[-1] is not None
                and pages[-1] < center[0] - 1
            ):
                pages.append(None)

        pages += center
        if pages and right:
            if pages[-1] == right[0] - 2:
                if len(right) > 1:
                    right = right[1:]

            if (
                pages[-1] is not None
                and pages[-1] < right[0] - 1
            ):
                pages.append(None)

        pages += right

        return sorted_dedup(pages)


def sorted_dedup(iterable: Iterable) -> List[Optional[int]]:
    """Sorted deduplication without removing the
    possibly duplicated `None` values."""
    dedup: List[Optional[int]] = []

    visited = set()
    for item in iterable:
        if item is None:
            dedup.append(item)
        elif item not in visited:
            dedup.append(item)
            visited.add(item)

    return dedup


def sanitize_page_number(
    page: Union[int, str],
    default: int = DEFAULT_START_PAGE,
) -> int:
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

    return page if page > 0 else default
