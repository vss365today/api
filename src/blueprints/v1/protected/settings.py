from webargs import fields
from webargs.flaskparser import use_args

from src.blueprints import settings
from src.core import helpers


@settings.route("/", methods=["GET"])
def get():
    """GET request to fetch configuration values."""
    return helpers.make_response(200)


@settings.route("/", methods=["POST"])
@use_args({"tk": fields.Str()}, location="json")
def post(args: dict):
    """"POST request to update configuration values."""
    return helpers.make_response(201)


@settings.route("/timer/", methods=["GET"])
def timer_get():
    """GET request to fetch fetch time values."""
    return helpers.make_response(200)


@settings.route("/timer/", methods=["POST"])
@use_args({"tk": fields.Str()}, location="json")
def timer_post(args: dict):
    """POST request to update finder time values."""
    return helpers.make_response(201)
