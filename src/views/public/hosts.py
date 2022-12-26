from flask.views import MethodView
from flask_smorest import abort

from src.blueprints import hosts
from src.configuration import get_config
from src.core.database.v2 import hosts as db
from src.core.models.v2 import Generic, Hosts as models


@hosts.route("/current/")
class HostCurrent(MethodView):
    @hosts.response(200, models.Basic)
    @hosts.alt_response(404, schema=Generic.HttpError)
    def get(self):
        """Get the current Host for the current Hosting period."""
        if host := db.current_host():
            return host
        abort(404)
