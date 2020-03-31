from flask import jsonify

from webargs import fields
from webargs.flaskparser import use_args

from src.blueprints import broadcast
from src.core import database
from src.core.helpers import make_response, make_error_response


# TODO This needs to be protected via @authorize_route
@broadcast.route("/", methods=["POST"])
@use_args({
    "date": fields.DateTime(location="query")
})
def post(args: dict):
    """Trigger an email broadcast for the given day's prompt."""
    mailing_list = database.subscription_list_get()
    if mailing_list:
        return make_response({}, 201)

    # We couldn't send the broadcast :(
    return make_error_response(
        f"Unable to send email broadcast for date {args['date']}!",
        503
    )
