def get_flask_cli(alembic, name):
    from flask.cli import FlaskGroup

    group = FlaskGroup(name)
    return _get_cli(alembic, group)


def get_click_cli(alembic, name):
    from click import Group

    group = Group(name)
    return _get_cli(alembic, group)


def _get_cli(alembic, group):
    import click

    @group.command()
    @click.argument("message", default=None)
    @click.option(
        "--empty", is_flag=True, default=False,
        help="Generate just an empty migration file, not the operations.",
    )
    @click.option(
        "--parent", default=None,
        help="Parent revision of this new revision.",
    )
    def revision(message, empty, parent):
        """Create a new revision.
        Auto-generate operations by comparing models and database.
        """
        alembic.revision(message, empty=empty, parent=parent)

    @group.command()
    @click.argument("target", default="head")
    @click.option(
        "--sql", is_flag=True, default=False,
        help="Don't emit SQL to database, dump to standard output instead",
    )
    def upgrade(target, sql):
        """Run migrations to upgrade database."""
        alembic.upgrade(target, sql=sql)

    @group.command()
    @click.argument("target", default="-1")
    @click.option(
        "--sql", is_flag=True, default=False,
        help="Don't emit SQL to database, dump to standard output instead",
    )
    def downgrade(target, sql):
        """Revert to a previous version"""
        alembic.downgrade(target, sql=sql)

    @group.command()
    @click.option(
        "-v", "--verbose", is_flag=True, default=False,
        help="Shows also the path and the docstring of each revision file.",
    )
    @click.option(
        "-s", "--start", default="base",
        help="From this revision (including it.)",
    )
    @click.option(
        "-e", "--end", default="head",
        help="To this revision (including it.)",
    )
    def history(verbose, start, end):
        """Get the list of revisions in chronological order.
        You can optionally specify the range of revisions to return.
        """
        alembic.history(verbose=verbose, start=start, end=end)

    @group.command()
    @click.argument("target", default="head")
    @click.option(
        "--sql", is_flag=True, default=False,
        help="Don't emit SQL to database - dump to standard output instead",
    )
    @click.option(
        "--purge", is_flag=True, default=False,
        help="Delete all entries in the version table before stamping.",
    )
    def stamp(target, sql, purge):
        """Set the given revision in the revision table.
        Don't run migrations."""
        alembic.stamp(target, sql=sql, purge=purge)

    @group.command()
    @click.option(
        "-v", "--verbose", is_flag=True, default=False,
        help="Shows also the path and the docstring of the revision file.",
    )
    def current(verbose):
        """Print the latest revision(s) applied."""
        alembic.current(verbose=verbose)

    @group.command()
    @click.option(
        "-v", "--verbose", is_flag=True, default=False,
        help="Shows also the path and the docstring of the revision file.",
    )
    def head(verbose):
        """Print the latest revision(s)."""
        alembic.head(verbose=verbose)

    @group.command()
    @click.argument("path", default=None)
    def init(path):
        """Creates a new migration folder
        with a `script.py.mako` template file. It doesn't fail if the
        folder or file already exists.
        """
        alembic.init(path)

    @group.command()
    def create_all():
        """Create all the tables from the current models
        and stamp the latest revision without running any migration.
        """
        alembic.create_all()

    return group
