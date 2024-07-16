from flask import request, Blueprint

from ..models import Image


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
    return {"images": images, "pages": pagination.pages, "total": pagination.total}
