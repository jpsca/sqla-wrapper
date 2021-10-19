import shutil
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

from alembic import autogenerate, util
from alembic.config import Config
from alembic.runtime.environment import EnvironmentContext
from alembic.script import Script, ScriptDirectory

from .cli import click_cli, pyceo_cli
from .sqlalchemy_wrapper import SQLAlchemy


__all__ = ("Alembic",)

StrPath = Union[str, Path]
DEFAULT_FILE_TEMPLATE = "%%(year)d_%%(month).2d_%%(day).2d_%%(rev)s_%%(slug)s"
TEMPLATE_FILE = "script.py.mako"


class Alembic(object):
    """Provide an Alembic environment and migration API.

    See the
    [alembic documentation](https://alembic.sqlalchemy.org/en/latest/tutorial.html#editing-the-ini-file)
    for more details about the options.

    Arguments:
    - db:
        A `sqla_wrapper.SQLAlchemy` instance.
    - script_path:
        Path to the migrations folder.
    - context:
        ...
    - **options:
        Other alembic options

    """

    def __init__(
        self,
        db: SQLAlchemy,
        script_path: StrPath = "db/migrations",
        *,
        init: bool = True,
        context: Optional[Dict[str, Any]] = None,
        **options,
    ) -> None:
        self.db = db
        self.script_path = script_path = Path(script_path).absolute()
        script_path.mkdir(exist_ok=True)
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
    ) -> Optional[Script]:
        """Create a new revision.
        Auto-generate operations by comparing models and database.

        Arguments:
        - message:
            Revision message.
        - empty:
            Generate just an empty migration file, not the operations.
        - parent:
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
        - target:
            Revision target or "from:to" range if `sql=True`. "head"
            by default.
        - sql:
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
        - target:
            Revision target as an integer relative to the current
            state (e.g.: "-1"), or as a "from:to" range if `sql=True`.
            "-1" by default.
        - sql:
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

    def _get_history(
        self, *, start: Optional[str] = None, end: Optional[str] = None
    ) -> List[Script]:
        """Get the list of revisions in chronological order.
        You can optionally specify the range of revisions to return.

        Arguments:
        - start:
            From this revision (including it.)
        - end:
            To this revision (including it.)

        """
        if start == "current":
            current = self._get_current()
            start = current.revision if current else None
        if end == "current":
            current = self._get_current()
            end = current.revision if current else "heads"

        return list(
            self.script_directory.walk_revisions(start or "base", end or "heads")
        )[::-1]

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
        - verbose:
            If `True`, shows also the path and the docstring
            of each revision file.
        - start:
            Optional starting revision (including it.)
        - end:
            Optional end revision (including it.)

        """
        for rev in self._get_history(start=start, end=end):
            if verbose:
                print("-" * 20)
            print(
                rev.cmd_format(
                    verbose=verbose,
                    include_doc=True,
                    include_parents=True,
                )
            )

    def stamp(
        self, target: str = "head", *, sql: bool = False, purge: bool = False
    ) -> None:
        """Set the given revision in the revision table. Don't run migrations.

        Arguments:
        - target:
            The target revision; "head" by default.
        - sql:
            Don't emit SQL to the database, dump to the standard
            output instead.
        - purge:
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

    def _get_currents(self) -> Tuple[Script, ...]:
        """Get the latest revisions applied."""
        env = EnvironmentContext(self.config, self.script_directory)
        with self.db.engine.connect() as connection:
            env.configure(connection=connection, **self.context)
            migration_context = env.get_context()
            current_heads = migration_context.get_current_heads()

        return self.script_directory.get_revisions(current_heads)

    def _get_current(self) -> Optional[Script]:
        revisions = self._get_currents()
        return revisions[0] if revisions else None

    def current(self, verbose: bool = False) -> None:
        """Print the latest revision(s) applied.

        Arguments:
        - verbose:
            If `True`, shows also the path and the docstring
            of the revision file.

        """
        rev = self._get_current()
        if rev:
            print(
                rev.cmd_format(
                    verbose=verbose,
                    include_doc=True,
                    include_parents=True,
                )
            )

    def _get_heads(self) -> Tuple[Script, ...]:
        """Get the list of the latest revision."""
        return self.script_directory.get_revisions("heads")

    def _get_head(self) -> Optional[Script]:
        """Get the latest revision."""
        heads = self._get_heads()
        return heads[0] if heads else None

    def head(self, verbose: bool = False) -> None:
        """Print the latest revision(s).

        Arguments:
        - verbose:
            If `True`, shows also the path and the docstring
            of the revision file.

        """
        rev = self._get_head()
        if rev:
            print(
                rev.cmd_format(
                    verbose=verbose,
                    include_doc=True,
                    include_parents=True,
                )
            )

    def init(self, script_path: StrPath) -> None:
        """Creates a new migration folder
        with a `script.py.mako` template file. It doesn't fail if the
        folder or file already exists.

        Arguments:
        - script_path:
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

    def create_all(self) -> None:
        """Create all the tables from the current models
        and stamp the latest revision without running any migration.
        """
        self.db.create_all()
        self.stamp()

    def get_pyceo_cli(self) -> Any:
        return pyceo_cli.get_pyceo_cli(self)

    def get_click_cli(self, name="db") -> Any:
        return click_cli.get_click_cli(self, name)

    def get_flask_cli(self, name="db") -> Any:
        return click_cli.get_flask_cli(self, name)

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
