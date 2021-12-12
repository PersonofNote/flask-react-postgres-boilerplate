import os
import logging
import jwt

from flask import g, request, abort

from flask_restful import Resource, Api
#from models.user import User


def decode_cookie():
    cookie = request.cookies.get("user")

    if not cookie:
        g.cookie = {}
        return

    try:
        g.cookie = jwt.decode(cookie, os.environ["SECRET_KEY"], algorithms=["HS256"])
    except jwt.InvalidTokenError as err:
        logging.warning(str(err))
        abort(401)


def require_login(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if "id" not in g.cookie:
            logging.warning("No authorization provided!")
            abort(401)

        g.user = User.query.get(g.cookie["id"])

        if not g.user:
            response = make_response("", 401)
            response.set_cookie("user", "")
            return response

        return func(*args, **kwargs)

    return wrapper


class AuthenticatedView(Resource):
    method_decorators = [require_login]