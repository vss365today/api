from webargs import fields
from webargs.flaskparser import use_args

from src.blueprints import writer
# from src.core import database
from src.core.helpers import make_response, make_error_response


@writer.route("/", methods=["GET"])
@use_args({
    "id": fields.Str(
        location="query",
        required=True
    )
})
def get(args: dict):
    # TODO Get the details for a single writer
    result = True
    if result:
        return make_response({}, 201)
    return make_error_response("Unable to get Writer details!", 503)


@writer.route("/", methods=["POST"])
@use_args({
    "id": fields.Str(
        location="json",
        required=True
    ),
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
    result = True
    if result:
        return make_response({}, 201)
    return make_error_response("Unable to create a new Writer!", 503)
