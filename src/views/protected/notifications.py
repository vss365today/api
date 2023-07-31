from datetime import date
from typing import Any, cast

from flask import current_app
from flask.views import MethodView
from flask_smorest import abort

import src.core.database.v2 as db
from src.configuration import get_config
from src.core import email, helpers
from src.core.database.models import Prompt
from src.core.email import mailgun
from src.core.models.v2 import Generic
from src.core.models.v2 import Notification as models
from src.views import notifications


@notifications.route("/<string:date>")
class Notification(MethodView):
    @notifications.arguments(models.Date, location="path", as_kwargs=True)
    @notifications.arguments(models.Which, location="query", as_kwargs=True)
    @notifications.response(204, Generic.Empty)
    @notifications.alt_response(403, schema=Generic.HttpError)
    @notifications.alt_response(404, schema=Generic.HttpError)
    @notifications.alt_response(422, schema=Generic.HttpError)
    def post(self, **kwargs: Any):
        """Send out an email notification for a given date.

        If email sending is not enabled, a successful response will be given
        without attempting to actually send any emails.

        The option to select which Prompt should be sent out is available
        in the case of days that have multiple Prompts recorded. By default,
        the newest recorded Prompt will be selected.

        * **Permission Required**: `has_notifications`
        """
        # If email sending is not enabled, just pretend it worked
        if not get_config("ENABLE_EMAIL_SENDING"):
            return None

        # We can't sent out emails for a Prompt that does not exist
        # (or shouldn't exist yet)
        if not (prompt := db.prompts.get_by_date(kwargs["date"])):
            abort(
                404, message=f"Unable to find Prompt for {kwargs['date'].isoformat()}."
            )

        # Using our `which` parameter, select the Prompt that should be sent out.
        # This supports our rare but possible multiple Prompts per day scenario
        # while also correctly handling a single Prompt on a given day.
        # We also we don't want to attempt to select a Prompt
        # that is beyond how many we actually have
        prompt_to_select = kwargs["which"]
        num_of_prompts = len(prompt)
        if prompt_to_select != 1 and prompt_to_select > num_of_prompts:
            abort(
                422,
                message=(
                    f"Cannot select Prompt #{prompt_to_select} out of"
                    f" {num_of_prompts} total."
                ),
            )
        prompt = cast(Prompt, prompt[prompt_to_select])

        # Build up the email render information. Our custom `as_dict()` method
        # doesn't follow FKs or hybrid properties, so we have to take care
        # to add that information ourselves
        render_opts = {**prompt.as_dict()}
        render_opts["url"] = prompt.url
        render_opts["host_handle"] = prompt.host.handle
        render_opts["file"] = prompt.media[0].file if prompt.media else None

        # Because of the Twitter/X API paywall that went online June 9/10 2023,
        # all email sending immediately ceased. Access was not restored until late July,
        # meaning nothing sent for nearly 2 months. Email, however, is picky, and sending out
        # to 700+ addresses all at once will almost certainly cause all of them + my IP +
        # email reputation to be blocked and sunk. To combat that, I need to gradually send them
        # back up until I'm sending all 700+ again. To do this, I've picked a date to start sending
        # them again (except one day before to prevent multiplication by zero), then taking the
        # number of days since and multiplying it by a constant. Once I get back to sending all
        # 700+, I'll switch back to the mailing list
        day_emails_started_back = date(2023, 7, 28)
        days_since_start = (date.today() - day_emails_started_back).days
        total_emails_to_send_to = days_since_start * 20
        emails = db.emails.get_emails_totalling(total_emails_to_send_to)
        current_app.logger.debug(f"Sending out {total_emails_to_send_to} emails...")
        for addr in emails:
            email.make_and_send(
                addr.address,
                helpers.format_datetime_pretty(prompt.date),
                "email",
                **render_opts,
            )

        # Send an email to the Mailgun-hosted mailing list. This helps us keep track
        # of who is on the list at any given moment but also resolves a crazy amount of trouble
        # when it comes to sending out a large amount of email messages.
        # TODO: Switch back to this once I'm sending out the whole list using the code above
        # https://documentation.mailgun.com/en/latest/api-mailinglists.html#examples
        # email.make_and_send(
        #     mailgun.mailing_list(),
        #     helpers.format_datetime_pretty(prompt.date),
        #     "email",
        #     **render_opts,
        # )
