"""Mock a Twingly API call."""

from twingly_search import Result, Post
import xml.etree.ElementTree as ET


def mock_api_call():
    """
    Make a fake Twingly API call: create and return a mock Result object for 
    the search term 'carrot'.
    """
    
    result_obj = Result()
    result_obj.number_of_matches_returned = 10
    result_obj.number_of_matches_total = 1160
    result_obj.seconds_elapsed = 0.0
    result_obj.incomplete_result = False
    result_obj.posts = make_posts()

    return result_obj


def make_posts():
    """Make mock post objects.

    Post objects need to have the post's url, title, indexedAt, and 
    publishedAt elements' text.
    """

    tree = ET.parse("sample_responses/sample_carrot_twingly_test.xml")
    root = tree.getroot()

    posts = []
    for child in root:
        current_post = Post()

        for sub_child in child:
            # each sub_child is an attribute of the post
            current_tag = sub_child.tag
            if current_tag == "url": 
                current_post.url = sub_child.text
            elif current_tag == "title":
                current_post.title = sub_child.text
            elif current_tag == "indexedAt":
                current_post.indexed_at = sub_child.text
            elif current_tag == "title":
                current_post.title = sub_child.text

        posts.append(current_post)
    
    return posts