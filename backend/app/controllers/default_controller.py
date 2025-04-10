from flask.views import MethodView
from flask import jsonify
import logging
 
logger = logging.getLogger(__name__)
 
 
class DefaultController(MethodView):
 
    def __init__(self):
        pass
 
    def check_backend(self):
        logger.info("Handling GET > check_backend")
        return jsonify({"status": "OK"}), 200
 
    @classmethod
    def register(cls, app):
        logger.info("register routes")
 
        app.add_url_rule(
            "/api/check_backend",
            view_func=cls().check_backend,
            methods=["GET"],
        )