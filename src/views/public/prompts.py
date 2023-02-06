from typing import Any
from flask.views import MethodView
from flask_smorest import abort

import src.core.database.v2 as db
from src.blueprints import prompts
from src.core.auth_helpers import authorize_route_v2
from src.core.models.v2 import Generic, Prompts as models


@prompts.route("/")
class Prompt(MethodView):
    @prompts.response(200, models.Prompt(many=True))
    def get(self, **kwargs: Any):
        """Get the current Prompt(s)."""
        ...

    @authorize_route_v2
    @prompts.response(201, models.Prompt)
    @prompts.alt_response(403, schema=Generic.HttpError)
    def post(self, **kwargs: Any):
        """Create a new Prompt.

        * **Permission Required**: `has_prompts`
        """
        ...


@prompts.route("/<int:id>")
class PromptAlter(MethodView):
    @prompts.arguments(models.PromptId, location="path", as_kwargs=True)
    @prompts.response(200, models.Prompt)
    @prompts.alt_response(404, schema=Generic.HttpError)
    def get(self, **kwargs: Any):
        """Get the specified Prompt."""
        ...

    @authorize_route_v2
    @prompts.arguments(models.PromptId, location="path", as_kwargs=True)
    @prompts.response(204, schema=Generic.Empty)
    @prompts.alt_response(403, schema=Generic.HttpError)
    @prompts.alt_response(404, schema=Generic.HttpError)
    def patch(self, **kwargs: Any):
        """Update an existing Prompt.

        * **Permission Required**: `has_prompts`
        """
        ...

    @authorize_route_v2
    @prompts.arguments(models.PromptId, location="path", as_kwargs=True)
    @prompts.response(204, schema=Generic.Empty)
    @prompts.alt_response(403, schema=Generic.HttpError)
    @prompts.alt_response(404, schema=Generic.HttpError)
    def delete(self, **kwargs: Any):
        """Delete an existing Prompt.

        * **Permission Required**: `has_prompts`
        """
        if not db.prompts.delete(kwargs["id"]):
            abort(404)


@prompts.route("/date/<string:date>")
class PromptDate(MethodView):
    @prompts.arguments(models.PromptDate, location="path", as_kwargs=True)
    @prompts.response(200, models.Prompt)
    @prompts.alt_response(404, schema=Generic.HttpError)
    def get(self, **kwargs: Any):
        """Get the Prompt(s) for a date."""
        ...
