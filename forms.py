"""Form definitions for WTForm form validation."""

from wtforms import Form, StringField, SubmitField, validators
from flask_wtf import FlaskForm

class QueryForm(FlaskForm):
    """Main form for collecting user's food term query."""

    user_query = StringField('Food or Ingredient:', [
                                validators.Length(min=2, max=35), 
                                validators.DataRequired()])
    submit = SubmitField('Find pairings')