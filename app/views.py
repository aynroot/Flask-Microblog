from datetime import datetime

import flask
from flask import render_template
from flask.ext.login import login_user, logout_user, current_user, login_required
from passlib.hash import sha256_crypt

from app import app, db, login_manager
from .models import User, Post
from .forms import LoginForm, SignUpForm, PostForm


@app.before_request
def before_request():
    flask.g.user = current_user


@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(body=form.post.data, timestamp=datetime.utcnow(), author=flask.g.user)
        db.session.add(post)
        db.session.commit()
        flask.flash('Your post is now live!')

        # this trick avoids inserting duplicate posts when a user
        # refreshes the page after submitting a blog post.
        # because before redirect we have POST and after - GET
        return flask.redirect(flask.url_for('index'))

    posts = flask.g.user.followed_posts().all()
    return render_template('index.html',
                           title='Home',
                           user=current_user,
                           form=form,
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

        # make the user follow himself
        db.session.add(user.follow(user))
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


@app.route('/follow/<nickname>')
@login_required
def follow(nickname):
    user = User.query.filter_by(nickname=nickname).first()
    if user is None:
        flask.flash('User %s not found.' % nickname)
        return flask.redirect(flask.url_for('index'))
    if user == flask.g.user:
        flask.flash('You can\'t follow yourself!')
        return flask.redirect(flask.url_for('user', nickname=nickname))
    u = flask.g.user.follow(user)
    if u is None:
        flask.flash('Cannot follow ' + nickname + '.')
        return flask.redirect(flask.url_for('user', nickname=nickname))
    db.session.add(u)
    db.session.commit()
    flask.flash('You are now following ' + nickname + '!')
    return flask.redirect(flask.url_for('user', nickname=nickname))


@app.route('/unfollow/<nickname>')
@login_required
def unfollow(nickname):
    user = User.query.filter_by(nickname=nickname).first()
    if user is None:
        flask.flash('User %s not found.' % nickname)
        return flask.redirect(flask.url_for('index'))
    if user == flask.g.user:
        flask.flash('You can\'t unfollow yourself!')
        return flask.redirect(flask.url_for('user', nickname=nickname))
    u = flask.g.user.unfollow(user)
    if u is None:
        flask.flash('Cannot unfollow ' + nickname + '.')
        return flask.redirect(flask.url_for('user', nickname=nickname))
    db.session.add(u)
    db.session.commit()
    flask.flash('You have stopped following ' + nickname + '.')
    return flask.redirect(flask.url_for('user', nickname=nickname))