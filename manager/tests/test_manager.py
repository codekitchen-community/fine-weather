import os
from pathlib import Path

import pytest

from ..src.fw_manager.models import Image

resources = Path(__file__).parent / "resources"
global_data = {}


@pytest.fixture
def set_global():
    def _set_global(key, value):
        global_data[key] = value

    return _set_global


@pytest.fixture
def get_global():
    return lambda key: global_data.get(key)


@pytest.fixture()
def context():
    os.environ.update({
        'FLASK_SQLALCHEMY_DATABASE_URI': 'sqlite:///',
        'FLASK_SECRET_KEY': 'test_secret_key',
        'FLASK_ENV': 'testing',
        'FLASK_WTF_CSRF_ENABLED': 'False'
    })
    from ..src.app import app, auth, db

    app.testing = True
    with app.app_context():
        db.create_all()
    yield app, auth, db
    app.testing = False


@pytest.fixture()
def authorized_client(context, monkeypatch):
    app, auth, _ = context
    authorized_client = app.test_client()
    monkeypatch.setattr(auth, 'authenticate', lambda *x: True)
    yield authorized_client


def test_auth(context):
    app, _, _ = context
    resp = app.test_client().get("/manager")
    assert resp.status_code == 401


@pytest.mark.run(order=1)
def test_add_image(authorized_client, context, set_global):
    resp = authorized_client.post("/images", data={
        "title": "Upload Test",
        "position": "SH",
        "time": "2024",
        "description": "Testing uploading...",
        "image": ((resources / "picture.png").open("rb"), "picture.png")
    })
    assert resp.status_code == 200
    newly_added = resp.json['result']
    assert newly_added and not resp.json['err_code']

    app, _, db = context
    with app.app_context():
        img = db.session.get(Image, newly_added)
        root_folder = Path(app.root_path)
        img_path = root_folder / img.uri
        img_thumbnail_path = root_folder / img.thumbnail_uri
        assert img_path.exists() and img_thumbnail_path.exists()

    set_global("newly_added", newly_added)


@pytest.mark.run(order=2)
def test_add_repeat(authorized_client, context, set_global):
    resp = authorized_client.post("/images", data={
        "title": "Upload Test",
        "position": "SH",
        "time": "2024",
        "description": "Testing uploading...",
        "image": ((resources / "picture.png").open("rb"), "picture.png")
    })
    assert resp.status_code == 200
    assert resp.json['err_code'] == 'REPEAT_TITLE'


@pytest.mark.run(order=3)
def test_update_image(authorized_client, context, get_global):
    app, _, db = context
    with app.app_context():
        img = db.session.get(Image, get_global("newly_added"))
        assert img

        new_title = "Upload Test 3"
        resp = authorized_client.put(f"/images/{img.id}", data={
            "title": new_title,
            "position": "SH",
            "time": "2024",
            "description": "Testing uploading...",
            "image": ((resources / "picture.png").open("rb"), "picture.png")
        })
        assert resp.status_code == 200

        updated_img = db.session.get(Image, img.id)
        assert updated_img.title == new_title


@pytest.mark.run(order=4)
def test_update_repeat(authorized_client, context, get_global, set_global):
    # upload another
    new_title = "Upload Test 2"
    resp = authorized_client.post("/images", data={
        "title": new_title,
        "position": "SH",
        "time": "2024",
        "description": "Testing uploading...",
        "image": ((resources / "picture.png").open("rb"), "picture.png")
    })
    assert resp.status_code == 200
    set_global('another_image', resp.json['result'])

    app, _, db = context
    with app.app_context():
        img = db.session.get(Image, get_global("newly_added"))
        assert img

        resp = authorized_client.put(f"/images/{img.id}", data={
            "title": new_title,
            "position": "SH",
            "time": "2024",
            "description": "Testing uploading...",
            "image": ((resources / "picture.png").open("rb"), "picture.png")
        })
        assert resp.status_code == 200
        assert resp.json['err_code'] == 'REPEAT_TITLE'


@pytest.mark.run(order=5)
def test_retrieve_image(authorized_client, context, get_global):
    resp = authorized_client.get("/images")
    assert resp.status_code == 200
    assert isinstance(resp.json['pages'], int)
    assert isinstance(resp.json['images'], list) and len(resp.json['images']) == 2


@pytest.mark.run(order=6)
def test_delete_image(authorized_client, context, get_global):
    img_id = get_global('newly_added')
    img_id_another = get_global('another_image')

    app, _, db = context
    with app.app_context():
        img = db.session.get(Image, img_id)
        img_another = db.session.get(Image, img_id_another)
        assert img and img_another

        resp = authorized_client.delete(f"/images/{img_id}")
        assert resp.status_code == 204
        resp = authorized_client.delete(f"/images/{img_id_another}")
        assert resp.status_code == 204

        img_exist = Image.query.count()
        assert not img_exist

        root_folder = Path(app.root_path)
        img_path = root_folder / img.uri
        img_thumbnail_path = root_folder / img.thumbnail_uri
        img_path_another = root_folder / img_another.uri
        img_thumbnail_path_another = root_folder / img_another.thumbnail_uri
        assert not img_path.exists() and not img_thumbnail_path.exists()
        assert not img_path_another.exists() and not img_thumbnail_path_another.exists()


