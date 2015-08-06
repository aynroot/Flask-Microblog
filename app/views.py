import flask
from flask import render_template
from flask.ext.login import login_user, logout_user, current_user, login_required
from passlib.hash import sha256_crypt

from app import app, db, login_manager
from .models import User
from .forms import LoginForm, SignUpForm


@app.before_request
def before_request():
    flask.g.user = current_user


@app.route('/')
@app.route('/index')
@login_required
def index():
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
    return render_template('index.html',
                           title='Home',
                           user=current_user,
                           posts=posts)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if flask.g.user is not None and flask.g.user.is_authenticated():
        flask.flash('Already authenticated.')
        return flask.redirect(flask.url_for('index'))

    form = SignUpForm()
    if form.validate_on_submit():
        user = User()
        user.nickname = form.nickname.data
        user.email = form.email.data
        user.password = sha256_crypt.encrypt(form.password.data)
        db.session.add(user)
        db.session.commit()
        flask.flash('Successfully signed up. Try to login.')
        return flask.redirect(flask.url_for('index'))
    return render_template('signup.html',
                           title='Sign Up',
                           form=form)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if flask.g.user is not None and flask.g.user.is_authenticated():
        flask.flash('Already authenticated.')
        return flask.redirect(flask.url_for('index'))

    form = LoginForm()
    if form.validate_on_submit():
        flask.session['remember_me'] = form.remember_me.data
        user = User.query.filter_by(email=form.email.data).first()

        if not user:
            flask.flash('No such email in database')
            return render_template('login.html',
                                   title='Sign In',
                                   form=form)
        if sha256_crypt.verify(form.password.data, user.password):
            login_user(user, remember=form.remember_me.data)
            flask.flash('Logged in successfully.')
            return flask.redirect(flask.url_for('index'))
        else:
            flask.flash('Wrong password')
            return render_template('login.html',
                                   title='Sign In',
                                   form=form)
    return render_template('login.html',
                           title='Sign In',
                           form=form)


@app.route('/logout', methods=["GET"])
@login_required
def logout():
    logout_user()
    flask.flash('Successfully logged out')
    return flask.redirect(flask.url_for('index'))


@app.route('/user/<nickname>')
@login_required
def user(nickname):
    user = User.query.filter_by(nickname=nickname).first()
    if user is None:
        flask.flash('User %s not found.' % nickname)
        return flask.redirect(flask.url_for('index'))
    posts = [
        {'author': user, 'body': 'Test post #1'},
        {'author': user, 'body': 'Test post #2'}
    ]
    return render_template('user.html',
                           user=user,
                           posts=posts)
