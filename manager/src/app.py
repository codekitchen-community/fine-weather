import os.path
import time
from datetime import datetime
from pathlib import Path
from uuid import uuid4

import blurhash
from flask_bootstrap import Bootstrap5
from flask import Flask, render_template, request, redirect, url_for, g
from flask_httpauth import HTTPBasicAuth
from flask_wtf import CSRFProtect
from loguru import logger
from PIL import Image as PImage
from sqlalchemy import or_
from werkzeug.security import check_password_hash

from .fw_manager import commands
from .fw_manager.forms import UploadImageForm, EditImageForm
from .fw_manager.models import db, User, Image

app = Flask(__name__, instance_path=Path("./instance").absolute())
app.config.from_prefixed_env()

bootstrap = Bootstrap5(app)
commands.init_app(app)
db.init_app(app)
auth = HTTPBasicAuth()

IMG_FOLDER = os.environ.get("IMG_FOLDER_NAME", "img")
THUMBNAIL_FOLDER = os.environ.get("THUMBNAIL_FOLDER_NAME", "thumbnail")
THUMBNAIL_MAX_WIDTH = os.environ.get("THUMBNAIL_MAX_WIDTH", 600)


def _make_resp(result=None, err_code="", msg="Success"):
    return {
        "result": result,
        "err_code": err_code,
        "msg": msg,
        "timestamp": int(time.time())
    }


@auth.verify_password
def verify_password(username, password):
    user = User.query.filter_by(username=username).first()
    if not user:
        return False
    g.current_user = user
    return check_password_hash(user.password_hash, password)


def _gen_thumbnail(src_img: PImage) -> tuple[PImage, str]:
    img = src_img.copy()
    w, h = img.size
    img.thumbnail((THUMBNAIL_MAX_WIDTH, round(THUMBNAIL_MAX_WIDTH / w * h)))
    img_hash = blurhash.encode(img.copy(), 4, 4)  # `blurhash.encode` will close the img passed in
    return img, img_hash


@app.get("/manager")
@auth.login_required
def images_page():
    """Images page."""
    page = request.args.get("page", 1, type=int)
    page_size = request.args.get("page_size", 10, type=int)
    keyword = request.args.get("keyword", "")
    pagination = Image.query.filter(
        or_(
            Image.title.contains(keyword),
            Image.description.contains(keyword),
            Image.position.contains(keyword),
            Image.time.contains(keyword)
        )
    ).order_by(Image.updated_at.desc()).paginate(page=page, per_page=page_size, error_out=False)
    if page > pagination.pages > 0:
        return redirect(url_for("get_images", page=1, page_size=page_size, keyword=keyword))
    return render_template(
        "manager.html",
        pagination=pagination,
        year=datetime.now().year,
        add_form=UploadImageForm(),
        edit_form=EditImageForm()
    )


@app.get("/images")
def get_images():
    """Fetch images in JSON."""
    page = request.args.get("page", 1, type=int)
    page_size = request.args.get("page_size", 10, type=int)
    pagination = Image.query.order_by(Image.updated_at.desc()).paginate(page=page, per_page=page_size, error_out=False)
    images = [p.as_dict() for p in pagination.items]
    return {
        "images": images,
        "pages": pagination.pages
    }


@app.post("/images")
@auth.login_required
def add_image():
    """Add one image."""
    img_folder = Path(app.static_folder) / IMG_FOLDER
    thumbnail_folder = img_folder / THUMBNAIL_FOLDER
    thumbnail_folder.mkdir(exist_ok=True, parents=True)
    img_name = ""

    try:
        form_data = request.form

        # check repetition
        img_repeat = Image.query.filter_by(title=form_data['title']).count()
        if img_repeat:
            return _make_resp(err_code="REPEAT_TITLE", msg="Image with same title exists.")

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
        thumbnail.save(thumbnail_uri)
        pil_img.save(img_uri)
        logger.info("Done.")

        # commit db record
        logger.info("Saving to db...")
        w, h = pil_img.size
        img = Image(
            uri=img_uri.relative_to(app.root_path).as_posix(),
            thumbnail_uri=thumbnail_uri.relative_to(app.root_path).as_posix(),
            title=form_data['title'],
            position=form_data['position'],
            time=form_data['time'],
            description=form_data['description'],
            blurhash=img_hash,
            width=w,
            height=h
        )
        db.session.add(img)
        db.session.commit()
        logger.info("Done.")
        return _make_resp(img.id)
    except Exception as e:
        err_msg = "An error occurred"
        logger.error(f"{err_msg} during image adding:\n{e!r}")
        if img_name:
            (img_folder / img_name).unlink(missing_ok=True)
            (thumbnail_folder / img_name).unlink(missing_ok=True)
        return _make_resp(err_code="INTERNAL_ERROR", msg=err_msg)


@app.put("/images/<image_id>")
@auth.login_required
def update_image(image_id):
    """Update info of one certain image."""
    try:
        form_data = request.form

        # check existence
        img = db.session.get(Image, image_id)
        if not img:
            return _make_resp(err_code="INVALID_IMAGE", msg="Target image does not exist.")

        # check repetition
        img_repeat = Image.query.filter_by(title=form_data['title']).filter(Image.id.isnot(image_id)).count()
        if img_repeat:
            return _make_resp(err_code="REPEAT_TITLE", msg="Image with same title exists.")

        img.title = form_data['title']
        img.position = form_data['position']
        img.time = form_data['time']
        img.description = form_data['description']

        db.session.commit()
        return _make_resp()
    except Exception as e:
        err_msg = "An error occurred"
        logger.error(f"{err_msg} during updating:\n{e!r}")
        return _make_resp(err_code="INTERNAL_ERROR", msg=err_msg)


@app.delete("/images/<image_id>")
@auth.login_required
def delete_image(image_id):
    """Delete one certain image."""
    try:
        img = db.session.get(Image, image_id)
        if not img:
            return _make_resp(err_code="INVALID_IMAGE", msg="Target image does not exist.")

        logger.info(f"Deleting db record: {image_id}...")
        db.session.delete(img)
        db.session.commit()
        logger.info("Done.")

        logger.info("Deleting file...")
        root_folder = Path(app.root_path)
        (root_folder / img.uri).unlink(missing_ok=True)
        (root_folder / img.thumbnail_uri).unlink(missing_ok=True)
        logger.info("Done.")
        return _make_resp(), 204
    except Exception as e:
        err_msg = "An error occurred"
        logger.error(f"{err_msg} during deleting:\n{e!r}")
        return _make_resp(err_code="INTERNAL_ERROR", msg=err_msg)
