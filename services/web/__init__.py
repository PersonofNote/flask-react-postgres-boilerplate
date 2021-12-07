from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Resource, Api
import os

app = Flask(__name__)
app.config.from_object("web.config.Config")
SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite://")

db = SQLAlchemy(app)
api = Api(app)

# TODO: move models into their own folder
class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(128), unique=True, nullable=False)
    active = db.Column(db.Boolean(), default=True, nullable=False)

    def __init__(self, email):
        self.email = email


class DisplayUserProfile(Resource):
    def get(self, user_id):
        engine = db.create_engine(SQLALCHEMY_DATABASE_URI, {})
        connection = engine.connect()
        metadata = db.MetaData()
        user = db.Table('users', metadata, autoload=True, autoload_with=engine)
        #Equivalent to 'SELECT * FROM user'
        query = db.select([user]).where(user.c.id == user_id)
        ResultProxy = connection.execute(query)
        result = ResultProxy.fetchall()
        return jsonify({'result': [dict(row) for row in result]})

    def put(self, user_id):
        #TODO: Add to db once model is finalized
        return(f"Adding user {user_id}")

api.add_resource(DisplayUserProfile, '/users/<int:user_id>')

class DisplayAllUsers(Resource):
    def get(self):
        engine = db.create_engine(SQLALCHEMY_DATABASE_URI, {})
        connection = engine.connect()
        metadata = db.MetaData()
        user = db.Table('users', metadata, autoload=True, autoload_with=engine)
        #Equivalent to 'SELECT * FROM user'
        query = db.select([user])
        ResultProxy = connection.execute(query)
        result = ResultProxy.fetchall()
        return jsonify({'result': [dict(row) for row in result]})

api.add_resource(DisplayAllUsers, '/users')


