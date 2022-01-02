

def get_proper_cli(alembic):
    import proper_cli  # type: ignore

    return type(
        "DBCli",
        (proper_cli.Cli,),
        {
            "__doc__": """Database migrations operations.""",

            "revision": alembic.revision,
            "upgrade": alembic.upgrade,
            "downgrade": alembic.downgrade,
            "history": alembic.history,
            "stamp": alembic.stamp,
            "head": alembic.head,
            "current": alembic.current,
            "init": alembic.init,
            "create_all": alembic.create_all,
        },
    )
