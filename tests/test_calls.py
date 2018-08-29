"""Unit tests for fxns in calls.py"""

import sys
import unittest

# import from parent directory
sys.path.append("/home/vagrant/src/food_trends_app/")
import calls
import mock_twingly as twingly


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

        assert 'banana cake' in calls.terms_from_response(response_content)
        assert 'banana' in calls.terms_from_response(response_content)
        assert 'cake' in calls.terms_from_response(response_content)


class TestQueryStructure(unittest.TestCase):
    """
    Test the structure of a generated Twingly Structure.
    """

    def test_build_twingly_query(self):
        """Should return a properly formatted query string."""
        assert (calls.build_twingly_query("banana", "tspan:w") == 
                "banana fields:title lang:en page-size:20 sort:created tspan:w")


class TestTwinglyResponse(unittest.TestCase):
    """
    Test handling of Twingly Blog Search API response.
    """

    def setUp(self):
        """Mock Twingly Blog Search API."""
        results = twingly.mock_api_call()

    def test_process_blog_results(self):
        """Should return food terms and their occurences."""
        #assert "pepitas" in process_blog_results(results, search_id=0, search_term="carrot").keys()
        pass

    def test_dissect_post(self):
        """Should get the publish_date, index_date, and post_url from post."""
        pass


#####################################################################

if __name__ == '__main__':
    """Do unittest tests if run directly."""
    unittest.main()