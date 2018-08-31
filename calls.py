"""API calls  and their helper fxns for Food Trends application."""

import os
import requests
import json
from datetime import datetime

from sqlalchemy import Table
from sqlalchemy.sql import select
from sqlalchemy.exc import IntegrityError
from twingly_search import Client
from flask import session

from connector import DBConnector
import mock_spoonacular
import mock_twingly


MASHAPE_KEY = os.environ.get("MASHAPE_KEY")
# TWINGLY_SEARCH_KEY pulled from environment variables by library

# several fxns need to access the database
DB_PATH = "postgresql:///food_trends"
db = DBConnector(DB_PATH)

#####################################################################
def get_food_terms(input_text, api_key):
    """Get food terms from input text using Spoonacular API.

    Return list of food terms (dupes removed).
    """
    if api_key:
        endpoint_url = "https://spoonacular-recipe-food-nutrition-v1.p.mashape.com/food/detect"
        payload = {"text": input_text}
        headers = {"X-Mashape-Key": api_key,
                    "Content-Type": "application/x-www-form-urlencoded",
                    "Accept": "application/json"}
        r = requests.post(endpoint_url, data=payload, headers=headers)
        
    response_content = json.loads(r.text)
    return terms_from_response(response_content)

    # MOCK RESPONSE FOR DEV
    #return mock_spoonacular.mock_get_food_terms(input_text)


def terms_from_response(response_content):
    """Extract food terms from response.

    Input is Python object representation of JSON response; in this case a 
    dictionary.

    Return list of food term strings.
    """
    terms = set()
    for term in response_content["annotations"]:
        terms.add(term["annotation"])

    return list(terms)


#### I HAVE LIMITED ACCESS TO THIS API; USE MOCK FOR DEV
def find_store_matches(food_term):
    """Make call to Twingly Blog Search API. 

    Search blog post TITLES using the food term. Store relevant response
    information in the database.
    """
    # # real API call
    # q = build_twingly_query(food_term, "tspan:w")
    # client = Client()
    # results = client.execute_query(q)

    # FAKE API CALL
    results = mock_twingly.mock_api_call()

    term_id = food_terms_record(food_term)
    search_id = make_searches_record(results.number_of_matches_total, 
                                        results.number_of_matches_returned,
                                        term_id)
    process_blog_results(results, search_id, food_term)

    # want to access search id in several routes
    session["search_id"] = search_id


def build_twingly_query(food_term, search_window):
    """Build query string for Twingly Blog Search API."""
    return (food_term + " fields:title lang:en page-size:20 sort:created " + 
            search_window)


#### TODO: ABSTRACT TO DB CLASS
def food_terms_record(food_term):
    """Add a food term to the food_terms table if not there.

    This function should run when new searches are made.

    Return the id of the inserted term.
    """
    db.reflect()
    food_terms = db.meta.tables['food_terms']
    ins = food_terms.insert().values(term=food_term.lower())

    # want to execute statment then get food term's id
    try:
        result = db.execute(ins)
        term_id = result.inserted_primary_key[0]
    except IntegrityError:
        # sqlalchemy wraps psycopg2.IntegrityError with its own exception
        print("This food term is already in the table.")
        term_id = get_term_id(food_term=food_term.lower())

    return term_id


def get_term_id(food_term):
    """Get and return the id of a given food term in the db."""
    food_terms = db.meta.tables["food_terms"]
    selection = select([food_terms]).where(food_terms.c.term == food_term)
    result = db.execute(selection)

    return result.fetchone()[0]


#### TODO: ABSTRACT TO DB CLASS
def make_searches_record(num_matches_total, num_matches_returned, term_id):
    """Add a record to the searches table.

    Fields to include: user_timestamp, search_window, food_id, 
                       num_matches_total, num_matches_returned
    """
    ts = datetime.utcnow()
    search_window = "tspan:w"
    searches = db.meta.tables["searches"]

    ins = searches.insert().values(user_timestamp=ts, 
                                   search_window=search_window, 
                                   food_id=term_id, 
                                   num_matches_total=num_matches_total,
                                   num_matches_returned=num_matches_returned)
    result = db.execute(ins)

    return result.inserted_primary_key[0]


def process_blog_results(results, search_id, search_term):
    """Put desired data from blog search results into database."""

    # want to keep the search term separate from other food terms
    other_terms_dict = {}

    for post in results.posts:
        make_results_record(post, search_id)
        post_title = post.title

        other_terms = get_food_terms(post_title, MASHAPE_KEY)

        # clean so that search term is not in other_terms
        if search_term in other_terms:
            other_terms.remove(search_term)

        for term in other_terms:
            if term in other_terms_dict.keys():
                other_terms_dict[term] += 1
            else:
                other_terms_dict[term] = 1

    if other_terms_dict != {}:
        build_pairs(search_term, search_id, other_terms_dict)


#### TODO: ABSTRACT TO DB CLASS
def make_results_record(post, search_id):
    """Add a record to the results table.

    Fields to include: publish_date, index_date, url, search_id
    """
    publish_date, index_date, post_url = dissect_post(post)
    results = db.meta.tables["results"]

    selection = select([results]).where(results.c.url == post_url)
    result = db.execute(selection)

    # do not want redundant URLs in table
    if not result:
        ins = results.insert().values(publish_date=publish_date, 
                                       index_date=index_date, 
                                       url=post_url, 
                                       search_id=search_id)
        db.execute(ins)


def dissect_post(post):
    """Get publish_date, index_date, and post_url from blog post.

    Post object attributes:
        published_at  (datetime.datetime)
        indexed_at    (datetime.datetime)
        url           (string)
    """
    return post.published_at, post.indexed_at, post.url


def build_pairs(search_term, search_id, other_terms_dict):
    """Create pairings and put each in database."""
    pairings = db.meta.tables["pairings"]
    search_term_id = get_term_id(search_term)

    for other_term, count in other_terms_dict.items():
        other_term_id = food_terms_record(other_term)
        make_pairings_record(pairings, search_term_id, other_term_id, 
                                                    search_id, count)

#### TODO: ABSTRACT TO DB CLASS
def make_pairings_record(pairings, search_term_id, other_term_id, 
                                                search_id, count):
    """Add a record to the pairings table."""
    ins = pairings.insert().values(food_id1=search_term_id, 
                                   food_id2=other_term_id, 
                                   search_id=search_id, 
                                   occurences=count)
    db.execute(ins)


def get_search_record(search_id):
    """Retrieve the search record associated with search_id."""
    return db.search_record(search_id)


def get_search_term(term_id):
    """Retrieve the search term from its id."""
    return db.term_by_id(term_id)[1]


def get_pairings(search_id):
    """Retrieve all pairings associated with a given search id.

    Return a dictionary containing a pairing food term and the number of times 
    it occured in the search:
        {"food_term": occurences, ..., "food_term_n": occurences}
    """
    pairings = db.pairings_by_search(search_id)

    pairings_dict = {}
    for pairing in pairings:
        pairing_term = db.term_by_id(pairing[2])[1]
        occurences = pairing[4]
        pairings_dict[pairing_term] = occurences

    return pairings_dict
