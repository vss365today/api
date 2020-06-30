from flask import jsonify

from webargs import fields
from webargs.flaskparser import use_args

from src.blueprints import host
from src.core import database
from src.core.helpers import make_response, make_error_response, format_datetime_iso


@host.route("/", methods=["GET"])
@use_args(
    {"id": fields.Str(missing=""), "handle": fields.Str(missing="")}, location="query"
)
def get(args: dict):
    """Get a Host by their Twitter ID or handle."""
    # We need something to search by
    if not args["id"] and not args["handle"]:
        return make_error_response(422, "Either a Host id or handle must be provided!")

    # Both a host ID and handle cannot be provided
    if args["id"] and args["handle"]:
        return make_error_response(
            422, "Providing a Host id and handle is not allowed!"
        )

    # Get the host information
    found_host = database.host_get(uid=args["id"], handle=args["handle"])
    if found_host:
        return make_response(200, jsonify(found_host))

    # Determine which param was given
    given_param = [(k, v) for k, v in args.items() if v][0]

    # We don't have that host
    return make_error_response(
        404, f"Unable to get details for Host {given_param[0]} {given_param[1]}!"
    )


@host.route("/", methods=["POST"])
@use_args(
    {
        "id": fields.Str(required=True),
        "handle": fields.Str(required=True),
        "date": fields.DateTime(missing=None, allow_none=True),
    },
    location="json",
)
def post(args: dict):
    """Create a new Host."""
    # Rewrite the date into the proper format if it's present
    if args["date"] is not None:
        args["date"] = format_datetime_iso(args["date"])

    # Create a host with all their details
    result = database.host_create(args)
    if result:
        return make_response(201)
    return make_error_response(503, f'Unable to create new Host {args["handle"]}!')


@host.route("/", methods=["PATCH"])
@use_args(
    {
        "id": fields.Str(required=True),
        "handle": fields.Str(missing=None, allow_none=True),
        "date": fields.DateTime(missing=None, allow_none=True),
    },
    location="json",
)
def patch(args: dict):
    """Update a Host."""
    # Rewrite the date into the proper format if it's present
    if args["date"] is not None:
        args["date"] = format_datetime_iso(args["date"])

    # Attempt to find the host, bc they must exist to be updated
    existing_host = database.host_get(uid=args["id"], handle="")
    if not existing_host:
        return make_error_response(400, "Unable to update Host details!")

    # Update the host with the new info
    database.host_update(args)
    return make_response(200)


@host.route("/", methods=["DELETE"])
@use_args({"id": fields.Str(required=True)}, location="query")
def delete(args: dict):
    """Delete a Host.

    This will only succeed if the Host does not have any associated
    Prompts to prevent orphaned records or an incomplete record."""
    result = database.host_delete(args["id"])
    if result:
        return make_response(204)
    return make_error_response(
        403,
        f"Unable to delete Host {args['id']}! They have Prompts associated with them.",
    )


@host.route("date/", methods=["GET"])
@use_args({"date": fields.DateTime(required=True)}, location="query")
def get_date(args: dict):
    """Get the assigned Host for the specified month."""
    found_host = database.host_get_by_date(format_datetime_iso(args["date"]))
    if found_host:
        return make_response(200, jsonify(found_host))
    return make_error_response(404, "Unable to get Host details!")
