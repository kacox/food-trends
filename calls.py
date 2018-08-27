"""API calls  and their helper fxns for Food Trends application."""

# imports
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

    Make call to Spoonacular (POST Detect Food in Text endpoint).
    Return list of food terms (dupes removed).
    """
    
    # check that you have the API key
    if api_key:
        # assign request arguments
        endpoint_url = "https://spoonacular-recipe-food-nutrition-v1.p.mashape.com/food/detect"
        payload = {"text": input_text}
        headers = {"X-Mashape-Key": api_key,
                    "Content-Type": "application/x-www-form-urlencoded",
                    "Accept": "application/json"}

        # make request
        r = requests.post(endpoint_url, data=payload, headers=headers)
        
    # extract food terms from response
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


def get_final_term(terms_list):
    """Choose final term to use for later queries and pair building."""

    # for now, ask in terminal which term to use
    # CHANGE LATER FOR UI SELECTION (radio buttons or drop down)
    valid_indx = False
    print("Final terms:", terms_list)
    while not valid_indx:
        print("Pick a term using its index (0 to", 
                                str(len(terms_list) - 1) + "): ")
        user_choice = input()

        # input validation
        try:
            # check if integer
            user_choice = int(user_choice)

            # check range
            if (user_choice >= 0) and (user_choice < len(terms_list)):
                # choice in valid index range
                valid_indx = True
            else:
                print("Choice is out of range.")
        except ValueError:
            print("Please choose a valid index as an integer.")
            

    # select term
    return terms_list[user_choice]


#####################################################################
#### I HAVE LIMITED ACCESS TO THIS API; USE MOCK FOR DEV
def find_matches(food_term):
    """
    Make call to Twingly Blog Search API. Search blog post TITLES using the 
    food term from get_food_term().

    Need to build a query (see below functions).

    Return dictionary with pairing matches.
    """

    # # build query string
    # search_window = get_search_window()
    # q = build_twingly_query(food_term, search_window)

    # # make the actual query
    # client = Client()
    # results = client.execute_query(q)

    # FAKE API CALL
    results = mock_twingly.mock_api_call()

    # add relevant information to dbs related to call
    term_id = food_terms_record(food_term)
    search_id = make_searches_record(results.number_of_matches_total, 
                                        results.number_of_matches_returned,
                                        term_id)

    # want to access search id in several routes
    session["search_id"] = search_id

    return process_blog_results(results, search_id, food_term)

    """
    `results` represents a result from a Query to the Search API
    Attributes:
        number_of_matches_returned (int):
                number of Posts the Query returned
        number_of_matches_total (int):
                total number of Posts the Query matched
        seconds_elapsed (float):
                number of seconds it took to execute the Query
        posts (list of Post):
                all Posts that matched the Query; list of Post objects
    """

    
def get_search_window():
    """
    Determine search window time period for next call to Twingly.

    I am restricting the search window to the past week while developing, 
    but maybe expand to last month and last three months depending on 
    average result sizes.

    FROM DOCS:
        The default is to search in posts published at any time.

        example:
        `tspan:24h`

        The supported arguments to tspan are:

            h - posts published the last hour
            12h - posts published the last 12 hours
            24h - posts published the last 24 hours
            w - posts published the last week
            m - posts published the last month
            3m - posts published the last three months

        how it would look in a final query string:        
        `q = 'github page-size: 10 lang:sv tspan:24h'`
    """
    # hard-coded for now; may change in future
    search_window = "w"
    return "tspan:" + search_window


def build_twingly_query(food_term, search_window):
    """Build query string for Twingly Blog Search API."""
    
    return (food_term + " fields:title lang:en page-size:20 sort:created " + 
            search_window)


# PARTIALLY TESTED ABOVE LINE
#####################################################################
def food_terms_record(food_term):
    """Add a food term to the food_terms table if not there.

    This function should run when new searches are made.

    Return the id of the inserted term.
    """

    db.reflect()
    food_terms = db.meta.tables['food_terms']

    # format is 'INSERT INTO food_terms (id, term) VALUES (:id, :term)'
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
    """Get desired data from blog search results."""

    # want to keep the search term separate from other food terms
    other_terms_dict = {}

    # process results post by post
    for post in results.posts:
        make_results_record(post, search_id)
        post_title = post.title

        # THIS IS THE 3RD AND FINAL ROUND OF API CALLS
        # BUILD OUT PAIRING MECHANISM FIRST (BELOW)
        other_terms = get_food_terms(post_title, MASHAPE_KEY)

        # clean so that search term is not in other_terms
        if search_term in other_terms:
            other_terms.remove(search_term)

        #print(post_title)
        #print(other_terms, "\n")

        # take food terms extracted from post and update dict
        for term in other_terms:
            if term in other_terms_dict.keys():
                # increment count
                other_terms_dict[term] += 1
            else:
                # new entry
                other_terms_dict[term] = 1


    #print(other_terms_dict, "\n")
    # other terms dict now has info from all blog posts from this search_id
    # make pairs; add pairings record for each to db ONLY IF NOT EMPTY
    if other_terms_dict != {}:
        build_pairs(search_term, search_id, other_terms_dict)

    return other_terms_dict



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
        # make a record in the pairings table
        other_term_id = food_terms_record(other_term)
        make_pairings_record(pairings, search_term_id, other_term_id, 
                                                    search_id, count)


def make_pairings_record(pairings, search_term_id, other_term_id, 
                                                search_id, count):
    """Add a record to the pairings table."""

    ins = pairings.insert().values(food_id1=search_term_id, 
                                   food_id2=other_term_id, 
                                   search_id=search_id, 
                                   occurences=count)
    db.execute(ins)

#####################################################################
# metric calculations and support fxns

def get_search_record(search_id):
    """Retrieve the search record associated with search_id."""
    searches = db.meta.tables["searches"]
    selection = select([searches]).where(searches.c.id == search_id)
    
    return db.execute(selection).fetchone()


def get_srch_term_popularity(num_matches_total):
    """Calculate the search term popularity."""
    # based on the past week
    return num_matches_total // 7


def get_pairing_popularities(pairings_dict, num_matches_returned):
    """
    Determine popularity of pairings with original search term.

    Takes a dictionary containing a pairing food term and the number of times 
    it occured in the search:
        {"food_term": occurences, ..., "food_term_n": occurences}

    Returns a dictionary of the same food term and its popularity score:
        {"food_term": popularity, ..., "food_term_n": popularity}
    """
    return {food_term: (occurences/num_matches_returned)*10 for \
                (food_term, occurences) in pairings_dict.items()}
