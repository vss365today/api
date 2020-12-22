from flask import jsonify

from webargs import fields
from webargs.flaskparser import use_args

from src.blueprints import host
from src.core import database, helpers
from src.core.auth_helpers import authorize_route


@host.route("/", methods=["GET"])
@use_args(
    {
        "id": fields.String(missing=""),
        "handle": fields.String(missing=""),
        "all": fields.Boolean(),
    },
    location="query",
)
def get(args: dict):
    """Get a Host by their Twitter ID or handle."""
    # Return a list of all Hosts
    if "all" in args and args["all"]:
        return helpers.make_response(200, jsonify(database.host.get_all()))

    # We need something to search by
    if not args["id"] and not args["handle"]:
        return helpers.make_error_response(
            422, "Either a Host id or handle must be provided!"
        )

    # Both a host ID and handle cannot be provided
    if args["id"] and args["handle"]:
        return helpers.make_error_response(
            422, "Providing a Host id and handle is not allowed!"
        )

    # Get the host information
    found_host = database.host.get(uid=args["id"], handle=args["handle"])
    if found_host:
        return helpers.make_response(200, jsonify(found_host))

    # Determine which param was given
    given_param = [(k, v) for k, v in args.items() if v][0]

    # We don't have that host
    return helpers.make_error_response(
        404, f"Unable to get details for Host {given_param[0]} {given_param[1]}!"
    )


@authorize_route
@host.route("/", methods=["POST"])
@use_args({"handle": fields.String(required=True)}, location="json")
def post(args: dict):
    """Create a new Host."""
    if database.host.exists(uid="", handle=args["handle"]):
        return helpers.make_error_response(
            422, f'Host {args["handle"]} already exists!'
        )

    # Get the Twitter user ID for this Host
    host_id = database.host.lookup(args["handle"])
    if not host_id:
        return helpers.make_error_response(
            503, f'Unable to find Twitter account {args["handle"]}!'
        )

    # Create a host with all their details
    args["id"] = host_id
    result = database.host.create(args)
    if result:
        return helpers.make_response(201, args)
    return helpers.make_error_response(
        503, f'Unable to create new Host {args["handle"]}!'
    )


@authorize_route
@host.route("/", methods=["PATCH"])
@use_args(
    {"id": fields.String(required=True), "handle": fields.String(required=True)},
    location="json",
)
def patch(args: dict):
    """Update a Host's handle."""
    # Attempt to find the host. They must exist to be updated
    existing_host = database.host.get(uid=args["id"], handle="")
    if not existing_host:
        return helpers.make_error_response(400, "Unable to update Host details!")

    # Update the host
    database.host.update(args)
    return helpers.make_response(200)


@authorize_route
@host.route("/", methods=["DELETE"])
@use_args({"id": fields.String(required=True)}, location="query")
def delete(args: dict):
    """Delete a Host.

    This will only succeed if the Host does not have any associated
    Prompts to prevent orphaned records or an incomplete record."""
    result = database.host.delete(args["id"])
    if result:
        return helpers.make_response(204)
    return helpers.make_error_response(
        403,
        f"Unable to delete Host {args['id']}! They have Prompts associated with them.",
    )


@host.route("/date/", methods=["GET"])
@use_args({"date": fields.DateTime(required=True)}, location="query")
def date_get(args: dict):
    """Get the assigned Host for the specified date."""
    current_host = database.host.get_by_date(helpers.format_datetime_ymd(args["date"]))
    if current_host:
        return helpers.make_response(200, jsonify(current_host))
    return helpers.make_error_response(404, "Unable to get Host details!")


@authorize_route
@host.route("/date/", methods=["POST"])
@use_args(
    {"id": fields.String(required=True), "date": fields.DateTime(required=True)},
    location="json",
)
def date_post(args: dict):
    """Create a new hosting date for the given Host."""
    result = database.host.create_date(args)
    if result:
        return helpers.make_response(201)
    return helpers.make_error_response(
        503, f'Unable to create new hosting date for {args["date"]}!'
    )


@authorize_route
@host.route("/date/", methods=["DELETE"])
@use_args(
    {"id": fields.String(required=True), "date": fields.DateTime(required=True)},
    location="query",
)
def date_delete(args: dict):
    """Delete a Host's assigned date."""
    database.host.delete_date(args["id"], helpers.format_datetime_ymd(args["date"]))
    return helpers.make_response(204)
