from app import db


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), index=True, unique=True)
    nickname = db.Column(db.String(64), index=True, unique=True)
    password = db.Column(db.String(64))
    posts = db.relationship('Post', backref='author', lazy='dynamic')

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

    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    def __repr__(self):
        return '<Post: %r>' % self.body
