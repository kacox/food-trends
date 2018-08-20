"""API calls  and their helper fxns for Food Trends application."""

# imports
import os
import requests
import json

from sqlalchemy import Table, MetaData
from sqlalchemy.sql import select
from sqlalchemy.exc import IntegrityError
from twingly_search import Client

from connector import engine


# get api key from envionment variables
MASHAPE_KEY = os.environ.get("MASHAPE_KEY")
# TWINGLY_SEARCH_KEY pulled from environment variables by library

# build request to Spoonacular POST Detect Food in Text endpoint
endpoint_url = "https://spoonacular-recipe-food-nutrition-v1.p.mashape.com/food/detect"
payload = {"text": "Carrot cake is so good! So is chai."}
headers = {
    "X-Mashape-Key": MASHAPE_KEY,
    "Content-Type": "application/x-www-form-urlencoded",
    "Accept": "application/json"}


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


#### I DO NOT HAVE ACCESS TO THIS API RIGHT NOW; USE MOCK FOR DEV
def find_matches(food_term="carrot"):
    """
    Make call to Twingly Blog Search API. Search blog post TITLES using the 
    food term from get_food_term().

    Need to build a query (see below functions).

    Return results (list of Post objects); limited to 3 Posts within the 
    past week while developing.
    """

    # # build query string
    # search_window = get_search_window()
    # q = build_twingly_query(food_term, search_window)

    # # make the actual query
    # client = Client()
    # results = client.execute_query(q)

    # FAKE API CALL UNTIL I HAVE ACCESS AGAIN
    import mock_twingly
    results = mock_twingly.mock_api_call()

    # add relevant information to dbs related to call
    term_id = food_terms_record(food_term)
    search_id = make_searches_record(results.number_of_matches_total, term_id)
    process_blog_results(results, search_id, food_term)

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
    # hard-coded for now
    search_window = "w"

    # return piece to be used in final query
    return "tspan:" + search_window


def build_twingly_query(food_term, search_window):
    """Build query string for Twingly Blog Search API."""
    
    return (food_term + " fields:title lang:en page-size:3 sort:created " + 
            search_window)


# PARTIALLY TESTED ABOVE LINE
#####################################################################
def food_terms_record(food_term):
    """Add a food term to the food_terms table if not there.

    This function should run when new searches are made.

    Return the id of the inserted term.
    """

    # make connection (object)
    conn = engine.connect()

    # reflect db object
    metadata = MetaData()
    food_terms = Table('food_terms', metadata, 
                        autoload=True, autoload_with=engine)

    # make insert statement (object)
    # format is 'INSERT INTO food_terms (id, term) VALUES (:id, :term)'
    ins = food_terms.insert().values(term=food_term.lower())

    # insert if not in db; then get food term's id
    try:
        # execute insert statement
        result = conn.execute(ins)
        # result is ResultProxy object (analogous to the DBAPI cursor object)
        term_id = result.inserted_primary_key[0]
    except IntegrityError:
        # sqlalchemy wraps psycopg2.IntegrityError with its own exception
        # find the existing term's id
        print("This food term is already in the table.")
        term_id = get_term_id(food_term=food_term.lower(), 
                              table_obj=food_terms,
                              connection_obj=conn)

    # return the id of the inserted term
    return term_id


def get_term_id(food_term, table_obj, connection_obj):
    """Get and return the id of a given food term in the db."""

    # create selection statement
    selection = select([table_obj]).where(table_obj.c.term == food_term)

    # execute selection statement
    result = connection_obj.execute(selection)

    # return the id
    return result.fetchone()[0]


def make_searches_record(num_matches_total, term_id):
    """Add a record to the searches table.

    Fields to include: user_timestamp, search_window, food_id, 
                       num_matches_total
    """
    ### establish DB connection

    # make connection (object)
    conn = engine.connect()

    # reflect db object
    metadata = MetaData()
    searches = Table('searches', metadata, 
                        autoload=True, autoload_with=engine)


    ### get all the information you need to make a new searches record
    # grab time stamp (UTC)
    ts = get_time_stamp()

    # get search window (hard-coded for now)
    search_window = "tspan:w"

    ### make searches record and commit to db
    # create insert statement (obj)
    ins = searches.insert().values(user_timestamp=ts, 
                                   search_window=search_window, 
                                   food_id=term_id, 
                                   num_matches_total=num_matches_total)

    # execute insert statement
    result = conn.execute(ins)

    # return the search's id
    return result.inserted_primary_key[0]


def get_time_stamp():
    """Get UTC timestamp."""
    from datetime import datetime
    return datetime.utcnow()


def process_blog_results(results, search_id, search_term):
    """Get desired data from blog search results.

    for every result:
        get the title of that blog post
        make a record in the results table
        extract food terms from title text (get_food_terms)
        build pairs
        add records to pairings table for each pair

    search_id defaults to 0 (for testing) if not given.
    """
    # init dict for other food terms (not the search term)
    other_terms_dict = {}

    # process results post by post
    for post in results.posts:
        # make a record in the results table
        ##make_results_record(post, search_id)

        # get the title of that blog post
        post_title = post.title

        # extract food terms from title text
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



def make_results_record(post, search_id):
    """Add a record to the results table.

    Fields to include: publish_date, index_date, url, search_id
    """
    # extract data from post
    publish_date, index_date, post_url = dissect_post(post)

    # make and execute insert statement

    # make connection (object)
    conn = engine.connect()

    # reflect db object
    metadata = MetaData()
    results = Table('results', metadata, 
                        autoload=True, autoload_with=engine)

    # check if post_url is already in the db

    selection = select([results]).where(results.c.url == post_url)
    selection_result = conn.execute(selection)

    # prevent redundant URLs in table
    if not selection_result:
        # new url not already in results; add record to results

        # create insert statement (obj)
        ins = results.insert().values(publish_date=publish_date, 
                                       index_date=index_date, 
                                       url=post_url, 
                                       search_id=search_id)

        # execute insert statement
        conn.execute(ins)


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

    # make connection (object)
    conn = engine.connect()

    # reflect db objects
    metadata_pairings = MetaData()
    pairings = Table('pairings', metadata_pairings, 
                        autoload=True, autoload_with=engine)

    metadata_food_terms = MetaData()
    food_terms = Table('food_terms', metadata_food_terms, 
                        autoload=True, autoload_with=engine)

    # get id of search term
    search_term_id = get_term_id(search_term, food_terms, conn)

    for other_term, count in other_terms_dict.items():
        ### make a record in the pairings table

        # get the id for the food term from food_terms (add if not there)
        other_term_id = food_terms_record(other_term)

        # put pairings record in db
        make_pairings_record(conn, pairings, search_term_id, other_term_id, 
                                                    search_id, count)


def make_pairings_record(connection_obj, pairings, search_term_id, 
                                    other_term_id, search_id, count):
    """Add a record to the pairings table."""

    # create insert statement (obj)
    ins = pairings.insert().values(food_id1=search_term_id, 
                                   food_id2=other_term_id, 
                                   search_id=search_id, 
                                   occurences=count)

    # execute insert statement
    connection_obj.execute(ins)


#####################################################################
if __name__ == "__main__":
    """
    If run with 'make_request' and a filepath as addn'l CL arguments, then 
    make a call to the API
    """
    import sys

    if (len(sys.argv) > 1) and (sys.argv[1] == "make_request"):
        # check that a filepath is given before making a request
        try:
            # check for filepath
            new_file = sys.argv[2]
        except IndexError as e:
            # no filepath given
            print("Give a file name for the response contents to live.")
        else:
            # filepath given; check for API key before making request
            if MASHAPE_KEY:
                # make request
                r = requests.post(endpoint_url, data=payload, headers=headers)

                # write to file
                with open(new_file, "w") as f:
                    f.write(r.text)
            else:
                # API key missing
                print("Need API key in envionment variables.")