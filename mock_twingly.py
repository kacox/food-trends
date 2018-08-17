"""Mock a Twingly API call."""

from twingly_search import Result, Post
import xml.etree.ElementTree as ET


def mock_api_call():
    """A fake search.

    Hard-coded to mock the search for the term "carrot".

    Need to mock a Result object being returned; posts attribute is a list of 
    Post objects.
    """

    # fake Twingly API call
    return make_mock_result()


def make_mock_result():
    """Create and return a mock Result object for the search term 'carrot'."""
    # init object
    result_obj = Result()

    # set attributes
    result_obj.number_of_matches_returned = 10
    result_obj.number_of_matches_total = 1160
    result_obj.seconds_elapsed = 0.0
    result_obj.incomplete_result = False

    # make list of Post objects
    posts = make_posts()

    # set posts attribute
    result_obj.posts = posts

    # return mocked Result object
    return result_obj


def make_posts():
    """Make mock post objects.

    Post objects need to have the post's url, title, indexedAt, and 
    publishedAt elements' text.
    """

    # parse sample response (XML) content
    tree = ET.parse("sample_responses/sample_carrot_twingly_test.xml")
    root = tree.getroot()

    # init list
    posts = []

    # iter thru parse tree elements
    for child in root:
        # each child is a post element
        current_post = Post()

        for sub_child in child:
            # each sub_child is an attribute of the post

            if sub_child.tag == "url":
                current_tag = sub_child.tag
                current_post.url = sub_child.text
            elif sub_child.tag == "title":
                current_tag = sub_child.tag
                current_post.title = sub_child.text
            elif sub_child.tag == "indexedAt":
                current_tag = sub_child.tag
                current_post.indexed_at = sub_child.text
            elif sub_child.tag == "title":
                current_tag = sub_child.tag
                current_post.title = sub_child.text

        # add the filled in Post into the list
        posts.append(current_post)
    
    return posts