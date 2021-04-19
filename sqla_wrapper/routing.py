from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session, Session


def get_routing_class(engines):

    class RoutingSession(_Session):
        def get_bind(self, mapper=None, clause=None):
            if mapper is not None:
                bind_key = getattr(mapper.class_, '__bind_key__', 'default')
                return engines[bind_key]
            return Session.get_bind(self, mapper, clause)

    return RoutingSession
