import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.absolute()))
global_data = {}


@pytest.fixture
def set_global():
    def _set_global(key, value):
        global_data[key] = value

    return _set_global


@pytest.fixture
def get_global():
    return lambda key: global_data.get(key)


@pytest.fixture(autouse=True, scope="session")
def app():
    from fw_manager import create_app
    from fw_manager.models import db

    os.environ.update(
        {
            "FLASK_SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            "FLASK_SECRET_KEY": "test_secret_key",
            "FLASK_WTF_CSRF_ENABLED": "false",
            "FLASK_TESTING": "true",
        }
    )
    app = create_app()

    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture()
def unauthorized_client(app):
    yield app.test_client()


@pytest.fixture()
def client(app, monkeypatch):
    from fw_manager.blueprints.manager import auth

    authorized_client = app.test_client()
    monkeypatch.setattr(auth, "authenticate", lambda *_: True)
    yield authorized_client
