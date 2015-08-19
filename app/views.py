from datetime import datetime

import flask
from flask import render_template
from flask.ext.babel import gettext
from flask.ext.login import login_user, logout_user, current_user, login_required
from passlib.hash import sha256_crypt

import config
from app import app, db, login_manager, babel
from .models import User, Post
from .forms import LoginForm, SignUpForm, PostForm, SearchForm


@babel.localeselector
def get_locale():
    return flask.request.accept_languages.best_match(config.LANGUAGES.keys())


@app.before_request
def before_request():
    flask.g.user = current_user
    if flask.g.user.is_authenticated():
        flask.g.search_form = SearchForm()


@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@app.route('/index/<int:page>', methods=['GET', 'POST'])
@login_required
def index(page=1):
    form = PostForm()
    if form.validate_on_submit():
        post = Post(body=form.post.data, timestamp=datetime.utcnow(), author=flask.g.user)
        db.session.add(post)
        db.session.commit()
        flask.flash(gettext('Your post is now live!'))

        # this trick avoids inserting duplicate posts when a user
        # refreshes the page after submitting a blog post.
        # because before redirect we have POST and after - GET
        return flask.redirect(flask.url_for('index'))

    # posts = flask.g.user.followed_posts().all()
    posts = flask.g.user.followed_posts().paginate(page, config.POSTS_PER_PAGE, False)
    return render_template('index.html',
                           title='Home',
                           user=current_user,
                           form=form,
                           posts=posts)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if flask.g.user is not None and flask.g.user.is_authenticated():
        flask.flash(gettext('Already authenticated.'))
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
        flask.flash(gettext('Successfully signed up. Try to login.'))
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
        flask.flash(gettext('Already authenticated.'))
        return flask.redirect(flask.url_for('index'))

    form = LoginForm()
    if form.validate_on_submit():
        flask.session['remember_me'] = form.remember_me.data
        user = User.query.filter_by(email=form.email.data).first()

        if not user:
            flask.flash(gettext('No such email in database'))
            return render_template('login.html',
                                   title='Sign In',
                                   form=form)
        if sha256_crypt.verify(form.password.data, user.password):
            login_user(user, remember=form.remember_me.data)
            flask.flash(gettext('Logged in successfully.'))
            return flask.redirect(flask.url_for('index'))
        else:
            flask.flash(gettext('Wrong password'))
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
    flask.flash(gettext('Successfully logged out'))
    return flask.redirect(flask.url_for('index'))


@app.route('/user/<nickname>')
@app.route('/user/<nickname>/<int:page>')
@login_required
def user(nickname, page=1):
    user = User.query.filter_by(nickname=nickname).first()
    if user is None:
        flask.flash(gettext('User %(name)s not found.', name=nickname))
        return flask.redirect(flask.url_for('index'))
    posts = user.posts.paginate(page, config.POSTS_PER_PAGE, False)
    return render_template('user.html',
                           user=user,
                           posts=posts)


@app.route('/follow/<nickname>')
@login_required
def follow(nickname):
    user = User.query.filter_by(nickname=nickname).first()
    if user is None:
        flask.flash(gettext('User %(name)s not found.', name=nickname))
        return flask.redirect(flask.url_for('index'))
    if user == flask.g.user:
        flask.flash(gettext('You can\'t follow yourself!'))
        return flask.redirect(flask.url_for('user', nickname=nickname))
    u = flask.g.user.follow(user)
    if u is None:
        flask.flash(gettext('Cannot follow %(name)s.', name=nickname))
        return flask.redirect(flask.url_for('user', nickname=nickname))
    db.session.add(u)
    db.session.commit()
    flask.flash(gettext('You are now following %(name)s!', name=nickname))
    return flask.redirect(flask.url_for('user', nickname=nickname))


@app.route('/unfollow/<nickname>')
@login_required
def unfollow(nickname):
    user = User.query.filter_by(nickname=nickname).first()
    if user is None:
        flask.flash(gettext('User %(name)s not found.', name=nickname))
        return flask.redirect(flask.url_for('index'))
    if user == flask.g.user:
        flask.flash(gettext('You can\'t unfollow yourself!'))
        return flask.redirect(flask.url_for('user', nickname=nickname))
    u = flask.g.user.unfollow(user)
    if u is None:
        flask.flash(gettext('Cannot unfollow %(name)s.', name=nickname))
        return flask.redirect(flask.url_for('user', nickname=nickname))
    db.session.add(u)
    db.session.commit()
    flask.flash(gettext('You have stopped following %(name)s.', name=nickname))
    return flask.redirect(flask.url_for('user', nickname=nickname))


@app.route('/search', methods=['POST'])
@login_required
def search():
    if not flask.g.search_form.validate_on_submit():
        return flask.redirect(flask.url_for('index'))
    return flask.redirect(flask.url_for('search_results', query=flask.g.search_form.search.data))


@app.route('/search_results/<query>')
@login_required
def search_results(query):
    results = Post.query.whoosh_search(query, config.MAX_SEARCH_RESULTS).all()
    return render_template('search_results.html',
                           query=query,
                           results=results)