"""Tests for fxns in `calls.py`."""

# imports
import sys
import pytest

# import from parent directory
sys.path.append("/home/vagrant/src/food_trends_app/")
import calls


# skip unless you specifically want to run
@pytest.mark.skip(reason="Limited number of API calls allowed.")
def test_get_food_terms():
    """Should get food terms from input text."""
    input1 = "Low - Carb Banana Pancakes"
    assert "banana" in calls.get_food_terms(input1, calls.MASHAPE_KEY)
    assert "pancakes" in calls.get_food_terms(input1, calls.MASHAPE_KEY)


def test_get_search_window():
    """Should return the string `tspan:w`.

    For now, it will always be `tspan:w`, however in the future different 
    suffixes possible.
    """
    assert calls.get_search_window() == "tspan:w"


def test_build_twingly_query():
    """Should return a properly formatted query string."""
    assert (calls.build_twingly_query("banana", "tspan:w") == 
            "banana fields:title lang:en page-size:3 sort:created tspan:w")


def test_terms_from_response():
    """Should extract food terms from JSON response."""
    # example of what response contains as a Python object
    test_response_content = {'annotations': 
                                [{'annotation': 'banana cake', 'tag': 'dish', 
                                'image': 'https://spoonacular.com/menuItemImages/plastic-to-go-drink-cup.jpg'}, 
                                {'annotation': 'banana', 'tag': 'ingredient', 
                                'image': 'https://spoonacular.com/cdn/ingredients_100x100/bananas.jpg'}, 
                                {'annotation': 'cake', 'tag': 'dish', 
                                'image': 'https://spoonacular.com/menuItemImages/plastic-to-go-drink-cup.jpg'}], 
                             'processedInMs': 9}
    # no guaranteed order, so "assert ___ in" necessary
    assert 'banana cake' in calls.terms_from_response(test_response_content)
    assert 'banana' in calls.terms_from_response(test_response_content)
    assert 'cake' in calls.terms_from_response(test_response_content)