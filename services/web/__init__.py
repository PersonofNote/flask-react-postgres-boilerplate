from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.config.from_object("web.config.Config")
SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite://")

db = SQLAlchemy(app)


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(128), unique=True, nullable=False)
    active = db.Column(db.Boolean(), default=True, nullable=False)

    def __init__(self, email):
        self.email = email

# Prevents circular imports?
'''
def init_app(app):
    db.init_app(app)

    from app.api import api_blueprint

    app.register_blueprint(api_blueprint)

    return app
'''

@app.route("/")
def hello_world():
    return jsonify(hello="world")


@app.route("/users/<int:user_id>")
def fetch_user_profile(user_id):
    engine = db.create_engine(SQLALCHEMY_DATABASE_URI, {})
    connection = engine.connect()
    metadata = db.MetaData()
    user = db.Table('users', metadata, autoload=True, autoload_with=engine)
    #Equivalent to 'SELECT * FROM user'
    query = db.select([user]).where(user.c.id == user_id)
    ResultProxy = connection.execute(query)
    result = ResultProxy.fetchall()
    return jsonify({'result': [dict(row) for row in result]})


@app.route("/users")
def fetch_all_users():
    engine = db.create_engine(SQLALCHEMY_DATABASE_URI, {})
    connection = engine.connect()
    metadata = db.MetaData()
    user = db.Table('users', metadata, autoload=True, autoload_with=engine)
    #Equivalent to 'SELECT * FROM user'
    query = db.select([user])
    ResultProxy = connection.execute(query)
    result = ResultProxy.fetchall()
    return jsonify({'result': [dict(row) for row in result]})

