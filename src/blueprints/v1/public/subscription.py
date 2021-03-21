from flask import current_app
from requests import codes
from webargs import fields
from webargs.flaskparser import use_args

from src.blueprints import subscription
from src.core import database, helpers
from src.core.auth_helpers import authorize_route
from src.core.email import mailgun


@subscription.route("/", methods=["POST"])
@use_args({"email": fields.Email(required=True)}, location="query")
def post(args: dict):
    """Add an email to the mailing list."""
    # Define the error response
    error = helpers.make_error_response(503, "Unable to add email to mailing list!")

    # Because this endpoint costs money with each hit, block it off
    # if we're not planning on sending out any emails
    if current_app.config["ENABLE_EMAIL_SENDING"]:
        # Validate the address to decide if we should record it
        if not mailgun.validate_email_address(args["email"]):
            return error

    # Add the address to the local database
    db_result = database.subscription.email_create(args["email"])

    # It didn't added to the db
    if not db_result:
        return error

    # Add the address to the Mailgun mailing list
    mg_result = mailgun.subscription_email_create(args["email"])

    # The address was successfully recorded
    if mg_result.status_code == codes.ok:
        return helpers.make_response(201)

    # ...Welllllll... actually it didn't...
    return error


@authorize_route
@subscription.route("/", methods=["DELETE"])
@use_args({"email": fields.Email(required=True)}, location="query")
def delete(args: dict):
    """Remove an email from the mailing list."""
    mailgun.subscription_email_delete(args["email"])
    database.subscription.email_delete(args["email"])
    return helpers.make_response(204)
