"""
Food Trends app made with Flask.

This file creates and configures the Flask application instance and connects 
to the database.
"""

# imports
from flask import Flask, render_template, redirect, request, url_for

from db import connect_to_db
import forms
import os

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

        # give results to backend function
        # for now, display a fake result
        return redirect(url_for("display_search"))
        

    # Form not submitted; no data; back to original page
    return render_template("index.html", form=form)


@app.route("/search-results", methods=["GET", "POST"])
def display_search():
    return "<h1>!!</h1>"


#####################################################################

if __name__ == "__main__":
    """Run the server."""

    # connect to db
    connect_to_db(app)
    print("Connected to DB")

    # run application on localhost
    app.run(port=5000, host="0.0.0.0", debug=True)