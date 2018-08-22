"""
Food Trends app made with Flask.

This file creates and configures the Flask application instance and connects 
to the database.
"""

# imports
from flask import Flask, render_template, redirect, request, url_for, flash

import forms
import os

from db import connect_to_db
import calls


# get secret key
APP_KEY = os.environ.get("APP_KEY")

# create app instance
app = Flask(__name__)

# session enabling and CSRF protection
app.config['SECRET_KEY'] = APP_KEY


#####################################################################
# routes & view functions
@app.route("/", methods=["GET", "POST"])
def index():
    form = forms.QueryForm(request.form)

    if form.validate_on_submit():
        # Successful POST request; take data
        query = form.user_query.data

        # give results to backend function (for now, display placeholder)
        # second arg for url_for is sent as GET request
        return redirect(url_for("display_search", srch_query=query))
        

    # Form not submitted; no data; back to original page
    if form.errors:
        # if there are any validation errors
        for error in form.errors["user_query"]:
            flash(error)

    return render_template("index.html", form=form)


@app.route("/search-results", methods=["GET", "POST"])
def display_search():
    # get the user's query string
    query = request.args['srch_query']

    # make request to Spoonacular (find food terms in user query)
    parsed_terms = calls.get_food_terms(query, calls.MASHAPE_KEY)

    # results
    return render_template("results.html", 
                            header_text=query, 
                            results=parsed_terms)


#####################################################################

if __name__ == "__main__":
    """Run the server."""

    # connect to db
    connect_to_db(app)
    print("Connected to DB")

    # run application on localhost
    app.run(port=5000, host="0.0.0.0", debug=True)