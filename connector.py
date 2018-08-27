"""Abstraction of database functions using a stand-alone class.

From the docs:
'The typical usage of create_engine() is once per particular database URL, 
held globally for the lifetime of a single application process. A single 
Engine manages many individual DBAPI connections on behalf of the process and 
is intended to be called upon in a concurrent fashion. The Engine is not 
synonymous to the DBAPI connect function, which represents just one connection 
resource - the Engine is most efficient when created just once at the module 
level of an application, not per-object or per-function call.'
"""

from sqlalchemy import create_engine, MetaData


class DBConnector():
    """Handles database interactions with Flask app."""

    def __init__(self, db_uri):
        self.engine = create_engine(db_uri, echo=False)
        print("Connected to DB.")
        self.meta = None

    def reflect(self):
        """Load table information from the database."""
        meta = MetaData()
        meta.reflect(bind=self.engine)

        # want to be able to access tables through instance attr
        self.meta = meta

    def execute(self, statement):
        """Wrapper to execute a SQL construct."""
        with self.engine.connect() as conn:
            return conn.execute(statement)