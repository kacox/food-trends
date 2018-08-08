"""API calls for Food Trends application."""

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



if __name__ == "__main__":
    """
    If run with 'make_request' and a filepath as addn'l CL arguments, then 
    make a call to the API
    """
    import sys

    if sys.argv[1] == "make_request":
        # make request then write response to file
        try:
            # check if file name argument given
            new_file = sys.argv[2]
        except IndexError as e:
            # no file name given
            print("Give a file name for the response contents to live.")
        else:
            # file name argument; make request
            if MASHAPE_KEY:
                r = requests.post(endpoint_url, data=payload, headers=headers)
            # write to file
            with open(new_file, "w") as f:
                f.write(r.text)