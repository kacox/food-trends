"""
Food Trends app made with Flask.

This file creates and configures the Flask application instance and connects 
to the database.
"""

import os
import json

from flask import Flask, render_template, redirect, request, url_for, flash
from flask import jsonify, session

import calls
import forms
import metric_calcs as calcs
import formatting


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
    parsed_terms = calls.get_food_terms(query, calls.MASHAPE_KEY)

    # want user to pick the final search term
    if len(parsed_terms) > 1:
        return render_template("term_chooser.html", 
                                header_text=query, 
                                results=parsed_terms)
    elif len(parsed_terms) < 1:
        flash("Please enter a food or ingredient.")
        return redirect(url_for("index"))
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
    calls.find_store_matches(final_term)

    return redirect(url_for("display_results"))


@app.route("/results", methods=["GET"])
def display_results():
    """Show the search results and calculated metrics."""
    search_id = session["search_id"]

    search_record = calls.get_search_record(search_id)
    timestamp, srch_term_id = search_record[1], search_record[3]
    num_matches_total, num_matches_returned = search_record[4], search_record[5]

    srch_term = calls.get_search_term(srch_term_id)
    srch_term_pop = calcs.get_srch_term_popularity(num_matches_total)

    pairings_dict = calls.get_pairings(search_id)
    pairings = calcs.get_pairing_popularities(pairings_dict, 
                                                num_matches_returned)

    # AJAX call in viz.js will get this from the session
    session["pairings"] = pairings
    
    return render_template("results.html", 
                            header_text=srch_term.capitalize(), 
                            timestamp=timestamp.strftime("%m-%d-%y"),
                            results=pairings,
                            term_popularity=srch_term_pop)


@app.route("/data.json")
def get_graph_data():
    """Get the pairings data from the session."""
    pairings = session["pairings"]
    dataset = formatting.format_pairings(pairings)
    session.clear()
    return jsonify(dataset)


@app.route("/recent-searches")
def get_recent():
    """Display recent search summaries."""
    summaries = calls.search_summaries()
    return render_template("recent_searches.html", summaries=summaries)


@app.route("/recent-searches/<past_search_id>")
def past_result(past_search_id):
    """Display a past search's results."""

    search_record = calls.get_search_record(past_search_id)
    timestamp, srch_term_id = search_record[1], search_record[3]
    num_matches_total, num_matches_returned = search_record[4], search_record[5]

    srch_term = calls.get_search_term(srch_term_id)
    srch_term_pop = calcs.get_srch_term_popularity(num_matches_total)

    pairings_dict = calls.get_pairings(past_search_id)
    pairings = calcs.get_pairing_popularities(pairings_dict, 
                                                num_matches_returned)

    session["pairings"] = pairings

    return render_template("results.html", 
                            header_text=srch_term.capitalize(), 
                            timestamp=timestamp.strftime("%m-%d-%y"),
                            results=pairings,
                            term_popularity=srch_term_pop)

#####################################################################

if __name__ == "__main__":
    """Run the server."""
    app.run(port=5000, host="0.0.0.0", debug=True)