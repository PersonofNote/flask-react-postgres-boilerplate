from werkzeug.security import generate_password_hash, check_password_hash
from web import db
import uuid


class User(db.Model):
    __tablename__ = "users"
    # Will also check uniqueness in the app itself
    __table_args__ = (db.UniqueConstraint("google_id"), db.UniqueConstraint("email"))

    id = db.Column(db.Integer, primary_key=True)
    
    # An ID to use as a reference when sending email.
    external_id = db.Column(
        db.String, default=lambda: str(uuid.uuid4()), nullable=False
    )
    
    google_id = db.Column(db.String, nullable=True)
    activated = db.Column(db.Boolean, default=False, server_default="f", nullable=False)

    # When the user chooses to set up an account directly with the app.
    _password = db.Column(db.String)

    username = db.Column(db.String, nullable=True)
    email = db.Column(db.String, nullable=True)
    picture = db.Column(db.String, nullable=True)

    last_login = db.Column(db.DateTime, nullable=True)

    @property
    def password(self):
        raise AttributeError("Can't read password")

    # Called when the user sets the password; looks like an attribute, is a method
    @password.setter
    def password(self, password):
        self._password = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self._password, password)

    def __init__(self, email, username, password):
        self.email = email
        self.username = username
        self.password = password
