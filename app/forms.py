import re
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, RadioField, validators,  IntegerField, SubmitField, TextAreaField, PasswordField, SelectField
from wtforms.fields import EmailField
from wtforms.validators import Length, EqualTo, Email, DataRequired,  Regexp
from wtforms.validators import Length, EqualTo, Email, DataRequired,  Regexp, NumberRange

# user registration form

class RegisterForm(FlaskForm):
    # all the fields in the form
    # regex for password validation
    exp = r"^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&+])[A-Za-z\d@$!%*#?&+]{4,}$"
    username = StringField(label='User Name:', validators=[
                           Length(min=2, max=30), DataRequired()])
    email_address = StringField(label='Email Address:', validators=[
                                Email(), DataRequired()])
    password1 = PasswordField(label='Password:', validators=[
                              Regexp(re.compile(exp),
                                     message='Password must contain at least one letter, one number and one special character'),
                              Length(min=4,  message='Password must have a minimum length of 4'), DataRequired()])
    password2 = PasswordField(label='Confirm Password:', validators=[
                              EqualTo('password1', message="Passwords do not match."), DataRequired()])
    submit = SubmitField(label='Create Account')

# user login form

class LoginForm(FlaskForm):
    username = StringField(label='Enter your username here',
                           validators=[DataRequired()])
    password = PasswordField(
        label='Enter Your Password:', validators=[DataRequired()])
    register=SubmitField(label='Register')
    submit = SubmitField(label='Sign in')

# Car Info Form

class CarForm(FlaskForm):
    options = [('', 'Maintained Car'), ('', 'Unmaintained Car')]
    type = SelectField('Dropdown', choices=options)
    mileage = IntegerField('mileage', validators=[validators.InputRequired("Number 1 is required")])
    average = IntegerField('average', validators=[validators.InputRequired("Number 2 is required")])
    submit = SubmitField('Submit')

    def validate_number2(form, field):
        if form.number1.data and not field.data:
            raise validators.ValidationError("Number 2 is required")