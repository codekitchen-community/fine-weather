from pathlib import Path

import pytest

from fw_manager import models, db

resources = Path(__file__).parent / "resources"


def test_auth(unauthorized_client):
    resp = unauthorized_client.get("/manager")
    assert resp.status_code == 401


@pytest.mark.run(order=1)
def test_add_image(client, app, set_global):
    resp = client.post(
        "/manager/images",
        data={
            "title": "Upload Test",
            "position": "SH",
            "time": "2024",
            "description": "Testing uploading...",
            "image": ((resources / "picture.png").open("rb"), "picture.png"),
        },
    )
    assert resp.status_code == 201
    newly_added = resp.json["result"]
    assert newly_added and not resp.json["err_code"]

    img = db.session.get(models.Image, newly_added)
    root_folder = Path(app.root_path)
    img_path = root_folder / img.uri
    img_thumbnail_path = root_folder / img.thumbnail_uri
    assert img_path.exists() and img_thumbnail_path.exists()

    set_global("newly_added", newly_added)


@pytest.mark.run(order=2)
def test_add_repeat(client, set_global):
    resp = client.post(
        "/manager/images",
        data={
            "title": "Upload Test",
            "position": "SH",
            "time": "2024",
            "description": "Testing uploading...",
            "image": ((resources / "picture.png").open("rb"), "picture.png"),
        },
    )
    assert resp.status_code == 200
    assert resp.json["err_code"] == "REPEAT_TITLE"


@pytest.mark.run(order=3)
def test_update_image(client, get_global):
    img = db.session.get(models.Image, get_global("newly_added"))
    assert img

    new_title = "Upload Test 3"
    resp = client.put(
        f"/manager/images/{img.id}",
        data={
            "title": new_title,
            "position": "SH",
            "time": "2024",
            "description": "Testing uploading...",
            "image": ((resources / "picture.png").open("rb"), "picture.png"),
        },
    )
    assert resp.status_code == 200

    updated_img = db.session.get(models.Image, img.id)
    assert updated_img.title == new_title


@pytest.mark.run(order=4)
def test_update_repeat(client, get_global, set_global):
    # upload another
    new_title = "Upload Test 2"
    resp = client.post(
        "/manager/images",
        data={
            "title": new_title,
            "position": "SH",
            "time": "2024",
            "description": "Testing uploading...",
            "image": ((resources / "picture.png").open("rb"), "picture.png"),
        },
    )
    assert resp.status_code == 201
    set_global("another_image", resp.json["result"])

    img = db.session.get(models.Image, get_global("newly_added"))
    assert img

    resp = client.put(
        f"/manager/images/{img.id}",
        data={
            "title": new_title,
            "position": "SH",
            "time": "2024",
            "description": "Testing uploading...",
            "image": ((resources / "picture.png").open("rb"), "picture.png"),
        },
    )
    assert resp.status_code == 200
    assert resp.json["err_code"] == "REPEAT_TITLE"


@pytest.mark.run(order=5)
def test_retrieve_image(client, get_global):
    resp = client.get("/images")
    assert resp.status_code == 200
    assert isinstance(resp.json["pages"], int)
    assert isinstance(resp.json["images"], list) and len(resp.json["images"]) == 2


@pytest.mark.run(order=6)
def test_delete_image(client, app, get_global):
    img_id = get_global("newly_added")
    img_id_another = get_global("another_image")

    img = db.session.get(models.Image, img_id)
    img_another = db.session.get(models.Image, img_id_another)
    assert img and img_another

    resp = client.delete(f"/manager/images/{img_id}")
    assert resp.status_code == 204
    resp = client.delete(f"/manager/images/{img_id_another}")
    assert resp.status_code == 204

    img_exist = models.Image.query.count()
    assert not img_exist

    root_folder = Path(app.root_path)
    img_path = root_folder / img.uri
    img_thumbnail_path = root_folder / img.thumbnail_uri
    img_path_another = root_folder / img_another.uri
    img_thumbnail_path_another = root_folder / img_another.thumbnail_uri
    assert not img_path.exists() and not img_thumbnail_path.exists()
    assert not img_path_another.exists() and not img_thumbnail_path_another.exists()
