from flask.views import MethodView
from flask_smorest import abort

from src.blueprints import notifications
from src.configuration import get_config
from src.core.models.v2 import Generic, Notification as models


@notifications.route("/")
class Notification(MethodView):
    @notifications.arguments(models.NotificationDate, location="query", as_kwargs=True)
    @notifications.response(204, Generic.Empty)
    @notifications.alt_response(403, schema=Generic.HttpError)
    @notifications.alt_response(422, schema=Generic.HttpError)
    def post(self, **kwargs: str):
        """Send out an email notification for a given date.

        If email sending is not enabled, a successful response will be given
        without attempting to actually send any emails.
        """
        # If email sending is not enabled, just pretend it worked
        if not get_config("ENABLE_EMAIL_SENDING"):
            return

        date = kwargs["date"]
        abort(422, message=f"Unable to send email notification for the {date} Prompt!")
