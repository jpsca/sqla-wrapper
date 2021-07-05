import shutil
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Union

from alembic import autogenerate, util
from alembic.config import Config
from alembic.runtime.environment import EnvironmentContext
from alembic.script import ScriptDirectory
from alembic.script.base import Script

from .sqlalchemy_wrapper import SQLAlchemy


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
        mkdir: bool = True,
        context: Optional[dict[str, Any]] = None,
        **options,
    ):
        self.db = db
        self.script_path = script_path = Path(script_path).absolute()
        options["script_location"] = str(script_path)
        self.config = self._get_config(options)

        if mkdir:
            self.mkdir(script_path)

        self.script_directory = ScriptDirectory.from_config(self.config)
        self.context = context or {}

    def mkdir(self, script_path: Path) -> None:
        script_path.mkdir(exist_ok=True)
        src_path = (
            Path(self.config.get_template_directory()) / "generic" / TEMPLATE_FILE
        )
        dest_path = script_path / TEMPLATE_FILE
        if not dest_path.exists():
            shutil.copy(src_path, script_path)

    def head(self) -> Optional[Script]:
        """Get the latest revision."""
        heads = self.script_directory.get_revisions("heads")
        return heads[0] if heads else None

    def current(self) -> Optional[Script]:
        """Get the current revision."""
        env = EnvironmentContext(self.config, self.script_directory)
        with self.db.engine.connect() as connection:
            env.configure(connection=connection, **self.context)
            env = env.get_context()
            current_heads = env.get_current_heads()

        revisions = self.script_directory.get_revisions(current_heads)
        return revisions[0] if revisions else None

    def get_log(self, start: str = "base", end: str = "heads") -> List[Script]:
        """Get the list of revisions in the order they will run."""
        if start == "current":
            start = self.current()
            start = start.revision if start else None
        if end == "current":
            end = self.current()
            end = end.revision if end else None

        return list(self.script_directory.walk_revisions(start, end))[::-1]

    def stamp(self, target: str = "head") -> None:
        """Set the current database revision without running migrations."""

        def do_stamp(revision, context):
            return self.script_directory._stamp_revs(target, revision)

        self._run_migrations_online(do_stamp)

    def upgrade(self, target: str = "head") -> None:
        """Run migrations to upgrade database."""

        def do_upgrade(revision, context):
            return self.script_directory._upgrade_revs(target, revision)

        self._run_migrations_online(do_upgrade)

    def downgrade(self, target: int = -1) -> None:
        """Run migrations to downgrade database."""
        target = int(target)
        target = -target if target > 0 else target

        def do_downgrade(revision, context):
            return self.script_directory._downgrade_revs(str(target), revision)

        self._run_migrations_online(do_downgrade)

    def revision(
        self,
        message: str,
        *,
        empty: bool = False,
        parent: str = "head",
    ) -> Script:
        """Create a new revision.  By default, auto-generate operations by comparing models and database.

        Arguments:
            - message: str
                description of revision.
            - empty: bool
                generate just an empty migration file, not the operations.
            - parent: str
                parent revision of this new revision.

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
                "rev_id": self.rev_id(),
                "depends_on": None,
            },
        )

        def do_revision(revision, context):
            if empty:
                revision_context.run_no_autogenerate(revision, context)
            else:
                revision_context.run_autogenerate(revision, context)
            return []

        self._run_migrations_online(do_revision)

        result = list(revision_context.generate_scripts())
        return result[0]

    def rev_id(self) -> str:
        """Generate a unique id for a revision.

        By default this uses `alembic.util.rev_id`. Override this
        method to change it.
        """
        return util.rev_id()

    # Private

    def _run_migrations_online(self, fn: Callable, **kw):
        env = EnvironmentContext(self.config, self.script_directory)
        with self.db.engine.connect() as connection:
            env.configure(
                connection=connection,
                target_metadata=self.db.registry.metadata,
                fn=fn,
                **self.context,
            )
            with env.begin_transaction():
                env.run_migrations(**kw)

    def _get_config(self, options: Dict[str, str]) -> Config:
        options.setdefault("file_template", DEFAULT_FILE_TEMPLATE)
        options.setdefault("version_locations", options["script_location"])

        config = Config()
        for key, value in options.items():
            config.set_main_option(key, value)

        return config
