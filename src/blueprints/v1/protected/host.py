from flask import jsonify

from webargs import fields
from webargs.flaskparser import use_args

from src.blueprints import host
from src.core import database
from src.core.helpers import make_response, make_error_response


@host.route("/", methods=["GET"])
@use_args({
    "id": fields.Str(location="query", missing=""),
    "handle": fields.Str(location="query", missing="")
})
def get(args: dict):
    # We need something to search by
    if not args["id"] and not args["handle"]:
        return make_error_response(
            "Either a Host id or handle must be provided!",
            422
        )

    # Both a host ID and handle cannot be provided
    if args["id"] and args["handle"]:
        return make_error_response(
            "Providing a Host id and handle is not allowed!",
            422
        )

    # Get the host information
    host = database.host_get(uid=args["id"], handle=args["handle"])
    if host:
        return make_response(jsonify(host), 200)

    # We don't have that host
    given_param = [(k, v) for k, v in args.items() if v][0]
    return make_error_response(
        f"Unable to get details for Host {given_param[0]} {given_param[1]}!",
        404
    )


@host.route("/date/", methods=["GET"])
@use_args({
    "date": fields.DateTime(location="query", required=True)
})
def get_date(args: dict):
    # We want the host for a given month
    host = database.host_get_by_date(args["date"].strftime("%Y-%m"))
    if not host:
        return make_response(jsonify(host), 200)
    return make_error_response("Unable to get Host details!", 404)


@host.route("/", methods=["POST"])
@use_args({
    "handle": fields.Str(
        location="json",
        required=True
    ),
    "date": fields.DateTime(
        location="json",
        required=True
    )
})
def post(args: dict):
    # TODO Create a single host with all their details
    # TODO Need to pull Twitter API to get the uid from handle
    result = True
    if result:
        return make_response({}, 201)
    return make_error_response("Unable to create a new Host!", 503)
