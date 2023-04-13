from typing import Any, cast

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
            return True

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
                message=f"Cannot select Prompt #{prompt_to_select} out of {num_of_prompts} total.",
            )
        prompt = cast(Prompt, prompt[prompt_to_select])

        # Build up the email render information. Our custom `as_dict()` method
        # doesn't follow FKs or hybrid properties, # so we have to take care
        # to add that information ourselves
        render_opts = {**prompt.as_dict()}
        render_opts["url"] = prompt.url
        render_opts["media"] = prompt.media[0].media
        render_opts["host_handle"] = prompt.host.handle

        # Send an email to the Mailgun-hosted mailing list.
        # This helps us keep track of who is on the list at any given moment
        # but also resolves a crazy amount of trouble
        # when it comes to sending out a large amount of email messages
        # https://documentation.mailgun.com/en/latest/api-mailinglists.html#examples
        email.make_and_send(
            mailgun.mailing_list(),
            helpers.format_datetime_pretty(prompt.date),
            "email",
            **render_opts,
        )
