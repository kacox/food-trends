"""Integration tests for routes in food_trends.py"""

import sys
import unittest

# import from parent directory
sys.path.append("/home/vagrant/src/food_trends_app/")
import food_trends


class TestLandingPage(unittest.TestCase):
    """Test the landing page."""

    def setUp(self):
        """Make an app instance."""
        food_trends.app.config["TESTING"] = True
        self.client = food_trends.app.test_client()

    def test_landing_page(self):
        """Landing page should be reached."""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

    def test_form_display(self):
        """Search form should be displayed."""
        response = self.client.get("/")
        self.assertIn(b"Food or Ingredient", response.data)

    def test_flash_display(self):
        """Flash message should appear."""
        response = self.client.post("/", data={"user_query": "b"})
        self.assertIn(b"between 2 and 35 characters", response.data)

    def test_flash_error(self):
        """Flash error message should appear."""
        response = self.client.post("/", data={"user_query": "carrot8"})
        self.assertIn(b"Only letters and apostrophes allowed", response.data)

    def test_validate_on_submit(self):
        """Should redirect to '/verify-term' route."""
        pass


class TestVerifyTerm(unittest.TestCase):
    """Test '/verify-term' route."""

    def setUp(self):
        """Make an app instance."""
        food_trends.app.config["TESTING"] = True
        self.client = food_trends.app.test_client()

    def test_single_term(self):
        """Should redirect to '/search' route."""
        pass

    def test_multi_term(self):
        """'term_chooser.html' should be displayed."""
        pass

    def test_something(self):
        """derp."""
        pass


#####################################################################

if __name__ == '__main__':
    unittest.main()