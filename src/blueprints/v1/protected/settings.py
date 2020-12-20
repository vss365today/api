from flask import jsonify
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
        "identifiers": fields.List(fields.String()),
        "additionals": fields.List(fields.String()),
        "word_index": fields.Integer(),
    },
    location="json",
)
def put(args: dict):
    """PUT request to update configuration values."""
    database.settings.update(args)
    return helpers.make_response(201)


@settings.route("/timings/", methods=["GET"])
def timer_get():
    """GET request to fetch finder timing values."""
    return helpers.make_response(200, jsonify(database.settings.timings_get()))


@settings.route("/timings/", methods=["PUT"])
@use_args({"timings": fields.List(fields.String())}, location="json")
def timer_put(args: dict):
    """PUT request to update finder timing values."""
    database.settings.timings_update(args["timings"])
    return helpers.make_response(201)
