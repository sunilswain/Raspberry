from flask_login import current_user
from flask_wtf import FlaskForm
from flask_wtf.file import FileField , FileAllowed
from wtforms import StringField, PasswordField , SubmitField, BooleanField , TextAreaField
from wtforms.validators import DataRequired , Length , Email , EqualTo, ValidationError
from flaskblog.models import User

class ResistrationForm(FlaskForm):
    username = StringField('Username' ,validators =[ DataRequired() ,Length(min = 2 , max = 20)] )
    email = StringField('Email' ,validators =[ DataRequired() ,Email()] )
    password = PasswordField('Password' , validators = [ DataRequired() ])
    confirm_password = PasswordField('Confirm password' , validators = [ DataRequired() , EqualTo("password")])

    submit = SubmitField('Sign up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()

        validation_message = 'The username you have entered is already been taken , Please choose a different one.'
        if user:
            raise ValidationError(validation_message)
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()

        validation_message = 'the email you have entered is already been taken , Please choose a different one.'
        if user:
            raise ValidationError(validation_message)


class LogInForm(FlaskForm):
    
    email = StringField('email' ,validators =[ DataRequired() ,Email()] )
    password = PasswordField('password ', validators = [ DataRequired() ])
    remember = BooleanField('Remember me')

    submit = SubmitField('sign up')
    login = SubmitField('Log in')


class UpdateAccountForm(FlaskForm):
    username = StringField('Username' ,validators =[ DataRequired() ,Length(min = 2 , max = 20)] )
    email = StringField('Email' ,validators =[ DataRequired() ,Email()] )
    profile_picture = FileField('Profile picture', validators = [FileAllowed(['jpg','jpeg', 'png', 'gif'])])
    submit = SubmitField('Save')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            validation_message = 'the username you have entered is already been taken , Please choose a different one.'
            if user:
                raise ValidationError(validation_message)
    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            validation_message = 'the email you have entered is already been taken , Please choose a different one.'
            if user:
                raise ValidationError(validation_message)

class RequestResetForm(FlaskForm):
    email = StringField('Email' ,validators =[ DataRequired() ,Email()] )
    submit = SubmitField('Request Request Password')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        validation_message = 'The Email you have entered is not valid or there is not any account asssigned with this email yet.'
        if user is None:
            raise ValidationError(validation_message)

class ResetPasswordForm(FlaskForm):
    password = PasswordField('New password' , validators = [ DataRequired() ])
    confirm_password = PasswordField('Confirm new password' , validators = [ DataRequired() , EqualTo("password")])
    submit = SubmitField('Submit')