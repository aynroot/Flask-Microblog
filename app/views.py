from flask import render_template, flash, redirect
from flask.ext.httpauth import HTTPDigestAuth

from app import app
from .forms import LoginForm

auth = HTTPDigestAuth()

users = {
    "john": "hello",
    "susan": "bye"
}


@app.route('/')
@app.route('/index')
def index():
    user = {'nickname': 'Miguel'}  # fake user
    posts = [  # fake array of posts
        {
            'author': {'nickname': 'John'},
            'body': 'Beautiful day in Portland!'
        },
        {
            'author': {'nickname': 'Susan'},
            'body': 'The Avengers movie was so cool!'
        }
    ]
    return render_template("index.html",
                           title='Home',
                           user=user,   # auth.username,
                           posts=posts)


@auth.get_password
def _get_password(username):
    if username in users:
        return users.get(username)
    return None


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        flash('Login requested for OpenID="%s", remember_me=%s' %
              (form.openid.data, str(form.remember_me.data)))
        return redirect('/index')
    return render_template('login.html',
                           title='Sign In',
                           form=form)
