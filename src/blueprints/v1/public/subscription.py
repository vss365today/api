from flask import jsonify

from webargs import fields
from webargs.flaskparser import use_args

from src.blueprints import subscription
from src.core import database
from src.core.helpers import date_iso_format, make_response, make_error_response


# TODO This needs to be protected via @authorize_route
@subscription.route("/", methods=["GET"])
def get():
    """Retrieve the entire mailing list."""
    mailing_list = database.subscription_list_get()
    if mailing_list:
        return make_response(jsonify(mailing_list), 200)
    return make_error_response("Unable to get mailing list!", 503)


@subscription.route("/", methods=["POST"])
@use_args({"email": fields.Email(required=True)}, location="query")
def post(args: dict):
    """Add an email to the mailing list."""
    result = database.subscription_email_create(args["email"])
    if result:
        return make_response({}, 201)
    return make_error_response("Unable to add email to mailing list!", 503)


@subscription.route("/", methods=["DELETE"])
@use_args({"email": fields.Email(required=True)}, location="query")
def delete(args: dict):
    """Remove an email from the mailing list."""
    database.subscription_email_delete(args["email"])
    return make_response({}, 204)


# TODO This needs to be protected via @authorize_route
@subscription.route("/broadcast/", methods=["POST"])
@use_args({"date": fields.DateTime()}, location="query")
def broadcast(args: dict):
    """Trigger an email broadcast for the given day's prompt."""
    # Put the date in the proper format
    date = date_iso_format(args["date"])

    # A prompt for that date doesn't exist
    prompt = database.prompts_get_by_date(date, date_range=False)
    if not prompt:
        return make_error_response(
            f"Unable to send out email broadcast for the {date} prompt!", 404
        )

    # Get the mailing list
    mailing_list = database.subscription_list_get()
    if mailing_list:
        return make_response({}, 201)

    # We couldn't send the broadcast :(
    return make_error_response(
        f"Unable to send email broadcast for date {args['date']}!", 503
    )
