"""API calls  and their helper fxns for Food Trends application."""

import os
import requests
import json

from twingly_search import Client
from flask import session

from connector import DBConnector
import mock_spoonacular
import mock_twingly
import metric_calcs as calcs


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
    # real API call
    q = build_twingly_query(food_term, "tspan:w")
    client = Client()
    results = client.execute_query(q)

    # # FAKE API CALL
    # results = mock_twingly.mock_api_call()

    term_id = db.new_food_term_record(food_term)
    search_id = db.new_search_record(term_id, 
                                        results.number_of_matches_total, 
                                        results.number_of_matches_returned)
    process_blog_results(results, search_id, food_term)

    # want to access search id in several routes
    session["search_id"] = search_id


def build_twingly_query(food_term, search_window):
    """Build query string for Twingly Blog Search API."""
    return (food_term + " fields:title lang:en page-size:20 sort:created " + 
            search_window)


def process_blog_results(results, search_id, search_term):
    """Put desired data from blog search results into database."""

    # want to keep the search term separate from other food terms
    other_terms_dict = {}

    for post in results.posts:
        db.new_results_record(post, search_id)
        post_title = post.title

        other_terms = get_food_terms(post_title, MASHAPE_KEY)

        # clean so that search term is not in other_terms
        if search_term in other_terms:
            other_terms.remove(search_term)

        for term in other_terms:
            if search_term in term:
                other_terms.remove(term)
            elif term in other_terms_dict.keys():
                other_terms_dict[term] += 1
            else:
                other_terms_dict[term] = 1

    if other_terms_dict != {}:
        build_pairs(search_term, search_id, other_terms_dict)


def build_pairs(search_term, search_id, other_terms_dict):
    """Create pairings and put each in database."""
    search_term_id = db.id_by_term(search_term)

    for other_term, count in other_terms_dict.items():
        other_term_id = db.new_food_term_record(other_term)
        db.new_pairings_record(search_term_id, other_term_id, 
                                                    search_id, count)


def get_search_record(search_id):
    """Retrieve the search record associated with search_id."""
    return db.search_record_by_id(search_id)


def get_search_term(term_id):
    """Retrieve the search term from its id."""
    return db.term_by_id(term_id)


def get_pairings(search_id):
    """Retrieve all pairings associated with a given search id.

    Return a dictionary containing a pairing food term and the number of times 
    it occured in the search:
        {"food_term": occurences, ..., "food_term_n": occurences}
    """
    pairings = db.pairings_by_search(search_id)

    pairings_dict = {}
    for pairing in pairings:
        pairing_term = db.term_by_id(pairing[2])
        occurences = pairing[4]
        pairings_dict[pairing_term] = occurences

    return pairings_dict


def gather_results(search_id):
    """Gather information for displaying search results."""
    search_record = get_search_record(search_id)
    timestamp, srch_term_id = search_record[1], search_record[3]
    num_matches_total, num_matches_returned = search_record[4], search_record[5]

    srch_term = get_search_term(srch_term_id)
    srch_term_pop = calcs.get_srch_term_popularity(num_matches_total)

    pairings_dict = get_pairings(search_id)
    pairings = calcs.get_pairing_popularities(pairings_dict, 
                                                num_matches_returned)

    return srch_term, timestamp, pairings, srch_term_pop


def search_summaries():
    """Get a list containing recent search summaries."""
    records = db.recent_n_searches(10)
    # # FOR DEMO HARD CODED
    # records = []
    # records.append(db.recent_n_searches(1)[0])
    # for desired_search_id in [109, 110, 129, 140, 128, 
    #                             132, 138, 130, 100]:
    #     records.append(db.demo_search_record_by_id(desired_search_id))
    return build_summary_info(records)


def build_summary_info(records):
    """Build a list containing search record summaries.
    
    Return a list as follows:
        [(foodterm1, search_id, searchdate, [previews]), 
                (foodterm2, search_id, searchdate, [previews]),
                ... ]
    """
    summaries = []
    for record in records:
        previews = get_previews(record[0])
        summaries.append((db.term_by_id(record[2]), 
                                        record[0], 
                                        record[1].strftime("%m-%d-%y"), 
                                        previews))
    return summaries


def get_previews(search_id):
    """Get the first 3 pairing foods associated with food_id."""
    records = db.pairings_by_search(search_id)
    all_pairing_terms = [db.term_by_id(record[2]) for record in records]

    if len(all_pairing_terms) >= 3:
        return all_pairing_terms[:3]
    else:
        return all_pairing_terms[:len(all_pairing_terms)]
