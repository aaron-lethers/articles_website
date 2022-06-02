from wtforms import Form, StringField, TextAreaField, PasswordField, validators

# REGISTER FORM CLASS
class RegisterForm(Form):
    name = StringField('Name', [validators.input_required(), validators.Length(min=1, max=50)])
    email  = StringField('Email', [validators.input_required(), validators.Length(min=1, max=50)])
    username = StringField('Username', [validators.input_required(), validators.Length(min=1, max=100)])
    password = PasswordField('Password', [
    	validators.input_required(),
    	validators.EqualTo('confirm', message='Passwords do not match')
    ])
    confirm = PasswordField('Confirm Password')

# LOGIN FORM CLASS
class LoginForm(Form):
	email = StringField('Email', [validators.input_required(), validators.Length(min=1, max=50)])
	password = PasswordField('Password', [validators.input_required(), validators.Length(min=1, max=50)])