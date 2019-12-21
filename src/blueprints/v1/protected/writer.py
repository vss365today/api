from flask import jsonify

from webargs import fields
from webargs.flaskparser import use_args

from src.blueprints import writer
from src.core import database
from src.core.helpers import make_response, make_error_response


@writer.route("/", methods=["GET"])
@use_args({
    "id": fields.Str(location="query"),
    "handle": fields.Str(location="query")
})
def get(args: dict):
    if "id" in args and "handle" in args:
        return make_error_response(
            "Providing a Writer id and handle is not allowed!",
            422
        )

    # TODO Get the details for a single writer
    # result = True
    # if result:
    #     return make_response({}, 201)
    return make_error_response("Unable to get details for Writer <id/handle>!", 503)


@writer.route("/date", methods=["GET"])
@use_args({
    "date": fields.DateTime(
        "%Y-%m-%d",
        location="query",
        required=True
    )
})
def get_date(args: dict):
    # We want the Writer for a given month
    if (writer := database.get_writers_by_date(args["date"].strftime("%Y-%m"))):  # noqa
        return make_response(jsonify(writer), 200)
    return make_error_response("Unable to get Writer details!", 503)


@writer.route("/", methods=["POST"])
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
    # TODO Create a single writer with all their details
    # TODO Need to pull Twitter API to get the uid from handle
    result = True
    if result:
        return make_response({}, 201)
    return make_error_response("Unable to create a new Writer!", 503)
