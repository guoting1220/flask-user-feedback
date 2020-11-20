"""Models for flask-feedback"""

from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

db = SQLAlchemy()

bcrypt = Bcrypt()

def connect_db(app):
    """Connect this database to Flask app.
    Call this function in Flask app.
    """
    db.app = app
    db.init_app(app)
    

class User(db.Model):
    """model for user"""

    __tablename__ = "user" 

    username = db.Column(db.String(20), nullable=False, primary_key=True, unique=True)
    password = db.Column(db.Text, nullable=False)
    email = db.Column(db.String(50), nullable=False)
    first_name = db.Column(db.String(30), nullable=False)
    last_name = db.Column(db.String(30), nullable=False)

    feedbacks = db.relationship(
        "Feedback", backref="user", cascade="all,delete")

    @classmethod
    def register(cls, username, password, first_name, last_name, email):
        """register a user with hashed password & return user"""

        hashed = bcrypt.generate_password_hash(password)
        # turn bytestring into normal (unicode utf8) string
        hashed_utf8 = hashed.decode("utf8")

        # return instance of user w/username and hashed password
        return cls(username=username, 
                   password=hashed_utf8, 
                   first_name=first_name, 
                   last_name=last_name, 
                   email=email)

    @classmethod
    def authenticate(cls, username, password):
        """validate that user exists & password is correct"""

        user = User.query.filter_by(username=username).first()
        if user and bcrypt.check_password_hash(user.password, password):
            return user
        else: 
            return False    


class Feedback(db.Model):
    """model for Feedback"""

    __tablename__ = "feedback"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    username = db.Column(db.String(20), db.ForeignKey('user.username'), nullable=False)





