import flask.ext.whooshalchemy as whooshalchemy

from app import app, db


followers = db.Table('followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('users.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('users.id'))
)


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), index=True, unique=True)
    nickname = db.Column(db.String(64), index=True, unique=True)
    password = db.Column(db.String(64))
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    followed = db.relationship('User',
                               secondary=followers,
                               primaryjoin=(followers.c.follower_id == id),
                               secondaryjoin=(followers.c.followed_id == id),
                               backref=db.backref('followers', lazy='dynamic'),
                               lazy='dynamic')

    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)
            return self

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)
            return self

    def is_following(self, user):
        return self.followed.filter(followers.c.followed_id == user.id).count() > 0

    def followed_posts(self):
        return Post.query.join(followers, (followers.c.followed_id == Post.user_id)).\
            filter(followers.c.follower_id == self.id).order_by(Post.timestamp.desc())

    def is_authenticated(self):
        """ should return True unless the object represents a user that should not be allowed to authenticate """
        return True

    def is_active(self):
        """ should return True for users unless they are inactive, f.e. because they are banned """
        return True

    def is_anonymous(self):
        """ should return True only for fake users that are not supposed to log in to the system """
        return False

    def get_id(self):
        return unicode(self.id)

    def __repr__(self):
        return '<User: %r>' % self.nickname


class Post(db.Model):
    __tablename__ = 'posts'
    __searchable__ = ['body']

    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    def __repr__(self):
        return '<Post: %r>' % self.body

whooshalchemy.whoosh_index(app, Post)
