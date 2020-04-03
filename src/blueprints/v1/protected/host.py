from flask import jsonify

from webargs import fields
from webargs.flaskparser import use_args

from src.blueprints import host
from src.core import database
from src.core.helpers import make_response, make_error_response


@host.route("/", methods=["GET"])
@use_args(
    {"id": fields.Str(missing=""), "handle": fields.Str(missing="")}, location="query"
)
def get(args: dict):
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

    # We don't have that host
    given_param = [(k, v) for k, v in args.items() if v][0]
    return make_error_response(
        404, f"Unable to get details for Host {given_param[0]} {given_param[1]}!"
    )


@host.route("/date/", methods=["GET"])
@use_args({"date": fields.DateTime(required=True)}, location="query")
def get_date(args: dict):
    # We want the host for a given month
    found_host = database.host_get_by_date(args["date"].strftime("%Y-%m"))
    if found_host:
        return make_response(200, jsonify(found_host))
    return make_error_response(404, "Unable to get Host details!")


@host.route("/", methods=["POST"])
@use_args(
    {
        "id": fields.Str(required=True),
        "handle": fields.Str(required=True),
        "date": fields.DateTime(required=True),
    },
    location="json",
)
def post(args: dict):
    # TODO Create a single host with all their details
    result = True
    if result:
        return make_response(201)
    return make_error_response(503, "Unable to create a new Host!")
