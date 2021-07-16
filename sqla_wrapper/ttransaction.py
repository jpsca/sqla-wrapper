from sqlalchemy import event


class TestTransaction:
    """Helper for building sessions that rollback everyting at the end.

    See: https://docs.sqlalchemy.org/en/14/orm/session_transaction.html#session-external-transaction
    """
    def __init__(self, db, savepoint=False):
        self.connection = db.engine.connect()
        self.trans = self.connection.begin()
        self.session = db.session_factory(bind=self.connection)

        if savepoint:
            # if the database supports SAVEPOINT (SQLite needs a
            # special config for this to work), starting a savepoint
            # will allow tests to also use rollback within tests
            self.nested = self.connection.begin_nested()

            @event.listens_for(self.session, "after_transaction_end")
            def end_savepoint(session, transaction):
                if not self.nested.is_active:
                    self.nested = self.connection.begin_nested()

    def close(self):
        self.session.close()
        self.trans.rollback()
        self.connection.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
