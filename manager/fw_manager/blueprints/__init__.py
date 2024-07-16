from flask import Flask, Blueprint, redirect, url_for

from fw_manager.blueprints.manager import manager_bp
from fw_manager.blueprints.retriever import retriever_bp
from fw_manager.blueprints.error import error_bp

index_bp = Blueprint("index", __name__)


@index_bp.get("")
def index():
    return redirect(url_for("manager.images_page"))


def init_app(app: Flask):
    app.register_blueprint(index_bp, url_prefix="/")
    app.register_blueprint(manager_bp, url_prefix="/manager")
    app.register_blueprint(retriever_bp, url_prefix="/images")
    app.register_blueprint(error_bp)
