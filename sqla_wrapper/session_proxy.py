

class SessionProxyMixin(object):

    @property
    def query(self):
        """Proxy for ``self._session.query``."""
        return self._session.query  # pragma:no cover

    def add(self, *args, **kwargs):
        """Proxy for ``self._session.add()``."""
        return self._session.add(*args, **kwargs)  # pragma:no cover

    def add_all(self, *args, **kwargs):
        """Proxy for ``self._session.add_all()``."""
        return self._session.add_all(*args, **kwargs)  # pragma:no cover

    def begin(self, *args, **kwargs):
        """Proxy for ``self._session.begin()``."""
        return self._session.begin(*args, **kwargs)  # pragma:no cover

    def begin_nested(self, *args, **kwargs):
        """Proxy for ``self._session.begin_nested()``."""
        return self._session.begin_nested(*args, **kwargs)  # pragma:no cover

    def commit(self, *args, **kwargs):
        """Proxy for ``self._session.commit()``."""
        return self._session.commit(*args, **kwargs)  # pragma:no cover

    def connection(self, *args, **kwargs):
        """Proxy for ``self._session.connection()``."""
        return self._session.connection(*args, **kwargs)  # pragma:no cover

    def delete(self, *args, **kwargs):
        """Proxy for ``self._session.delete()``."""
        return self._session.delete(*args, **kwargs)  # pragma:no cover

    def execute(self, *args, **kwargs):
        """Proxy for ``self._session.execute()``."""
        return self._session.execute(*args, **kwargs)  # pragma:no cover

    def expire(self, *args, **kwargs):
        """Proxy for ``self._session.expire()``."""
        return self._session.expire(*args, **kwargs)  # pragma:no cover

    def expire_all(self, *args, **kwargs):
        """Proxy for ``self._session.expire_all()``."""
        return self._session.expire_all(*args, **kwargs)  # pragma:no cover

    def expunge(self, *args, **kwargs):
        """Proxy for ``self._session.expunge()``."""
        return self._session.expunge(*args, **kwargs)  # pragma:no cover

    def expunge_all(self, *args, **kwargs):
        """Proxy for ``self._session.expunge_all()``."""
        return self._session.expunge_all(*args, **kwargs)  # pragma:no cover

    def flush(self, *args, **kwargs):
        """Proxy for ``self._session.flush()``."""
        return self._session.flush(*args, **kwargs)  # pragma:no cover

    def invalidate(self, *args, **kwargs):
        """Proxy for ``self._session.invalidate()``."""
        return self._session.invalidate(*args, **kwargs)  # pragma:no cover

    def is_modified(self, *args, **kwargs):
        """Proxy for ``self._session.is_modified()``."""
        return self._session.is_modified(*args, **kwargs)  # pragma:no cover

    def merge(self, *args, **kwargs):
        """Proxy for ``self._session.merge()``."""
        return self._session.merge(*args, **kwargs)  # pragma:no cover

    def prepare(self, *args, **kwargs):
        """Proxy for ``self._session.prepare()``."""
        return self._session.prepare(*args, **kwargs)  # pragma:no cover

    def prune(self, *args, **kwargs):
        """Proxy for ``self._session.prune()``."""
        return self._session.prune(*args, **kwargs)  # pragma:no cover

    def refresh(self, *args, **kwargs):
        """Proxy for ``self._session.refresh()``."""
        return self._session.refresh(*args, **kwargs)  # pragma:no cover

    def rollback(self, *args, **kwargs):
        """Proxy for ``self._session.rollback()``."""
        return self._session.rollback(*args, **kwargs)  # pragma:no cover

    def scalar(self, *args, **kwargs):
        """Proxy for ``self._session.scalar()``."""
        return self._session.scalar(*args, **kwargs)  # pragma:no cover
