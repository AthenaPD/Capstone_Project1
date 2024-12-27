from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, RadioField
from wtforms.validators import DataRequired, Email, Length


class ReviewForm(FlaskForm):
    """Form for adding/editing reviews."""

    rating = RadioField("Rating", choices=[('1', '1 star'), ('2', '2 stars'), ('3', '3 stars'),
                                          ('4', '4 stars'), ('5', '5 stars')], validators=[DataRequired()])
    comment = TextAreaField("Comment", validators=[DataRequired()])


class UserAddForm(FlaskForm):
    """Form for adding users."""

    first_name = StringField('First Name', validators=[Length(min=1, max=100)])
    last_name = StringField('Last Name', validators=[Length(min=1, max=100)])
    username = StringField('Username', validators=[Length(min=3, max=100)])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[Length(min=8)])


class LoginForm(FlaskForm):
    """User login form."""

    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[Length(min=8)])


class VetSearchForm(FlaskForm):
    """Form for searching vets in a particular zip code."""
    zipcode_or_city = StringField('Zip Code or City', validators=[DataRequired()])
