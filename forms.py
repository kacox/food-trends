"""Form definitions for WTForm form validation."""

from wtforms import Form, StringField, SubmitField, validators
from flask_wtf import FlaskForm


def validate_characters(form, field):
    """Custom validator: input only alphabetic characters or apostrophe.

    A validator in flask_wtf can be any callable that accepts two arguments 
    (form and field).
    """
    cleaned_query = field.data.strip().split()

    for word in cleaned_query:
        if not word.isalpha() or "'" in word:
            raise validators.ValidationError('Only letters and apostrophes allowed')


class QueryForm(FlaskForm):
    """Main form for collecting user's food term query."""
    user_query = StringField('Food or Ingredient:', [
                                validators.Length(min=2, max=35), 
                                validators.DataRequired(),
                                validate_characters])
    submit = SubmitField('Find pairings')
