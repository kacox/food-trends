"""
Food Trends app made with Flask.

This file creates and configures the Flask application instance and connects 
to the database.
"""

# imports
from flask import Flask, render_template

from db import connect_to_db


# create app instance
app = Flask(__name__)

#####################################################################
# routes & view functions
@app.route("/")
def index():
    return render_template("index.html")

#####################################################################

if __name__ == "__main__":
    """Run the server."""

    # connect to db
    connect_to_db(app)
    print("Connected to DB")

    # run application on localhost
    app.run(port=5000, host="0.0.0.0", debug=True)