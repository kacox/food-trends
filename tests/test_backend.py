"""Tests for fxns in `calls.py`."""

# imports
import sys
import pytest
import unittest

# import from parent directory
sys.path.append("/home/vagrant/src/food_trends_app/")
import calls


class TestFirstApiCall(unittest.TestCase):
    """
    Test first interaction with Spoonacular's POST Detect Food in Text 
    endpoint.
    """

    def setUp(self):
        """Mock API call before each test."""

        # Make mock
        def _mock_get_food_terms(input_text, api_key):
            return {'annotations': 
                        [{'annotation': 'banana cake', 'tag': 'dish', 
                            'image': 'https://spoonacular.com/menuItemImages/plastic-to-go-drink-cup.jpg'}, 
                        {'annotation': 'banana', 'tag': 'ingredient', 
                            'image': 'https://spoonacular.com/cdn/ingredients_100x100/bananas.jpg'}, 
                        {'annotation': 'cake', 'tag': 'dish', 
                            'image': 'https://spoonacular.com/menuItemImages/plastic-to-go-drink-cup.jpg'}], 
                    'processedInMs': 9}

        # Monkey patching
        calls.get_food_terms = _mock_get_food_terms

    def test_terms_from_response(self):
        """Should extract food terms from JSON response."""
        # mock API call
        input_text = "banana cake is good"
        api_key = calls.MASHAPE_KEY
        response_content = calls.get_food_terms(input_text, api_key)

        # tests
        assert 'banana cake' in calls.terms_from_response(response_content)
        assert 'banana' in calls.terms_from_response(response_content)
        assert 'cake' in calls.terms_from_response(response_content)


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


"""
Do not run unless you specifically want to; makes an actual API call 
and tests that I handle the response correctly.
"""
@pytest.mark.skip(reason="Limited number of API calls allowed.")
def test_get_food_terms():
    """Should get food terms from input text."""
    input1 = "Low - Carb Banana Pancakes"
    assert "banana" in calls.get_food_terms(input1, calls.MASHAPE_KEY)
    assert "pancakes" in calls.get_food_terms(input1, calls.MASHAPE_KEY)


if __name__ == '__main__':
    """Do unittest tests if run directly."""
    unittest.main()