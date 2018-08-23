"""
Mock a Spoonacular API call.

Should mock the behavior of get_food_terms(input_text, api_key) in calls.py
so that the "/search-results" route can simply swap this with its 
get_food_terms call.

Should give this format to calls.terms_from_response:
    {"annotations":[
        {"annotation":"carrot cake","tag":"dish",
            "image":"https://spoonacular.com/menuItemImages/carrot-cake.jpg"},
        {"annotation":"carrot","tag":"ingredient",
            "image":"https://spoonacular.com/cdn/ingredients_100x100/carrots.jpg"},
        {"annotation":"chai","tag":"dish",
            "image":"https://spoonacular.com/cdn/ingredients_100x100/tea-bags.jpg"},
        {"annotation":"cake","tag":"dish",
            "image":"https://spoonacular.com/menuItemImages/plastic-to-go-drink-cup.jpg"}
        ],
     "processedInMs":6}


Sample responses and file location:
    'classic peanut butter pie' > sample_responses/spoonacular_pbpie.txt
    'chocolate chip cookies' > sample_responses/spoonacular_cccookies.txt
    'lavender scones' > sample_responses/spoonacular_lav_scones.txt
    'classic carrot cake' > sample_responses/spoonacular_ccarrotcake.txt
"""

import json


def get_response_text(user_query):
    """Get the payload of the response as text."""
    # get the filepath associated with the user query
    filepath = "sample_responses/spoonacular_ccarrotcake.txt"

    # open and read in as string
    with open(filepath, "r") as f:
        file_text = f.read()

    # return the string
    return file_text


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


def mock_get_food_terms(user_query):
    """
    Mock getting food terms from input text using Spoonacular API.

    Return list of food terms (dupes removed).
    """
    # open and extract data from file
    response_text = get_response_text(user_query)
        
    # extract food terms from response
    response_content = json.loads(response_text)
    return terms_from_response(response_content)