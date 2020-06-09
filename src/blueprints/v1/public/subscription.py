from webargs import fields
from webargs.flaskparser import use_args

from src.blueprints import subscription
from src.core import database, helpers
from src.core.email import mailgun


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
