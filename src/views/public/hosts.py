from flask.views import MethodView
from flask_smorest import abort

from src.blueprints import hosts
from src.configuration import get_config
from src.core.database.v2 import hosts as db
from src.core.models.v2 import Generic, Hosts as models


@hosts.route("/")
class HostIndividual(MethodView):
    @hosts.arguments(models.Delete, location="query", as_kwargs=True)
    @hosts.response(201, Generic.Empty)
    @hosts.alt_response(403, schema=Generic.HttpError)
    def delete(self, args: dict[str, str]):
        """Delete a Host.

        This will only succeed if the Host does not have any
        associated Prompts to prevent orphaned or incomplete records.
        """
        abort(403)
        ...


@hosts.route("/current/")
class HostCurrent(MethodView):
    @hosts.response(200, models.Basic)
    @hosts.alt_response(404, schema=Generic.HttpError)
    def get(self):
        """Get the current Host.

        This endpoint resolves the hosting period start date automatically
        and provides the current Host for the day.
        """
        if host := db.current_host():
            return host
        abort(404)
