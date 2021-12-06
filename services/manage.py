## Runs the app

from flask.cli import FlaskGroup

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
    db.session.add(User(email="jessie@test.org"))
    db.session.commit()


if __name__ == "__main__":
    cli()