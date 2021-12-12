from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Resource, Api
from flask_cors import CORS, cross_origin
import jwt
from . import auth
import os
#from app.services.user import send_email
#from web.serde.user import UserSchema
#from models.user import User
#from web import db

from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool



SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite://")

engine = create_engine(
    SQLALCHEMY_DATABASE_URI, 
    poolclass=StaticPool
)



app = Flask(__name__)
app.config.from_object("web.config.Config")
app.before_request_funcs.setdefault(None, [auth.decode_cookie])
# Threading and tasks for email? What is this?
#create_celery(app)

db = SQLAlchemy(app)
api = Api(app)
# TODO: Restrict CORS to only the API
cors = CORS(app, resources={r"/*": {"origins": "*"}})

# Research the best way to handle this
connection = engine.connect()

from web.models import User
print(User)

class DisplayHomePage(Resource):
    def get(self):
        return jsonify({"message": "Welcome to the Home Page"})

api.add_resource(DisplayHomePage, '/')

class DisplayUserProfile(Resource):
    def get(self, user_id):
        metadata = db.MetaData()
        user = db.Table('users', metadata, autoload=True, autoload_with=engine)
        #Equivalent to 'SELECT * FROM user'
        query = db.select([user]).where(user.c.id == user_id)
        ResultProxy = connection.execute(query)
        result = ResultProxy.fetchall()
        return jsonify({'result': [dict(row) for row in result]})

api.add_resource(DisplayUserProfile, '/users/<int:user_id>')

class AllUsers(Resource):
    def get(self):
        try:
            metadata = db.MetaData()
            user = db.Table('users', metadata, autoload=True, autoload_with=engine)
            #Equivalent to 'SELECT * FROM user'
            query = db.select([user])
            ResultProxy = connection.execute(query)
            result = ResultProxy.fetchall()
            return jsonify({'result': [dict(row) for row in result]})
        except:
            return jsonify({'result': 'Error'})

api.add_resource(AllUsers, '/users', methods=['GET', 'POST'])

class CreateUser(Resource):
    def post(self):
        new_user = User.User(
            email=request.json['email'],
            username=request.json['username'],
            password=request.json['password']
        )
        db.session.add(new_user)
        db.session.commit()
        #TODO: Add to db once model is finalized
        print("⭐⭐⭐⭐⭐⭐⭐")
        print(request)
        return jsonify({"message": "Success! Check your inbox for an activation email"})

api.add_resource(CreateUser, '/users/create', methods=['POST'])


class SignUpView(Resource):
    def post(self):
        data = request.get_json()
        '''
        print("✨✨✨✨✨")
        print(data)
        user = User.query.filter(
            func.lower(User.email) == data["email"].strip().lower()
        ).first()

        if user:
            abort(400, "This email address is already in use.")

        user = User()
        user.email = data["email"].strip()
        user.password = data["password"].strip()
        user.last_login = datetime.now()

        db.session.add(user)
        db.session.commit()
        # TODO: integrate with mailgun
        send_email(
            user.email,
            "Account activation",
            "verify_email.html",
            root_domain=request.url_root,
        )
        response = make_response("")
        response.set_cookie(
            "user",
            jwt.encode(
                UserSchema().dump(user), app.config["SECRET_KEY"], algorithm="HS256"
            ),
        )
        '''

        return data

api.add_resource(SignUpView, '/auth/signup', methods=['GET','POST'])

class SignInView(Resource):
    def post(self):
        data = request.get_json()
        return data

api.add_resource(SignInView, '/auth/signin', methods=['GET','POST'])

'''
    # TODO: integrate mailgun
    def send_email(to, subject, template, **kwargs):
        rendered = render_template(template, **kwargs)

        response = requests.post(
            "https://api.mailgun.net/v3/{}/messages".format(app.config["MAIL_DOMAIN"]),
            auth=("api", app.config["MAILGUN_API_KEY"]),
            data={
                "from": app.config["MAIL_SENDER"],
                "to": to,
                "subject": app.config["MAIL_SUBJECT_PREFIX"] + " " + subject,
                "html": rendered,
            },
        )

        return response.status_code == 201
'''

