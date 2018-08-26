"""
Food Trends app made with Flask.

This file creates and configures the Flask application instance and connects 
to the database.
"""

# imports
from flask import Flask, render_template, redirect, request, url_for, flash
from flask import jsonify

import os

from db import connect_to_db
import calls
import forms


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


@app.route("/verify-term", methods=["GET", "POST"])
def display_search():
    # get the user's query string
    query = request.args.get("srch_query")

    # make request to Spoonacular (find food terms in user query)
    parsed_terms = calls.get_food_terms(query, calls.MASHAPE_KEY)

    # if more than one let user pick
    if len(parsed_terms) > 1:
        return render_template("term_chooser.html", 
                                header_text=query, 
                                results=parsed_terms)
    else:
        return redirect(url_for("search_blogs", choice=parsed_terms[0]))


@app.route("/search", methods=["GET", "POST"])
def search_blogs():
    # get final term depending on request type
    if request.method == "GET":
        final_term = request.args.get("choice")
    else:
        # query had more than one choice; narrowed to one now
        final_term = request.form.get("choice")

    # hard-coded to "carrot" right now; change to final_term later
    results_dict = jsonify(calls.find_matches())
    return results_dict


#####################################################################

if __name__ == "__main__":
    """Run the server."""
    # run application on localhost
    app.run(port=5000, host="0.0.0.0", debug=True)