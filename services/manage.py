## Runs the app

from flask.cli import FlaskGroup
import logging
import os

logging.basicConfig(level=logging.DEBUG)


from web import app, db

from web.models import User

cli = FlaskGroup(app)

#SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite://")

@cli.command("create_db")
def create_db():
    db.drop_all()
    db.create_all()
    db.session.commit()


@cli.command("seed_db")
def seed_db():
    # TODO: implement error handling on this
    db.session.add(User.User(email="jessie@test.org", username="jessie", password="test"))
    db.session.add(User.User(email="bob@test.org", username="bob", password="test"))
    db.session.commit()


if __name__ == "__main__":
    print("Starting app")
    cli()