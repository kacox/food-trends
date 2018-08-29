"""Integration tests for routes in food_trends.py"""

import sys
import unittest

# import from parent directory
sys.path.append("/home/vagrant/src/food_trends_app/")
import food_trends


class TestLandingPage(unittest.TestCase):
    """Test the landing page."""

    def setUp(self):
        """Get the main page."""
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


#####################################################################

if __name__ == '__main__':
    unittest.main()