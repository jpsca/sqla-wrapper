def get_cli(alembic):
    import pyceo

    return type(
        "DBCli",
        (pyceo.Cli,),
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
        },
    )
