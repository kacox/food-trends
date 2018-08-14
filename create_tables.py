"""
Code to create tables in Food Trends application.

Run directly to create (empty) tables from scratch.
"""

# imports
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


### DEFINE TABLES

# MetaData: a collection of Table objects and their associated schema 
# constructs.
metadata = MetaData()

food_terms = Table("food_terms", metadata,
     Column("id", Integer, primary_key=True, autoincrement=True), 
     Column("term", String(30), nullable=False))

pairings = Table("pairings", metadata,
     Column("pairing_id", BigInteger, primary_key=True, autoincrement=True),
     Column("food_id1", Integer, ForeignKey("food_terms.id"), nullable=False),
     Column("food_id2", Integer, ForeignKey("food_terms.id"), nullable=False),
     Column("search_id", BigInteger, ForeignKey("searches.id"), nullable=False))

searches = Table("searches", metadata,
     Column("id", BigInteger, primary_key=True, autoincrement=True),
     Column("user_timestamp", DateTime, nullable=False),
     Column("search_window_start", DateTime, nullable=False),
     Column("search_window_end", DateTime, nullable=False),
     Column("food_id", Integer, ForeignKey("food_terms.id"), nullable=False),
     Column("num_matches_total", Integer, nullable=False))

results = Table("results", metadata,
     Column("id", BigInteger, primary_key=True, autoincrement=True),
     Column("publish_date", DateTime, nullable=False),
     Column("index_date", DateTime, nullable=False),
     Column("url", String(150), nullable=False),
     Column("search_id", BigInteger, ForeignKey("searches.id"), nullable=False))


if __name__ == '__main__':
     """Create tables if script run directly."""

     ### CREATE ENGINE (core interface to db)
     engine = create_engine("postgresql:///food_trends", echo=True)

     ### CREATE TABLES IN DB
     ans = input("Are you sure you want to make the tables? (Y/N) ")
     if ans.upper() == "Y":
          # create tables
          metadata.create_all(engine)
          # report completion
          print("Tables made in db.")