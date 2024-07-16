import os.path
from datetime import datetime
from pathlib import Path
from uuid import uuid4

import blurhash
from flask import render_template, request, redirect, url_for, g, Blueprint, current_app
from flask_httpauth import HTTPBasicAuth
from loguru import logger
from PIL import Image as PImage
from sqlalchemy import or_
from werkzeug.security import check_password_hash

from ..utils import make_resp
from ..models import User, Image, db
from ..forms import UploadImageForm, EditImageForm

IMG_FOLDER = os.environ.get("IMG_FOLDER_NAME", "img")
THUMBNAIL_FOLDER = os.environ.get("THUMBNAIL_FOLDER_NAME", "thumbnail")
THUMBNAIL_MAX_WIDTH = int(os.environ.get("THUMBNAIL_MAX_WIDTH", 600))


manager_bp = Blueprint("manager", __name__)
auth = HTTPBasicAuth()


@auth.verify_password
def verify_password(username, password):
    user = User.query.filter_by(username=username).first()
    if not user:
        return False
    g.current_user = user
    return check_password_hash(user.password_hash, password)


def _gen_thumbnail(src_img: PImage.Image) -> tuple[PImage.Image, str]:
    img = src_img.copy()
    w, h = img.size
    img.thumbnail((THUMBNAIL_MAX_WIDTH, round(THUMBNAIL_MAX_WIDTH / w * h)))
    img_hash = blurhash.encode(
        img.copy(), 4, 4
    )  # `blurhash.encode` will close the img passed in
    return img, img_hash


@manager_bp.get("")
@auth.login_required
def images_page():
    """Images page."""
    page = request.args.get("page", 1, type=int)
    page_size = request.args.get("page_size", 10, type=int)
    keyword = request.args.get("keyword", "")
    pagination = (
        Image.query.filter(
            or_(
                Image.title.contains(keyword),
                Image.description.contains(keyword),
                Image.position.contains(keyword),
                Image.time.contains(keyword),
            )
        )
        .order_by(Image.updated_at.desc())
        .paginate(page=page, per_page=page_size, error_out=False)
    )
    if page > pagination.pages > 0:
        return redirect(
            url_for("get_images", page=1, page_size=page_size, keyword=keyword)
        )
    return render_template(
        "manager.html",
        pagination=pagination,
        year=datetime.now().year,
        add_form=UploadImageForm(),
        edit_form=EditImageForm(),
    )


@manager_bp.post("/images")
@auth.login_required
def add_image():
    """Add one image."""
    img_folder = Path(current_app.static_folder) / IMG_FOLDER
    thumbnail_folder = img_folder / THUMBNAIL_FOLDER
    thumbnail_folder.mkdir(exist_ok=True, parents=True)

    form_data = request.form

    # check repetition
    img_exist = db.session.scalar(db.select(Image).filter_by(title=form_data["title"]))
    if img_exist:
        return make_resp(err_code="REPEAT_TITLE", msg="Image with same title exists.")

    # save image/thumbnail
    [(_, img_file)] = request.files.items()

    img_name = f"{uuid4().hex}_{img_file.filename}"
    img_uri = img_folder / img_name
    pil_img = PImage.open(img_file)

    logger.info("Generating thumbnail...")
    thumbnail_uri = thumbnail_folder / img_name
    thumbnail, img_hash = _gen_thumbnail(pil_img)
    logger.info("Done.")

    logger.info("Saving file...")
    if (
        any([img_uri.name.lower().endswith(suffix) for suffix in ["jpg", "jpeg"]])
        and pil_img.mode == "RGBA"
    ):
        pil_img = pil_img.convert("RGB")
        thumbnail = thumbnail.convert("RGB")
    thumbnail.save(thumbnail_uri)
    pil_img.save(img_uri)
    logger.info("Done.")

    # commit db record
    logger.info("Saving to db...")
    w, h = pil_img.size
    img = Image(
        uri=img_uri.relative_to(current_app.root_path).as_posix(),
        thumbnail_uri=thumbnail_uri.relative_to(current_app.root_path).as_posix(),
        title=form_data["title"],
        position=form_data["position"],
        time=form_data["time"],
        description=form_data["description"],
        blurhash=img_hash,
        width=w,
        height=h,
    )
    db.session.add(img)
    db.session.commit()

    logger.info("Done.")
    return make_resp(img.id), 201


@manager_bp.put("/images/<image_id>")
@auth.login_required
def update_image(image_id):
    """Update info of one certain image."""
    form_data = request.form

    # check existence
    img = db.session.get(Image, image_id)
    if not img:
        return make_resp(err_code="INVALID_IMAGE", msg="Target image does not exist.")

    # check repetition
    img_repeat = db.session.scalar(
        db.select(Image)
        .filter_by(title=form_data["title"])
        .filter(Image.id.isnot(image_id))
    )
    if img_repeat:
        return make_resp(err_code="REPEAT_TITLE", msg="Image with same title exists.")

    img.title = form_data["title"]
    img.position = form_data["position"]
    img.time = form_data["time"]
    img.description = form_data["description"]

    db.session.commit()
    return make_resp()


@manager_bp.delete("/images/<image_id>")
@auth.login_required
def delete_image(image_id):
    """Delete one certain image."""
    img = db.session.get(Image, image_id)
    if not img:
        return make_resp(err_code="INVALID_IMAGE", msg="Target image does not exist.")

    logger.info(f"Deleting db record: {image_id}...")
    db.session.delete(img)
    db.session.commit()
    logger.info("Done.")

    logger.info("Deleting file...")
    root_folder = Path(current_app.root_path)
    (root_folder / img.uri).unlink(missing_ok=True)
    (root_folder / img.thumbnail_uri).unlink(missing_ok=True)
    logger.info("Done.")
    return "", 204
