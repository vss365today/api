from flask import jsonify

from webargs import fields
from webargs.flaskparser import use_args

from src.blueprints import subscription
from src.core import database
from src.core.helpers import make_response, make_error_response


# TODO This needs to be protected via @authorize_route
@subscription.route("/", methods=["GET"])
def get():
    mailing_list = database.subscription_list_get()
    if mailing_list:
        return make_response(jsonify(mailing_list), 200)
    return make_error_response("Unable to get mailing list!", 503)


@subscription.route("/", methods=["POST"])
@use_args({
    "email": fields.Email(
        location="query",
        required=True
    )
})
def post(args: dict):
    result = database.subscription_email_create(args["email"])
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
    database.subscription_email_delete(args["email"])
    return make_response({}, 204)
