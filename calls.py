"""API calls  and their helper fxns for Food Trends application."""

# imports
import os
import requests

# get api key from envionment variables
MASHAPE_KEY = os.environ.get("MASHAPE_KEY")

# build request to Spoonacular POST Detect Food in Text endpoint
endpoint_url = "https://spoonacular-recipe-food-nutrition-v1.p.mashape.com/food/detect"
payload = {"text": "Carrot cake is so good! So is chai."}
headers = {
    "X-Mashape-Key": MASHAPE_KEY,
    "Content-Type": "application/x-www-form-urlencoded",
    "Accept": "application/json"}



def get_food_terms(input_text, api_key):
    """Get food terms from input text.

    Make call to Spoonacular (POST Detect Food in Text endpoint).
    Extract food terms from response (JSON).
    Return as a list (duplicates removed).
    """
    pass


def get_final_term(terms_list):
    """Choose final term to use for later queries and pair building."""
    pass


def find_matches(food_term):
    """
    Make call to Twingly Blog Search API. Search blog post TITLES using the 
    food term from get_food_term().

    Need to build a query (see below functions).

    Return blog post matches ("results"); you might want to limit the number of 
    results returned while building out this portion.
    """

    # search_window = get_search_window()
    # build_twingly_query(api_key, search_window)
    # make the actual query
    # return the results
    pass


def get_search_window():
    """
    Determine search window time period for next call to Twingly.

    Options: past week, past month, past 3 months.
    """
    pass


def build_twingly_query(api_key, search_window):
    pass

  
def make_searches_record():
    """Add a record to the searches table.

    Fields to include: user_timestamp, search_window_start, search_window_end, 
                        food_id, num_matches_total
    """
    pass


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