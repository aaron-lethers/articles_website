from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from wtforms.widgets import TextArea

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

# ARTICLE FORM CLASS
class ArticleForm(Form):
    title = StringField('Title', [validators.input_required(), validators.Length(min=1, max=200)])
    body = TextAreaField('Body', [validators.input_required(), validators.Length(min=30)])

# EDIT ARTICLE FORM CLASS
class EditForm(Form):
    title = StringField('Title', [validators.input_required(), validators.Length(min=1, max=200)])
    body = TextAreaField('Body', [validators.input_required(), validators.Length(min=30)], render_kw={"rows": 10, "cols": 11})