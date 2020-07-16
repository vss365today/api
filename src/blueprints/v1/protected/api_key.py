from webargs import fields
from webargs.flaskparser import use_args

from src.blueprints import api_key
from src.core import database, helpers


@api_key.route("/", methods=["GET"])
@use_args({"token": fields.Str()}, location="query")
def get(args: dict):
    """GET request to fetch the key permissions."""
    return database.api_key.get(args["token"])


@api_key.route("/", methods=["POST"])
@use_args(
    {
        "token": fields.Str(),
        "desc": fields.Str(),
        "has_admin": fields.Bool(),
        "has_archive": fields.Bool(),
        "has_broadcast": fields.Bool(),
        "has_host": fields.Bool(),
        "has_prompt": fields.Bool(),
        "has_subscription": fields.Bool(),
    },
    location="json",
)
def post(args: dict):

    # database.api_key.create()
    return {}


@api_key.route("/", methods=["PUT"])
@use_args(
    {
        "token": fields.Str(),
        "desc": fields.Str(),
        "has_admin": fields.Bool(),
        "has_archive": fields.Bool(),
        "has_broadcast": fields.Bool(),
        "has_host": fields.Bool(),
        "has_prompt": fields.Bool(),
        "has_subscription": fields.Bool(),
    },
    location="json",
)
def put(args: dict):

    # database.api_key.update()
    return {}


@api_key.route("/", methods=["DELETE"])
@use_args({"token": fields.Str()}, location="query")
def delete(args: dict):
    """DELETE request for deleting an API key."""
    database.api_key.delete(args["token"])
    return helpers.make_response(204)
