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
from sqlalchemy.sql import select


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

    def search_record(self, search_id):
        """Retrieve the search record associated with search_id."""
        searches = self.meta.tables["searches"]
        selection = select([searches]).where(searches.c.id == search_id)
        
        return self.execute(selection).fetchone()

    def pairings_by_search(self, search_id):
        """Retrieve pairing records associated with search_id."""
        pairings = self.meta.tables["pairings"]
        selection = select([pairings]).where(pairings.c.search_id == search_id)
        
        return self.execute(selection).fetchall()

    def term_by_id(self, term_id):
        """Retrieve food term using its id."""
        food_terms = self.meta.tables["food_terms"]
        selection = select([food_terms]).where(food_terms.c.id == term_id)
        
        return self.execute(selection).fetchone()