from flask import current_app
from webargs import fields
from webargs.flaskparser import use_args

from src.blueprints import api_key
from src.core import database, helpers


@api_key.route("/", methods=["GET"])
@use_args({"token": fields.Str()}, location="query")
def get(args: dict):
    # Fetch the key permissions
    return database.api_key.get(args["token"])


@api_key.route("/", methods=["POST"])
def post():
    # database.api_key.create()
    return {}


@api_key.route("/", methods=["PUT"])
def put():
    # database.api_key.update()
    return {}


@api_key.route("/", methods=["DELETE"])
@use_args({"token": fields.Str()}, location="query")
def delete(args: dict):
    """DELETE request for deleting an API key."""
    database.api_key.delete(args["token"])
    return helpers.make_response(204)
