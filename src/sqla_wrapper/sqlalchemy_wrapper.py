import typing as t

import sqlalchemy as sa
from sqlalchemy import orm as sa_orm
from sqlalchemy.event import listens_for as sa_listens_for

from .base_model import BaseModel
from .session import PatchedScopedSession, Session


__all__ = ("SQLAlchemy", "TestTransaction")


class SQLAlchemy:
    """Create a SQLAlchemy connection

    This class creates an engine, a base class for your models, and a scoped session.

    The string form of the URL is
    `dialect[+driver]://user:password@host/dbname[?key=value..]`,
    where dialect is a database name such as mysql, postgresql, etc., and driver the
    name of a DBAPI, such as psycopg2, pyodbc, etc.

    Instead of the connection URL you can also specify dialect (plus optional driver),
    user, password, host, port, and database name as separate arguments.

    Please review the
    [Database URLs](https://docs.sqlalchemy.org/en/20/core/engines.html#database-urls)
    section of the SQLAlchemy documentation, for general guidelines in composing
    URL strings. In particular, special characters, such as those often part of
    passwords, must be URL-encoded to be properly parsed.

    Example:

    ```python
    db = SQLAlchemy(database_uri)
    # or SQLAlchemy(dialect=, name= [, user=] [, password=] [, host=] [, port=])

    class Base(db.Model):
        pass

    class User(Base):
        __tablename__ = "users"
        id: Mapped[int] = mapped_column(primary_key=True)
        name: Mapped[str] = mapped_column(sa.String(80), unique=True)
        deleted: Mapped[datetime] = mapped_column(sa.DateTime)
    ```

    """

    def __init__(
        self,
        url: "str | None" = None,
        *,
        dialect: str = "sqlite",
        name: "str | None" = None,
        user: "str | None" = None,
        password: "str | None" = None,
        host: "str | None" = None,
        port: "str | int | None" = None,
        engine_options: "t.Dict[str, t.Any] | None" = None,
        session_options: "t.Dict[str, t.Any] | None" = None,
        base_model_class: t.Any = BaseModel,
        base_model_metaclass: t.Any = sa_orm.DeclarativeMeta,
    ) -> None:
        self.url = url or self._make_url(
            dialect=dialect,
            host=host,
            name=name,
            user=user,
            password=password,
            port=port,
        )
        engine_options = engine_options or {}
        engine_options.setdefault("future", True)
        self.engine = sa.create_engine(self.url, **engine_options)

        self.registry = sa_orm.registry()
        self.Model = self.registry.generate_base(
            cls=base_model_class,
            name="Model",
            metaclass=base_model_metaclass
        )

        session_options = session_options or {}
        session_options.setdefault("class_", Session)
        session_options.setdefault("bind", self.engine)
        session_options.setdefault("future", True)
        self.session_class = session_options["class_"]
        self.Session = sa_orm.sessionmaker(**session_options)
        self.s = PatchedScopedSession(self.Session)

    def create_all(self, **kwargs) -> None:
        """Creates all the tables of the models registered so far.

        Only tables that do not already exist are created. Existing tables are
        not modified.
        """
        kwargs.setdefault("bind", self.engine)
        self.registry.metadata.create_all(**kwargs)

    def drop_all(self, **kwargs) -> None:
        """Drop all the database tables.

        Note that this is a destructive operation; data stored in the
        database will be deleted when this method is called.
        """
        kwargs.setdefault("bind", self.engine)
        self.registry.metadata.drop_all(**kwargs)

    def test_transaction(self, savepoint: bool = False) -> "TestTransaction":
        return TestTransaction(self, savepoint=savepoint)

    def _make_url(
        self,
        dialect: str,
        *,
        user: "str | None" = None,
        password: "str | None" = None,
        host: "str | None" = None,
        port: "str | int | None" = None,
        name: "str | None" = None,
    ) -> str:
        url_parts = [f"{dialect}://"]
        if user:
            url_parts.append(user)
            if password:
                url_parts.append(f":{password}")
            url_parts.append("@")

        if not host and not dialect.startswith("sqlite"):
            host = "127.0.0.1"

        if host:
            url_parts.append(f"{host}")
            if port:
                url_parts.append(f":{port}")

        if name:
            url_parts.append(f"/{name}")
        return "".join(url_parts)

    def __repr__(self) -> str:
        return f"<SQLAlchemy('{self.url}')>"


class TestTransaction:
    """Helper for building sessions that rollback everyting at the end.

    See ["Joining a Session into an External Transaction"](https://docs.sqlalchemy.org/en/20/orm/session_transaction.html#session-external-transaction)
    in the SQLAlchemy documentation.
    """
    def __init__(self, db: SQLAlchemy, savepoint: bool = False) -> None:
        self.connection = db.engine.connect()
        self.trans = self.connection.begin()
        self.session = db.Session(bind=self.connection)
        db.s.registry.set(self.session)

        if savepoint:  # pragma: no branch
            # if the database supports SAVEPOINT (SQLite needs a
            # special config for this to work), starting a savepoint
            # will allow tests to also use rollback within tests
            self.nested = self.connection.begin_nested()

            @sa_listens_for(target=self.session, identifier="after_transaction_end")
            def end_savepoint(session, transaction):
                if not self.nested.is_active:
                    self.nested = self.connection.begin_nested()

    def close(self) -> None:
        self.session.close()
        self.trans.rollback()
        self.connection.close()

    def __enter__(self) -> "TestTransaction":  # pragma: no cover
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:  # pragma: no cover
        self.close()
