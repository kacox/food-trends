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

from datetime import datetime

from sqlalchemy import create_engine, MetaData
from sqlalchemy.sql import select
from sqlalchemy.exc import IntegrityError


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

    def new_search_record(self, term_id, num_matches_total, 
                                            num_matches_returned):
        """Make a new search record in the database.

        Return the id of the newly inserted record.
        """
        searches = self.meta.tables["searches"]
        ins = searches.insert().values(user_timestamp=datetime.utcnow(), 
                                   search_window="tspan:w", 
                                   food_id=term_id, 
                                   num_matches_total=num_matches_total,
                                   num_matches_returned=num_matches_returned)
        result = self.execute(ins)
        return result.inserted_primary_key[0]

    def new_food_term_record(self, food_term):
        """Make a new record in the food_terms table.

        Return the id of the newly inserted record.
        """
        self.reflect()
        food_terms = self.meta.tables['food_terms']
        ins = food_terms.insert().values(term=food_term.lower())

        # want to execute statment then get food term's id
        try:
            result = self.execute(ins)
            term_id = result.inserted_primary_key[0]
        except IntegrityError:
            # sqlalchemy wraps psycopg2.IntegrityError with its own exception
            print("This food term is already in the table.")
            term_id = self.id_by_term(food_term=food_term.lower())

        return term_id

    def new_results_record(self, post, search_id):
        """Make a new record in the results table.

        Fields to include: publish_date, index_date, url, search_id.
        """
        publish_date, index_date = post.published_at, post.indexed_at
        post_url = post.url
        results = self.meta.tables["results"]

        selection = select([results]).where(results.c.url == post_url)
        result = self.execute(selection)

        # do not want redundant URLs in table
        if result:
            ins = results.insert().values(publish_date=publish_date, 
                                           index_date=index_date, 
                                           url=post_url, 
                                           search_id=search_id)
            self.execute(ins)

    def new_pairings_record(self, search_term_id, other_term_id, 
                                                search_id, count):
        """Make a new record in the pairings table."""
        pairings = self.meta.tables["pairings"]
        ins = pairings.insert().values(food_id1=search_term_id, 
                                   food_id2=other_term_id, 
                                   search_id=search_id, 
                                   occurences=count)
        self.execute(ins)

    def search_record_by_id(self, search_id):
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

    def id_by_term(self, food_term):
        """Retrieve a food term's id by the term itself."""
        food_terms = self.meta.tables["food_terms"]
        selection = select([food_terms]).where(food_terms.c.term == food_term)
        result = self.execute(selection)

        return result.fetchone()[0]