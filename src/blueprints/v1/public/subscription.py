from webargs import fields
from webargs.flaskparser import use_args

from src.blueprints import subscription
from src.core import database
from src.core.helpers import make_response, make_error_response


@subscription.route("/", methods=["POST"])
@use_args({
    "email": fields.Email(
        location="query",
        required=True
    )
})
def post(args: dict):
    result: bool = database.create_subscription_email(args["email"])
    if result:
        return make_response({}, 201)
    return make_error_response("Unable to add email to mailing list!", 503)


@subscription.route("/", methods=["DELETE"])
@use_args({
    "email": fields.Email(
        location="query",
        required=True
    )
})
def delete(args: dict):
    database.delete_subscription_email(args["email"])
    return make_response({}, 204)
