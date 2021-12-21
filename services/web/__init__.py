from flask import Flask, jsonify, request, make_response, g, abort
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Resource, Api
from flask_cors import CORS, cross_origin
from werkzeug.security import check_password_hash
import jwt
from . import auth
import os
#from app.services.user import send_email
#from web.serde.user import UserSchema
#from models.user import User
#from web import db

from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from flask_jwt_extended import JWTManager


from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
#

errors = {
    'UserAlreadyExistsError': {
        'message': "A user with that username or password already exists",
        'status': 409,
    },
    'ResourceDoesNotExist': {
        'message': "A resource with that ID no longer exists.",
        'status': 410,
        'extra': "This user may have been deleted or deactivated",
    },
}



SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite://")

engine = create_engine(
    SQLALCHEMY_DATABASE_URI, 
    poolclass=StaticPool
)



app = Flask(__name__)
app.config.from_object("web.config.Config")
app.before_request_funcs.setdefault(None, [auth.decode_cookie])

# Setup the Flask-JWT-Extended extension
app.config["JWT_SECRET_KEY"] = os.environ['JWT_SECRET_KEY']
jwt = JWTManager(app)

# Setup SqlAlchemy
db = SQLAlchemy(app)
api = Api(app)
# TODO: Restrict CORS to only the API
cors = CORS(app, resources={r"/*": {"origins": "*"}})

# Research the best way to handle this
connection = engine.connect()

from web.models import User

# TODO: Make this not be this way. It's weird.
User = User.User


# Create a route to authenticate your users and return JWTs. The
# create_access_token() function is used to actually generate the JWT.
@app.route("/logtest", methods=["POST"])
def login():
    print(request)
    email = request.json.get("username", "")
    password = request.json.get("password", "")
    user = User.query.filter(
           User.email == email.strip().lower()
    ).first()
    if user is None or not user.verify_password(password):
        return make_response(jsonify({"error": "Check your credentials and try again"}), 401)
    access_token = create_access_token(identity=email)
    return jsonify(access_token=access_token)


# Protect a route with jwt_required, which will kick out requests
# without a valid JWT present.
# For testing only
@app.route("/protected", methods=["GET"])
@jwt_required
def protected():
    # Access the identity of the current user with get_jwt_identity
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200 

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


class SignUpView(Resource):
    def post(self):
        data = request.get_json()
        user = User.query.filter(
           User.email == data["email"].strip().lower()
        ).first()
        if user:
            abort(400, "This email or username is already in use.")

        user = User(data["email"].strip(), data["username"].strip(), data["password"].strip())

        db.session.add(user) 
        db.session.commit()

        # TODO: integrate with mailgun
        '''
        send_email(
            user.email,
            "Account activation",
            "verify_email.html",
            root_domain=request.url_root,
        )
        '''
        response = make_response("")

        # TODO: modify response to indicate email was sent
        return jsonify({"message": "Success!"})


# TODO: add home redirect
api.add_resource(SignUpView, '/auth/signup', methods=['POST'])

class SignInView(Resource):
    def post(self):
        data = request.get_json()
        email = data["username"]
        password = data["password"]
        user = User.query.filter(
            User.email == email.strip().lower()
        ).first()
        if user is None or not user.verify_password(password):
            return make_response(jsonify({"error": "Check your credentials and try again"}), 401)
        access_token = create_access_token(identity=email)
        return jsonify({'status': 200, 'user': {'email': user.email, 'username': user.username, 'id': user.id, 'access_token': access_token}})

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

