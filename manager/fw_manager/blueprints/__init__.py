from flask import Flask

from fw_manager.blueprints.manager import manager_bp
from fw_manager.blueprints.retriever import retriever_bp


def init_app(app: Flask):
    app.register_blueprint(manager_bp, url_prefix="/manager")
    app.register_blueprint(retriever_bp, url_prefix="/images")
