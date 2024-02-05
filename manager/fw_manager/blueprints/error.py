from flask import Blueprint

from fw_manager.utils import make_resp

from loguru import logger

error_bp = Blueprint("error", __name__)


@error_bp.app_errorhandler(400)
def bad_request(err):
    logger.error(f"Bad request: {err!r}")
    return make_resp(err_code="BAD_REQUEST", msg="Bad request"), 400


@error_bp.app_errorhandler(403)
def not_authorized(err):
    logger.error(f"Not authorized: {err!r}")
    return make_resp(err_code="NOT_AUTHORIZED", msg="Not authorized"), 403


@error_bp.app_errorhandler(404)
def not_found(err):
    logger.error(f"Not found: {err!r}")
    return make_resp(err_code="NOT_FOUND", msg="404 not found"), 404


@error_bp.app_errorhandler(500)
def internal_server_error(err):
    logger.error(f"An error occurred: {err!r}")
    return make_resp(err_code="INTERNAL_ERROR", msg="An error occurred"), 500
