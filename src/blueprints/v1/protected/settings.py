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


@settings.route("/hosting", methods=["GET"])
@use_args(
    {
        "date": fields.DateTime(),
        "month": fields.Integer(validate=lambda x: 1 <= x <= 12),
    },
    location="query",
)
def hosting_get(args: dict):
    # Except one and only one parameter is supported
    if len(args) > 1:
        return helpers.make_error_response(422, "Only one parameter can be provided!")

    # We want the exact starting Hosting date for this day
    if "date" in args:
        return helpers.make_response(
            200, jsonify([database.settings.hosting_start_date_get(args["date"])])
        )

    # We want the Hosting dates for this month
    if "month" in args:
        return helpers.make_response(
            200, jsonify(database.settings.hosting_period_get(args["month"]))
        )

    # We didn't recieve any info so we don't know what to do ¯\_(ツ)_/¯
    return helpers.make_error_response(422, "A single parameter must be provided!")


@settings.route("/timings", methods=["GET"])
def timer_get():
    """GET request to fetch finder timing values."""
    return helpers.make_response(200, jsonify(database.settings.timings_get()))


@settings.route("/timings", methods=["PUT"])
@use_args({"timings": fields.List(fields.String())}, location="json")
def timer_put(args: dict):
    """PUT request to update finder timing values."""
    database.settings.timings_update(args["timings"])
    return helpers.make_response(201)
