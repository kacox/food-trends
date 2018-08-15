"""API calls  and their helper fxns for Food Trends application."""

# imports
import os
import requests
import json

from twingly_search import Client


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


def find_matches(food_term):
    """
    Make call to Twingly Blog Search API. Search blog post TITLES using the 
    food term from get_food_term().

    Need to build a query (see below functions).

    Return results (list of Post objects); limited to 3 Posts within the 
    past week while developing.
    """

    # build query string
    search_window = get_search_window()
    q = build_twingly_query(food_term, search_window)

    # make the actual query
    client = Client()
    results = client.execute_query(q)

    # add relevant information to dbs related to call
    term_id = food_terms_record(food_term)[0]
    make_searches_record(results.number_of_matches_total, term_id)

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
    return results


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
    from sqlalchemy import create_engine, Table, MetaData
    from sqlalchemy.exc import IntegrityError

    # create engine(core interface to db)
    engine = create_engine("postgresql:///food_trends", echo=False)

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
        term_id = result.inserted_primary_key
    except IntegrityError:
        # sqlalchemy wraps psycopg2.IntegrityError with its own exception
        # find the existing term's id
        print("This food term is already in the table.")
        term_id = get_term_id(food_term=food_term.lower(), 
                              table_obj=food_terms,
                              connection_obj=conn)

    # release referenced DBAPI connection to the connection pool
    conn.close()

    # return the id of the inserted term
    return term_id


def get_term_id(food_term, table_obj, connection_obj):
    """Get and return the id of a given food term in the db."""
    from sqlalchemy.sql import select

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
    from sqlalchemy import create_engine, Table, MetaData

    # create engine(core interface to db)
    engine = create_engine("postgresql:///food_trends", echo=False)

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
    conn.execute(ins)


def get_time_stamp():
    """Get UTC timestamp."""
    from datetime import datetime
    return datetime.utcnow()


#####################################################################
def dissect_results(results):
    """Get desired data from search results.

    for every result:
        make an record in the results table
        get the title of that blog post
        extract food terms from title text (get_food_terms)
        build pairs
        add records to pairings table for each pair
    """
    pass


def make_results_record():
    """Add a record to the results table.

    Fields to include: publish_date, index_date, url, search_id
    """
    pass


def extract_titles(search_results):
    """
    Parse titles out of each result in search results. Return titles as a 
    list?
    """
    pass


def build_pairs(original_term, food_terms):
    """Find all possible food term pair combinations.

    Return as a list of tuples?
    """
    pass


def make_pairings_record():
    """Add a record to the pairings table.

    Fields to include: food_id1, food_id2, search_id
    """
    pass


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