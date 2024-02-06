from pathlib import Path

from flask_bootstrap import Bootstrap5
from flask import Flask
from flask_wtf import CSRFProtect

from . import commands, blueprints
from .models import db


def create_app():
    app = Flask(__name__, instance_path=Path("./instance").absolute())
    app.config.from_prefixed_env()

    Bootstrap5(app)
    CSRFProtect(app)
    commands.init_app(app)
    db.init_app(app)
    blueprints.init_app(app)

    return app
