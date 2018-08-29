"""Code to create tables in Food Trends application.

Run directly to create (empty) tables from scratch.
"""

from sqlalchemy import create_engine
from sqlalchemy import Table, Column, MetaData, ForeignKey
from sqlalchemy import Integer, String, BigInteger, DateTime

"""
NOTE TO SELF:
The Engine, when first returned by create_engine(), has not actually tried to 
connect to the database yet; that happens only the first time it is asked to 
perform a task against the database. So, the first time a method like 
Engine.execute() or Engine.connect() is called, THEN the Engine establishes a 
real DBAPI connection to the database, which is then used to emit the SQL.
"""

metadata = MetaData()

food_terms = Table("food_terms", metadata,
     Column("id", Integer, primary_key=True, autoincrement=True), 
     Column("term", String(30), nullable=False, unique=True))

pairings = Table("pairings", metadata,
     Column("pairing_id", BigInteger, primary_key=True, autoincrement=True),
     Column("food_id1", Integer, ForeignKey("food_terms.id"), nullable=False),
     Column("food_id2", Integer, ForeignKey("food_terms.id"), nullable=False),
     Column("search_id", BigInteger, ForeignKey("searches.id"), nullable=False), 
     Column("occurences", Integer, nullable=False))

searches = Table("searches", metadata,
     Column("id", BigInteger, primary_key=True, autoincrement=True),
     Column("user_timestamp", DateTime, nullable=False),
     Column("search_window", String(10), nullable=False),
     Column("food_id", Integer, ForeignKey("food_terms.id"), nullable=False),
     Column("num_matches_total", Integer, nullable=False),
     Column("num_matches_returned", Integer, nullable=False))

results = Table("results", metadata,
     Column("id", BigInteger, primary_key=True, autoincrement=True),
     Column("publish_date", DateTime, nullable=False),
     Column("index_date", DateTime, nullable=False),
     Column("url", String(300), nullable=False),
     Column("search_id", BigInteger, ForeignKey("searches.id"), nullable=False))


if __name__ == '__main__':
     """Create tables if script run directly."""
     engine = create_engine("postgresql:///food_trends", echo=True)

     ans = input("Are you sure you want to make the tables? (Y/N) ")
     if ans.upper() == "Y":
          metadata.create_all(engine, checkfirst=True)
          print("Tables made in db.")