from webargs import fields
from webargs.flaskparser import use_args

from src.blueprints import settings
from src.core import database, helpers


@settings.route("/", methods=["GET"])
def get():
    """GET request to fetch configuration values."""
    return helpers.make_response(200, database.settings.get())


@settings.route("/", methods=["PUT"])
@use_args(
    {
        "identifiers": fields.List(fields.Str()),
        "additionals": fields.List(fields.Str()),
        "word_index": fields.Int(),
    },
    location="json",
)
def put(args: dict):
    """"POST request to update configuration values."""
    database.settings.update(args)
    return helpers.make_response(201)


@settings.route("/timer/", methods=["GET"])
def timer_get():
    """GET request to fetch fetch time values."""
    return helpers.make_response(200)


@settings.route("/timer/", methods=["PUT"])
@use_args({"tk": fields.Str()}, location="json")
def timer_put(args: dict):
    """POST request to update finder time values."""
    return helpers.make_response(201)
