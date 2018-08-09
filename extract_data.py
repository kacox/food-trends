"""
Functions to extract data from API responses.

    # open sample response (JSON) and convert to Python dictionary
    # get 'annotations' key's value (a list of dictionaries where each dict is 
            a food term result)
    # pull out each food term
    # if more than one, ask user to pick one to use for the next call
"""

# imports
import json


def extract_df_response():
    """Extract food terms from Spoonacular POST Detect Food in Text endpoint."""
    
    # turn response into Python obj
    response_content = load_json("sample_response.txt")

    # get food terms from response
    terms = extract_terms(response_content)
    
    # select final term
    # will eventually ask the user which one to choose, but in the meantime 
    # just take the first one
    if len(terms) > 1:
        final_term = terms[0]

    return final_term


def load_json(filename):
    """Load JSON response from file and make a Python obj."""
    with open(filename, "r") as f:
        json_content = json.load(f)
    return json_content


def extract_terms(response_content):
    """Extract food terms from Spoonacular POST Detect Food in Text response."""
    terms = []
    for term in response_content["annotations"]:
        terms.append(term["annotation"])
    return terms