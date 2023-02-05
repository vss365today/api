from flask.views import MethodView
from flask_smorest import abort

import src.core.database.v2 as db
from src.blueprints import prompts
from src.core.auth_helpers import authorize_route_v2
from src.core.models.v2 import Generic, Prompts as models


@prompts.route("/")
class Prompt(MethodView):
    @authorize_route_v2
    def post(self):
        """Create a new Prompt.

        * **Permission Required**: `has_prompts`
        """
        ...

    @authorize_route_v2
    def patch(self):
        """Update an existing Prompt.

        * **Permission Required**: `has_prompts`
        """
        ...

    @authorize_route_v2
    def delete(self):
        """Delete an existing Prompt.

        * **Permission Required**: `has_prompts`
        """
        ...


@prompts.route("/current")
class PromptCurrent(MethodView):
    def get(self):
        """Get the current Prompt."""
        ...


@prompts.route("/<string:date>")
class PromptDate(MethodView):
    def get(self):
        """Get the Prompt(s) for a date."""
        ...
