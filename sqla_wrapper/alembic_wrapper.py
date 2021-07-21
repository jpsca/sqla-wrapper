import shutil
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Union

try:
    from alembic import autogenerate, util
    from alembic.config import Config
    from alembic.runtime.environment import EnvironmentContext
    from alembic.script import ScriptDirectory
    from alembic.script.revision import Revision
except ImportError:  # pragma: no cover
    pass

from .sqlalchemy_wrapper import SQLAlchemy
from .cli import click_cli, pyceo_cli


StrPath = Union[str, Path]
DEFAULT_FILE_TEMPLATE = "%%(year)d_%%(month).2d_%%(day).2d_%%(rev)s_%%(slug)s"
TEMPLATE_FILE = "script.py.mako"


class Alembic(object):
    """Provide an Alembic environment and migration API.

    See the
    [alembic documentation](https://alembic.sqlalchemy.org/en/latest/tutorial.html#editing-the-ini-file)
    for more details about the options.

    Arguments:
        - db: SQLAlchemy
            A `sqla_wrapper.SQLAlchemy` instance.
        - script_path: str | Path
            Path to the migrations folder.
        - mkdir: bool
            Whether to create the migrations folder, if it doesn't exists.
        - context: dict | None
            ...
        - **options: dict | None
            Other alembic options

    """

    def __init__(
        self,
        db: SQLAlchemy,
        *,
        script_path: StrPath = "db/migrations",
        init: bool = True,
        context: Optional[Dict[str, Any]] = None,
        **options,
    ) -> None:
        self.db = db
        self.script_path = script_path = Path(script_path).absolute()
        options["script_location"] = str(script_path)
        self.config = self._get_config(options)

        if init:
            self.init(script_path)

        self.script_directory = ScriptDirectory.from_config(self.config)
        self.context = context or {}

    def revision(
        self,
        message: str,
        *,
        empty: bool = False,
        parent: str = "head",
    ) -> Revision:
        """Create a new revision.
        Auto-generate operations by comparing models and database.

        Arguments:
            - message: str
                Revision message.
            - empty: bool
                Generate just an empty migration file, not the operations.
            - parent: str
                Parent revision of this new revision.

        """
        revision_context = autogenerate.RevisionContext(
            self.config,
            self.script_directory,
            {
                "message": message,
                "sql": False,
                "head": [parent],
                "splice": False,
                "branch_label": None,
                "version_path": self.script_directory.dir,
                "rev_id": self._rev_id(),
                "depends_on": None,
            },
        )

        def do_revision(revision, context):
            if empty:
                revision_context.run_no_autogenerate(revision, context)
            else:
                revision_context.run_autogenerate(revision, context)
            return []

        self._run_online(do_revision)

        result = list(revision_context.generate_scripts())
        return result[0]

    def upgrade(self, target: str = "head", *, sql: bool = False, **kwargs) -> None:
        """Run migrations to upgrade database.

        Arguments:
            - target: str
                Revision target or "from:to" range if `sql=True`. "head"
                by default.
            - sql: bool
                Don't emit SQL to database, dump to standard output instead.
            - **kwargs:
                Optional arguments. If these are passed, they are sent directly
                to the `upgrade()` functions within each revision file.
                To use, modify the `script.py.mako`template file
                so that the `upgrade()` functions can accept arguments.

        """
        starting_rev = None
        if ":" in target:
            if not sql:
                raise ValueError("range target not allowed")
            starting_rev, target = target.split(":")
        elif sql:
            raise ValueError("sql=True requires target=from:to")

        def do_upgrade(revision, context):
            return self.script_directory._upgrade_revs(target, revision)

        run = self._run_offline if sql else self._run_online
        run(
            do_upgrade,
            kwargs=kwargs,
            starting_rev=starting_rev,
            destination_rev=target,
        )

    def downgrade(self, target: str = "-1", *, sql: bool = False, **kwargs) -> None:
        """Run migrations to downgrade database.

        Arguments:
            - target: str
                Revision target as an integer relative to the current
                state (e.g.: "-1"), or as a "from:to" range if `sql=True`.
                "-1" by default.
            - sql: bool
                Don't emit SQL to database, dump to standard output instead.
            - **kwargs:
                Optional arguments. If these are passed, they are sent directly
                to the `downgrade()` functions within each revision file.
                To use, modify the `script.py.mako` template file
                so that the `downgrade()` functions can accept arguments.

        """

        starting_rev = None
        if isinstance(target, str) and ":" in target:
            if not sql:
                raise ValueError("range target not allowed")
            starting_rev, target = target.split(":")
        elif sql:
            raise ValueError("sql=True requires target=from:to")
        else:
            itarget = int(target)
            target = str(-itarget if itarget > 0 else itarget)

        def do_downgrade(revision, context):
            return self.script_directory._downgrade_revs(target, revision)

        run = self._run_offline if sql else self._run_online
        run(
            do_downgrade,
            kwargs=kwargs,
            starting_rev=starting_rev,
            destination_rev=target,
        )

    def _history(
        self, *, start: Optional[str] = "base", end: Optional[str] = "heads"
    ) -> List[Revision]:
        """Get the list of revisions in chronological order.
        You can optionally specify the range of revisions to return.

        Arguments:
            - start: str:
                From this revision (including it.)
            - end: str
                To this revision (including it.)

        """
        if start == "current":
            current = self.current()
            start = current.revision if current else None
        if end == "current":
            current = self.current()
            end = current.revision if current else None

        return list(self.script_directory.walk_revisions(start, end))[::-1]

    def history(
        self,
        *,
        verbose: bool = False,
        start: Optional[str] = "base",
        end: Optional[str] = "heads",
    ) -> None:
        """Print the list of revisions in chronological order.
        You can optionally specify the range of revisions to return.

        Arguments:
            - verbose: bool
                If `True`, shows also the path and the docstring
                of each revision file.
            - start: str:
                Optional starting revision (including it.)
            - end: str
                Optional end revision (including it.)

        """
        for rev in self._history(start=start, end=end):
            if verbose:
                print("-" * 20)
            print(rev.cmd_format(
                verbose=verbose,
                include_doc=True,
                include_parents=True,
            ))

    def stamp(
        self, target: str = "head", *, sql: bool = False, purge: bool = False
    ) -> None:
        """Set the given revision in the revision table. Don't run migrations.

        Arguments:
            - target: str
                The target revision; "head" by default.
            - sql: bool
                Don't emit SQL to the database, dump to the standard
                output instead.
            - purge: bool
                Delete all entries in the version table before stamping.

        """

        def do_stamp(revision, context):
            return self.script_directory._stamp_revs(target, revision)

        run = self._run_offline if sql else self._run_online
        run(
            do_stamp,
            destination_rev=target,
            purge=purge,
        )

    def _currents(self) -> List[Revision]:
        """Get the latest revisions applied."""
        env = EnvironmentContext(self.config, self.script_directory)
        with self.db.engine.connect() as connection:
            env.configure(connection=connection, **self.context)
            migration_context = env.get_context()
            current_heads = migration_context.get_current_heads()

        return self.script_directory.get_revisions(current_heads)

    def _current(self) -> Optional[Revision]:
        revisions = self._currents()
        return revisions[0] if revisions else None

    def current(self, verbose: bool = False) -> None:
        """Print the latest revision(s) applied.

        Arguments:
            - verbose: bool
                If `True`, shows also the path and the docstring
                of the revision file.

        """
        rev = self._current()
        if rev:
            print(rev.cmd_format(
                verbose=verbose,
                include_doc=True,
                include_parents=True,
            ))

    def _heads(self) -> List[Revision]:
        """Get the list of the latest revision."""
        return self.script_directory.get_revisions("heads")

    def _head(self) -> Optional[Revision]:
        """Get the latest revision."""
        heads = self._heads()
        return heads[0] if heads else None

    def head(self, verbose: bool = False) -> None:
        """Print the latest revision(s).

        Arguments:
            - verbose: bool
                If `True`, shows also the path and the docstring
                of the revision file.

        """
        rev = self._head()
        if rev:
            print(rev.cmd_format(
                verbose=verbose,
                include_doc=True,
                include_parents=True,
            ))

    def init(self, script_path: StrPath) -> None:
        """Creates a new migration folder
        with a `script.py.mako` template file. It doesn't fail if the
        folder or file already exists.

        Arguments:
            - script_path: str|Path
                Target folder.

        """
        script_path = Path(script_path)
        script_path.mkdir(exist_ok=True)
        src_path = (
            Path(self.config.get_template_directory()) / "generic" / TEMPLATE_FILE
        )
        dest_path = script_path / TEMPLATE_FILE
        if not dest_path.exists():
            shutil.copy(src_path, script_path)

    def get_pyceo_cli(self) -> Any:
        return pyceo_cli.get_cli(self)

    def get_click_cli(self) -> Any:
        return click_cli.get_cli(self)

    def _get_config(self, options: Dict[str, str]) -> Config:
        options.setdefault("file_template", DEFAULT_FILE_TEMPLATE)
        options.setdefault("version_locations", options["script_location"])

        config = Config()
        for key, value in options.items():
            config.set_main_option(key, value)

        return config

    def _rev_id(self) -> str:
        """Generate a unique id for a revision.

        By default this uses `alembic.util.rev_id`. Override this
        method to change it.
        """
        return util.rev_id()

    def _run_online(
        self, fn: Callable, *, kwargs: Optional[Dict] = None, **envargs
    ) -> None:
        """Emit the SQL to the database."""
        env = EnvironmentContext(self.config, self.script_directory)
        with self.db.engine.connect() as connection:
            env.configure(
                connection=connection,
                fn=fn,
                target_metadata=self.db.registry.metadata,
                **envargs,
            )
            kwargs = kwargs or {}
            with env.begin_transaction():
                env.run_migrations(**kwargs)

    def _run_offline(
        self, fn: Callable, *, kwargs: Optional[Dict] = None, **envargs
    ) -> None:
        """Don't emit SQL to the database, dump to standard output instead."""
        env = EnvironmentContext(self.config, self.script_directory)
        env.configure(
            url=self.db.url,
            fn=fn,
            target_metadata=self.db.registry.metadata,
            as_sql=True,
            **envargs,
        )
        kwargs = kwargs or {}
        with env.begin_transaction():
            env.run_migrations(**kwargs)
