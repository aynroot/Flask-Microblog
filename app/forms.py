from flask.ext.wtf import Form
from wtforms import StringField, BooleanField, PasswordField
from wtforms.validators import Email, DataRequired, EqualTo


class LoginForm(Form):
    email = StringField('email', validators=[Email()])
    password = PasswordField('password', validators=[DataRequired()])
    remember_me = BooleanField('remember_me', default=False)


class SignUpForm(Form):
    email = StringField('email', validators=[Email()])
    nickname = StringField('nickname', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])
    verify_password = PasswordField('verify_password', validators=[EqualTo('password')])
