import click
from flask import Flask
from werkzeug.security import generate_password_hash

from .models import db, User


@click.command(name="create-tables")
@click.option("--username", prompt=True, help="Username used to login.")
@click.option(
    "--password",
    prompt=True,
    hide_input=True,
    confirmation_prompt=True,
    help="Password used to login.",
)
def create_tables(username, password) -> None:
    """Create all tables."""
    db.create_all()
    click.echo("Tables created")
    user = User.query.first()
    if user is not None:
        click.echo("Updating admin...")
        user.username = username
        user.password_hash = generate_password_hash(password)
    else:
        click.echo("Creating admin...")
        user = User(username=username, password_hash=generate_password_hash(password))
        db.session.add(user)
    click.echo("Done.")
    db.session.commit()


@click.command(name="drop-tables")
def drop_tables() -> None:
    """Drop all tables."""
    db.drop_all()
    click.echo("Tables dropped")


def init_app(app: Flask) -> None:
    app.cli.add_command(create_tables)
    app.cli.add_command(drop_tables)
