from webargs import fields
from webargs.flaskparser import use_args

from src.blueprints import config
from src.core import helpers


@config.route("/", methods=["GET"])
def get():
    """GET request to fetch configuration values."""
    return helpers.make_response(200)


@config.route("/", methods=["POST"])
@use_args({}, location="json")
def post(args: dict):
    """"POST request to update configuration values."""
    return helpers.make_response(201)


@config.route("/timer/", methods=["GET"])
def timer_get():
    """GET request to fetch fetch time values."""
    return helpers.make_response(200)


@config.route("/timer/", methods=["POST"])
@use_args({}, location="json")
def timer_post(args: dict):
    """POST request to update finder time values."""
    return helpers.make_response(201)
