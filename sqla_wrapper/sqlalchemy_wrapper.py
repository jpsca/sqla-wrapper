from typing import Any, Optional

from sqlalchemy import create_engine
from sqlalchemy.orm import registry, scoped_session, sessionmaker

from .active_record_mixin import get_active_record_mixin


class SQLAlchemy:
    """This class is used to easily instantiate a SQLAlchemy connection to
    a database, to provide a base class for your models, and to get a session
    to interact with them.

    The string form of the URL is `dialect[+driver]://user:password@host/dbname[?key=value..]`,
    where dialect is a database name such as mysql, postgresql, etc., and driver the
    name of a DBAPI, such as psycopg2, pyodbc, etc.

    Instead of the connection URL you can also specify dialect (plus optional driver), user, password,
    host, port, and database name as separate arguments.

    Please review the [Database URLs](https://docs.sqlalchemy.org/en/14/core/engines.html#database-urls)
    section of the SQLAlchemy documentation, for general guidelines in composing URL strings.
    In particular, special characters, such as those often part of passwords, must be URL encoded to be properly parsed.

    Example:

        ```python
        db = SQLAlchemy(database_uri)
        # or SQLAlchemy(dialect=, name= [, user=] [, password=] [, host=] [, port=])

        class Base(db.Model):
            pass

        class User(Base):
            __tablename__ = "users"
            id = Column(Integer, primary_key=True)
            login = Column(String(80), unique=True)
            deleted = Column(DateTime)
        ```

        **IMPORTANT**

        In a web application or a multithreaded environment you need to call
        ``session.remove()`` when a request/thread ends. Use your framework's
        ``after_request`` hook, to do that. For example, in `Flask`:

        ```python
        app = Flask(…)
        db = SQLAlchemy(…)

        @app.teardown_appcontext
        def shutdown(response=None):
            db.session.remove()
            return response
        ```

    """

    def __init__(
        self,
        url: Optional[str] = None,
        *,
        dialect: str = "sqlite",
        name: Optional[str] = None,
        user: Optional[str] = None,
        password: Optional[str] = None,
        host: Optional[str] = None,
        port: Optional[str] = None,
        engine_options: Optional[dict[str, Any]] = None,
        session_options: Optional[dict[str, Any]] = None,
    ):
        self.url = url or self._make_url(
            dialect=dialect,
            host=host,
            name=name,
            user=user,
            password=password,
            port=port,
        )
        engine_options = engine_options or {}
        engine_options["future"] = True
        self.engine = create_engine(self.url, **engine_options)

        session_options = session_options or {}
        session_options["bind"] = self.engine
        session_options["future"] = True
        session_factory = sessionmaker(**session_options)
        self.session = scoped_session(session_factory)

        self.registry = registry()
        self.Model = self._get_base_model_class()

    def create_all(self, **kw):
        """Creates all tables."""
        kw.setdefault("bind", self.engine)
        self.registry.metadata.create_all(**kw)

    def drop_all(self, **kw):
        """Drops all tables."""
        kw.setdefault("bind", self.engine)
        self.registry.metadata.drop_all(**kw)

    def _make_url(
        self,
        dialect: str,
        *,
        user: Optional[str] = None,
        password: Optional[str] = None,
        host: Optional[str] = None,
        port: Optional[str] = None,
        name: Optional[str] = None,
    ) -> str:
        url_parts = [f"{dialect}://"]
        if user:
            url_parts.append(user)
            if password:
                url_parts.append(f":{password}")
        if host:
            url_parts.append(f"@{host}")
            if port:
                url_parts.append(f":{port}")
        if name:
            url_parts.append(f"/{name}")
        return "".join(url_parts)

    def _get_base_model_class(self):
        ActiveRecordMixin = get_active_record_mixin(self.session)
        DeclarativeBase = self.registry.generate_base()
        attrs = {
            "__doc__": "Baseclass for custom user models.",
            "__abstract__": True,
        }
        return type("Model", (ActiveRecordMixin, DeclarativeBase), attrs)

    def __repr__(self):
        return f"<SQLAlchemy('{self.url}')>"
