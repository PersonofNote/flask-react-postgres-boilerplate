import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite://")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLACLHEMY_POOL_RECYCLE = int(os.getenv("SQLALCHEMY_POOL_RECYCLE", 300))
    SECRET_KEY = os.getenv("SECRET_KEY", "secret-key")
    # TODO: integrate mailgun
    '''
    MAILGUN_API_KEY = os.environ["MAILGUN_API_KEY"]
    MAIL_SUBJECT_PREFIX = "[A Minor Studios' Boilerplate App]"
    MAIL_SENDER = os.environ.get("MAIL_SENDER")
    MAIL_DOMAIN = os.environ["MAIL_DOMAIN"]
    '''
