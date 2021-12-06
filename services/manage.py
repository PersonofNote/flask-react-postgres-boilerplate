## Runs the app

from flask.cli import FlaskGroup
import logging

logging.basicConfig(level=logging.DEBUG)


from web import app, db, User


cli = FlaskGroup(app)

# Register command to the cli so we can run it from the terminal
@cli.command("create_db")
def create_db():
    db.drop_all()
    db.create_all()
    db.session.commit()


@cli.command("seed_db")
def seed_db():
    # TODO: implement error handling on this
    db.session.add(User(email="jessie@test.org"))
    db.session.add(User(email="bob@test.org"))
    db.session.commit()

from web.models import *

if __name__ == "__main__":
    cli()