from pprint import pprint

from flask import jsonify
from webargs import fields
from webargs.flaskparser import use_args

from src.blueprints import subscription
from src.core import database, email, helpers
from src.core.email import mailgun


# TODO This needs to be protected via @authorize_route
@subscription.route("/", methods=["GET"])
def get():
    """Retrieve the entire mailing list."""
    mailing_list = database.subscription_list_get()
    if mailing_list:
        return helpers.make_response(200, jsonify(mailing_list))
    return helpers.make_error_response(503, "Unable to get mailing list!")


@subscription.route("/", methods=["POST"])
@use_args({"email": fields.Email(required=True)}, location="query")
def post(args: dict):
    """Add an email to the mailing list."""
    mailgun.subscription_email_create(args["email"])
    db_result = database.subscription_email_create(args["email"])
    if db_result:
        return helpers.make_response(201)
    return helpers.make_error_response(503, "Unable to add email to mailing list!")


@subscription.route("/", methods=["DELETE"])
@use_args({"email": fields.Email(required=True)}, location="query")
def delete(args: dict):
    """Remove an email from the mailing list."""
    mailgun.subscription_email_delete(args["email"])
    database.subscription_email_delete(args["email"])
    return helpers.make_response(204)


# TODO This needs to be protected via @authorize_route
@subscription.route("/broadcast/", methods=["POST"])
@use_args({"date": fields.DateTime()}, location="query")
def broadcast(args: dict):
    """Trigger an email broadcast for the given day's prompt."""
    # Put the date in the proper format
    date = helpers.format_datetime_iso(args["date"])

    # A prompt for that date doesn't exist
    prompt = database.prompts_get_by_date(date, date_range=False)
    if not prompt:
        return helpers.make_error_response(
            503, f"Unable to send out email broadcast for the {date} prompt!"
        )

    # Construct the mailing list address. It is written this way
    # because the development and production lists are different
    # and we need to use the proper one depending on the env
    mg_list_addr = mailgun.mailing_list_addr_get()

    # Send an email to the MG mailing list
    # This helps us keep track of who is on the list at any given moment
    # but also resolves a crazy amount of trouble
    # when it comes to sending out a large amount of email messages
    # https://documentation.mailgun.com/en/latest/api-mailinglists.html#examples
    r = email.make_and_send(
        mg_list_addr,
        helpers.format_datetime_pretty(prompt[0].date),
        "email",
        **prompt[0],
    )
    pprint(r)

    # There's no easy way to tell if they all sent, so just pretend they did
    # TODO No easy way until I add some number tracking, that is
    return helpers.make_response(200)
