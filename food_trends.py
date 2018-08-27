"""
Food Trends app made with Flask.

This file creates and configures the Flask application instance and connects 
to the database.
"""

import os
import json

from flask import Flask, render_template, redirect, request, url_for, flash
from flask import jsonify

import calls
import forms


APP_KEY = os.environ.get("APP_KEY")
app = Flask(__name__)
app.config['SECRET_KEY'] = APP_KEY

#####################################################################
@app.route("/", methods=["GET", "POST"])
def index():
    """Display landing page with search form."""

    form = forms.QueryForm(request.form)

    if form.validate_on_submit():
        query = form.user_query.data
        return redirect(url_for("get_final_term", srch_query=query))
        
    if form.errors:
        for error in form.errors["user_query"]:
            flash(error)

    return render_template("index.html", form=form)


@app.route("/verify-term", methods=["GET", "POST"])
def get_final_term():
    """Get the final search term from the user query."""

    query = request.args.get("srch_query")

    # make request to Spoonacular (find food terms in user query)
    parsed_terms = calls.get_food_terms(query, calls.MASHAPE_KEY)

    # want user to pick the final search term
    if len(parsed_terms) > 1:
        return render_template("term_chooser.html", 
                                header_text=query, 
                                results=parsed_terms)
    else:
        return redirect(url_for("search_blogs", choice=parsed_terms[0]))


@app.route("/search", methods=["GET", "POST"])
def search_blogs():
    """Do blog search with final search term."""

    if request.method == "GET":
        final_term = request.args.get("choice")
    else:
        final_term = request.form.get("choice")

    # `final_term` hard-coded to "carrot" right now; change later
    results_dict = jsonify(calls.find_matches()).data

    return redirect(url_for("display_results", 
                                srch_results=results_dict, 
                                srch_term="carrot"))


@app.route("/results", methods=["GET"])
def display_results():
    """Show the search results and calculated metrics."""

    srch_term = request.args.get("srch_term")
    results = json.loads(request.args.get("srch_results"))
    
    # calculate search term popularity
    # for each pairing, calculate pairing popularity

    return render_template("results.html", 
                            header_text=srch_term, 
                            results=list(results.keys()))


#####################################################################

if __name__ == "__main__":
    """Run the server."""
    app.run(port=5000, host="0.0.0.0", debug=True)