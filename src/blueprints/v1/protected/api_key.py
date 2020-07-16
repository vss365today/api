from flask import current_app
from webargs import fields
from webargs.flaskparser import use_args

from src.blueprints import api_key
from src.core import database


@api_key.route("/", methods=["GET"])
def get():
    # database.api_key.info()
    return {}


@api_key.route("/", methods=["POST"])
def post():
    # database.api_key.update()
    return {}


@api_key.route("/", methods=["DELETE"])
def delete():
    # database.api_key.delete()
    return {}
