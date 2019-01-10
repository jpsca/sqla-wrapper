from sqlalchemy.orm import Query

from .paginator import Paginator


class BaseQuery(Query):
    """The default query object used for models. This can be subclassed and
    replaced for individual models by setting the :attr:`~SQLAlchemy.query_cls`
    attribute.

    This is a subclass of a standard SQLAlchemy
    :class:`~sqlalchemy.orm.query.Query` class and has all the methods of a
    standard query as well.
    """

    def get_or_error(self, uid, error):
        """Like :meth:`get` but raises an error if not found instead of
        returning `None`.
        """
        rv = self.get(uid)
        if rv is None:
            if isinstance(error, Exception):
                raise error
            return error()
        return rv

    def first_or_error(self, error):
        """Like :meth:`first` but raises an error if not found instead of
        returning `None`.
        """
        rv = self.first()
        if rv is None:
            if isinstance(error, Exception):
                raise error
            return error()
        return rv

    def paginate(self, **kwargs):
        """Paginate this results.

        Returns an :class:`Paginator` object.
        """
        return Paginator(self, **kwargs)
