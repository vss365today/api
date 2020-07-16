from flask import current_app
from webargs import fields
from webargs.flaskparser import use_args

from src.blueprints import api_key
from src.core import database, helpers
from src.core.auth_helpers import get_auth_token


@api_key.route("/", methods=["GET"])
def get():
    token = get_auth_token()
    database.api_key.info(token)
    return {}


@api_key.route("/", methods=["POST"])
def post():
    # database.api_key.create()
    return {}


@api_key.route("/", methods=["PUT"])
def put():
    # database.api_key.update()
    return {}


@use_args({"token": fields.Str()}, location="query")
@api_key.route("/", methods=["DELETE"])
def delete(args: dict):
    """DELETE request for deleting an API key."""
    database.api_key.delete(args["token"])
    return helpers.make_response(204)
