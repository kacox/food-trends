"""Database functions for Food Trends application."""

# imports
from flask_sqlalchemy import SQLAlchemy

# make database instance
db = SQLAlchemy()


def connect_to_db(app):
    """Connect the database to Flask app."""

    # Configure to use 'food_trends' db
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///food_trends'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.app = app

    # actual connection
    db.init_app(app)


if __name__ == "__main__":
    """Run this module interactively to work with the database directly."""

    from food_trends import app

    # connect to db
    connect_to_db(app)
    print("Connected to DB interactively.")