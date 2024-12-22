from flask import request, Blueprint

from ..models import db, Image, Site


retriever_bp = Blueprint("retriever", __name__)


@retriever_bp.get("")
def get_images():
    """Fetch images in JSON."""
    page = request.args.get("page", 1, type=int)
    page_size = request.args.get("page_size", 10, type=int)
    pagination = Image.query.order_by(Image.updated_at).paginate(
        page=page, per_page=page_size, error_out=False
    )
    images = [p.as_dict() for p in pagination.items]
    site = db.session.scalar(db.select(Site))
    return {
        "images": images,
        "pages": pagination.pages,
        "total": pagination.total,
        "site_title": site.title,
        "site_description": site.description,
        "no_image_tip": site.no_image_tip,
    }
