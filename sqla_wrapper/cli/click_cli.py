def get_cli(alembic):
    import click

    @click.group()
    def db():
        """Database migrations operations."""
        pass  # pragma: no cover

    @db.command()
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

    @db.command()
    @click.argument("target", default="head")
    @click.option(
        "--sql", is_flag=True, default=False,
        help="Don't emit SQL to database, dump to standard output instead",
    )
    def upgrade(target, sql):
        """Run migrations to upgrade database."""
        alembic.upgrade(target, sql=sql)

    @db.command()
    @click.argument("target", default="-1")
    @click.option(
        "--sql", is_flag=True, default=False,
        help="Don't emit SQL to database, dump to standard output instead",
    )
    def downgrade(target, sql):
        """Revert to a previous version"""
        alembic.downgrade(target, sql=sql)

    @db.command()
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
    def history(start, end):
        """Get the list of revisions in chronological order.
        You can optionally specify the range of revisions to return.
        """
        alembic.history(start=start, end=end)

    @db.command()
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

    @db.command()
    @click.option(
        "-v", "--verbose", is_flag=True, default=False,
        help="Shows also the path and the docstring of the revision file.",
    )
    def current(verbose):
        """Print the latest revision(s) applied."""
        alembic.current(verbose=verbose)

    @db.command()
    @click.option(
        "-v", "--verbose", is_flag=True, default=False,
        help="Shows also the path and the docstring of the revision file.",
    )
    def head(verbose):
        """Print the latest revision(s)."""
        alembic.head(verbose=verbose)

    @db.command()
    @click.argument("path", default=None)
    def init(path):
        """Creates a new migration folder
        with a `script.py.mako` template file. It doesn't fail if the
        folder or file already exists.
        """
        alembic.init(path)

    return db
