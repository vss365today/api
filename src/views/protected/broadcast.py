from flask.views import MethodView
from flask_smorest import abort

from src.blueprints import v2_broadcast
from src.configuration import get_config
from src.core.models.v2 import Generic
from src.core.models.v2 import Broadcast as models


@v2_broadcast.route("/")
class Broadcast(MethodView):
    @v2_broadcast.arguments(models.BroadcastDate, location="query", as_kwargs=True)
    @v2_broadcast.response(204, Generic.Empty)
    @v2_broadcast.alt_response(403, schema=Generic.HttpError)
    @v2_broadcast.alt_response(422, schema=Generic.HttpError)
    def post(self, **kwargs: str):
        """Broadcast an email notification for a given date.

        If email sending is not enabled, a successful response will be given
        without attempting to actually send any emails.
        """
        # If email sending is not enabled, just pretend it worked
        if not get_config("ENABLE_EMAIL_SENDING"):
            return

        date = kwargs["date"]
        abort(422, message=f"Unable to send out email broadcast for the {date} Prompt!")
