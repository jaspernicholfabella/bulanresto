from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,SubmitField,SelectField,FileField,IntegerField,TextAreaField
from wtforms.validators import DataRequired, ValidationError,Email, EqualTo,Required,InputRequired,Length,NumberRange
from wtforms.fields.html5 import EmailField
from wtforms_validators import AlphaNumeric,Alpha
from flask_wtf.file import FileField, FileRequired

from flask import Markup



class SignupForm(FlaskForm):
    user_name = StringField('User Name',render_kw={"placeholder": "Username"}, validators=[DataRequired(),
                                                     AlphaNumeric(message="Username must be AlphaNumeric Characters"),
                                                     Length(min=6,max=32,message="minimum 6 characters maximum of 32 characters only.")])
    email_address = EmailField('Email Address',render_kw={"placeholder": "Email Address"},validators=[DataRequired(),
                                                           Email(message="Please Enter an Email Address"),
                                                           Length(min=1,max=32,message="maximum of 32 characters only.")])
    home_address = StringField('Home Address',render_kw={"placeholder": "Home Address"}, validators=[DataRequired(),Length(min=1,max=64,message="maximum of 64 characters only.")])
    password = PasswordField('Password', render_kw={"placeholder": "Password"},validators=[InputRequired(),
                                                     Length(min=6,max=32,message="the password should be minimum of 6 character and maximum of 32 characters"),
                                                     EqualTo('repeat_password', message='Passwords must match')])
    repeat_password = PasswordField('Repeat Password',render_kw={"placeholder": "Repeat Password"}, validators=[InputRequired()])
    submit = SubmitField('SUBMIT')

class LoginForm(FlaskForm):
    user_name = StringField('Username',validators=[DataRequired()])
    password=PasswordField('Password',validators=[DataRequired()])

class RestaurantSignupForm(FlaskForm):
    restaurant_name = StringField('Restaurant Name', render_kw={"placeholder": "Restaurant Name"},validators=[DataRequired(),Length(min=6, max=32,message="name should be minimum of 6 maximum of 32 characters only.")])
    owner_name = StringField('Owner Name', render_kw={"placeholder": "Owner Name"},validators=[DataRequired(),Length(min=4, max=32,message="please type full name"),Alpha(message="Name must only contain Alphabet.")])
    address = StringField('Address', render_kw={"placeholder": "Address"},validators=[DataRequired(),Length(min=1, max=64,message="maximum of 64 characters only.")])
    email_address = EmailField('Email Address', render_kw={"placeholder": "Email Address"},validators=[DataRequired(),
                                Email(message="Please Enter an Email Address"),
                                Length(min=1, max=32,message="maximum of 32 characters only.")])
    file_field = FileField('Attach Business Permit',render_kw={"placeholder": "Attach Business Permit"},validators=[FileRequired(message="You need to attach a photo of your business permit")])
    submit=SubmitField('Submit Registration')

class SearchForm(FlaskForm):
    search_string= StringField('Search', validators=[DataRequired()])


class FeedbackForm(FlaskForm):
    rate = IntegerField('Rate',render_kw={"placeholder": "Rate from 1 - 5", "type" : "number"},validators=[NumberRange(1,5,message='You can only rate from 1 - 5')])
    message = TextAreaField('Message',render_kw={"placeholder":"Write a Comment..."},validators=[DataRequired()])
