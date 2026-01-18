from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Length
from app import db

# I'm assuming we're gonna allow users to search up players or teams so this is the form that will allow them to do that.
# It's hard to imagine any other forms we'll need to create since our application mostly only displays data to users.
class SearchForm(FlaskForm):
    search = StringField('TBA', validators=[Length(min=0, max=140)]) # (THE FIRST STRING IS THE LABEL, ACCESSED WITH form.search.label)
    submit = SubmitField('Search')