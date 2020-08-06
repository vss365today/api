from flask import jsonify
from webargs import fields
from webargs.flaskparser import use_args

from src.blueprints import api_key
from src.core import database, helpers


@api_key.route("/", methods=["GET"])
@use_args(
    {"token": fields.Str(), "all": fields.Bool()}, location="query",
)
def get(args: dict):
    """GET request to fetch key permissions."""
    # Cannot request info for a single key and all keys
    if "token" in args and "all" in args:
        return helpers.make_error_response(
            422, "Cannot request individual and all key info together!"
        )

    # We want all key info
    if "all" in args and args["all"]:
        records = database.api_key.get_all()
        return helpers.make_response(200, jsonify(records))

    # We want info on a single key
    if "token" in args:
        record = database.api_key.get(args["token"])
        if record is not None:
            return helpers.make_response(200, record)
        return helpers.make_error_response(404, "Could not get key information!")

    # Some form of info must be requested
    return helpers.make_error_response(
        422, "Must request some form of key information!"
    )


@api_key.route("/", methods=["POST"])
@use_args(
    {
        "desc": fields.Str(),
        "has_api_key": fields.Bool(),
        "has_archive": fields.Bool(),
        "has_broadcast": fields.Bool(),
        "has_host": fields.Bool(),
        "has_prompt": fields.Bool(),
        "has_subscription": fields.Bool(),
    },
    location="json",
)
def post(args: dict):
    """POST request to create a new API key."""
    # Create the token
    result = database.api_key.create(args)

    # Respond according to if it was successful or not
    if result:
        return helpers.make_response(201, result)
    return helpers.make_error_response(422, "Unable to create a new API key!")


@api_key.route("/", methods=["PUT"])
@use_args(
    {
        "token": fields.Str(),
        "desc": fields.Str(),
        "has_api_key": fields.Bool(),
        "has_archive": fields.Bool(),
        "has_broadcast": fields.Bool(),
        "has_host": fields.Bool(),
        "has_prompt": fields.Bool(),
        "has_subscription": fields.Bool(),
    },
    location="json",
)
def put(args: dict):
    """PUT request to update an existing API key."""
    # That key doesn't exist
    if not database.api_key.exists(args["token"]):
        return helpers.make_error_response(
            404, "The requested API key does not exist!",
        )

    # Update and respond accordingly
    result = database.api_key.update(args)
    if result:
        return helpers.make_response(200)
    return helpers.make_error_response(422, "Unable to update the API key!")


@api_key.route("/", methods=["DELETE"])
@use_args({"token": fields.Str()}, location="query")
def delete(args: dict):
    """DELETE request for deleting an API key."""
    database.api_key.delete(args["token"])
    return helpers.make_response(204)
