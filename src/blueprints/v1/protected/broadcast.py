from pprint import pprint

from flask import current_app
from webargs import fields
from webargs.flaskparser import use_args

from src.blueprints import broadcast
from src.core import database, email, helpers
from src.core.email import mailgun


@broadcast.route("/", methods=["POST"])
@use_args(
    {"date": fields.DateTime(required=True), "which": fields.Integer(missing=-1)},
    location="query",
)
def post(args: dict):
    """Trigger an email broadcast for the given day's prompt."""
    # Put the date in the proper format
    date = helpers.format_datetime_ymd(args["date"])

    # A prompt for that date doesn't exist
    prompts = database.prompt.get_by_date(date, date_range=False)
    if not prompts:
        return helpers.make_error_response(
            503, f"Unable to send out email broadcast for the {date} prompt!"
        )

    # If email sending is not allowed, just pretend it worked
    if not current_app.config["ENABLE_EMAIL_SENDING"]:
        return helpers.make_response(200)

    # Pull out the exact prompt we want to broadcast.
    # If there's more than one prompt for this day,
    # it'll use whichever was requested.
    # By default, the latest recorded/only prompt is selected
    prompt = prompts[args["which"]]

    # Send an email to the MG mailing list
    # This helps us keep track of who is on the list at any given moment
    # but also resolves a crazy amount of trouble
    # when it comes to sending out a large amount of email messages
    # https://documentation.mailgun.com/en/latest/api-mailinglists.html#examples
    r = email.make_and_send(
        mailgun.mailing_list_addr_get(),
        helpers.format_datetime_pretty(prompt.date),
        "email",
        **prompt,
    )
    pprint(r)

    # There's no easy way to tell if they all sent, so just pretend they did
    return helpers.make_response(200)
