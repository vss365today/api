from typing import Any

from flask.views import MethodView
from flask_smorest import abort

import src.core.database.v2 as db
from src.blueprints import prompts
from src.core.auth_helpers_v2 import require_permission
from src.core.models.v2 import Generic
from src.core.models.v2 import Prompts as models


@prompts.route("/")
class Prompt(MethodView):
    @require_permission("prompts")
    @prompts.response(200, models.Prompt(many=True))
    def get(self):
        """Get the Prompt(s) for the current day.

        The current day is defined as the latest day recorded in the database.
        It would be helpful to think of it as "the latest or newest Prompt(s)."

        This endpoint will not expose any future Prompts that may be recorded
        but not yet released.

        Special care should be taken to recognize multiple possible
        prompts being provided when consuming this endpoint.
        Historically, and as late as 2020, multiple Prompts could be
        and occasionally were given out on the same day. Even the 2021+ charter
        does not mention nor forbid multiple Prompts on the same day, though
        that is frowned upon and understood to not happen.

        Nevertheless, in lieu of a formal declaration, this endpoint will provide
        all Prompts recorded for the current day. In practice, there should only be
        one Prompt. Regardless, consumers should take care to handle multiple Prompts.
        """
        return db.prompts.get_current()

    @require_permission("prompts")
    @prompts.arguments(models.Prompt, location="json", as_kwargs=True)
    @prompts.response(201, models.Prompt)
    @prompts.alt_response(403, schema=Generic.HttpError)
    @prompts.alt_response(422, schema=Generic.HttpError)
    @prompts.alt_response(500, schema=Generic.HttpError)
    def post(self, **kwargs: dict[str, Any]):
        """Create a new Prompt.

        By default, recording a Prompt for day that already has a Prompt is forbidden
        unless the `is_additional` property is `true`.
        This should not happen under the 2021+ charter, but, as with the other
        endpoints, such a possibility is not explicitly forbidden,
        meaning the scenario is supported at a technical level.

        * **Permission Required**: `has_prompts`
        """
        # Unless specifically stated, we do not allow
        # creating  multiple Prompts for a single day
        if not kwargs.pop("is_additional"):
            if db.prompts.exists(kwargs["date"]):
                # TODO: Figure out how to put this message in the response
                # https://github.com/marshmallow-code/flask-smorest/blob/53001cf2308acd123bd3d274d3c00aaa75526129/tests/test_error_handler.py
                abort(
                    422,
                    message="Multiple Prompts cannot be created for a single day.",
                )

        # If we can't create the Prompt, error
        if (prompt := db.prompts.create(kwargs)) is None:
            abort(500, message="Unable to create Prompt for this day.")
        return prompt


@prompts.route("/<int:id>")
class PromptAlter(MethodView):
    @require_permission("prompts")
    @prompts.arguments(models.PromptId, location="path", as_kwargs=True)
    @prompts.arguments(models.PromptUpdate, location="json", as_kwargs=True)
    @prompts.response(204, schema=Generic.Empty)
    @prompts.alt_response(403, schema=Generic.HttpError)
    @prompts.alt_response(500, schema=Generic.HttpError)
    def patch(self, **kwargs: dict[str, Any]):
        """Update an existing Prompt.

        Providing a Host handle different from the current Host will associate
        the Prompt with the new Host. The new Host must already exist.
        It will not be created automatically.

        * **Permission Required**: `has_prompts`
        """
        if not db.prompts.update(kwargs):
            return abort(500)

    @require_permission("prompts")
    @prompts.arguments(models.PromptId, location="path", as_kwargs=True)
    @prompts.response(204, schema=Generic.Empty)
    @prompts.alt_response(403, schema=Generic.HttpError)
    @prompts.alt_response(404, schema=Generic.HttpError)
    def delete(self, **kwargs: dict[str, Any]):
        """Delete an existing Prompt.

        This will also delete any and all associated media record and files.

        * **Permission Required**: `has_prompts`
        """
        if not db.prompts.delete(kwargs["id"]):
            abort(404)


@prompts.route("/date/<string:date>")
class PromptDate(MethodView):
    @prompts.arguments(models.PromptDate, location="path", as_kwargs=True)
    @prompts.response(200, models.Prompt(many=True))
    @prompts.alt_response(404, schema=Generic.HttpError)
    def get(self, **kwargs: dict[str, Any]):
        """Get the Prompt(s) for a date.

        Special care should be taken to recognize multiple possible
        prompts being provided when consuming this endpoint.
        Historically, and as late as 2020, multiple Prompts could be
        and occasionally were given out on the same day. Even the 2021+ charter
        does not mention nor forbid multiple Prompts on the same day, though
        that is frowned upon and understood to not happen.

        As a result, this endpoint will provide all Prompts recorded for the given day,
        though for the vast majority of dates, there should only be one Prompt.

        This endpoint will not expose any future Prompts that may be recorded
        but not yet released.
        """
        if not (prompts := db.prompts.get_by_date(kwargs["date"])):
            abort(404)
        return prompts


@prompts.route("/<int:id>/media/")
class MediaCreate(MethodView):
    @require_permission("prompts")
    @prompts.arguments(models.PromptId, location="path", as_kwargs=True)
    @prompts.arguments(models.MediaItems, location="json", as_kwargs=True)
    @prompts.response(201, schema=Generic.Empty)
    @prompts.alt_response(403, schema=Generic.HttpError)
    @prompts.alt_response(404, schema=Generic.HttpError)
    def post(self, **kwargs: dict[str, Any]):
        """Create a Prompt Media record.

        * **Permission Required**: `has_prompts`
        """
        if not db.prompts.create_media(kwargs["id"], kwargs["items"]):
            abort(404)


@prompts.route("/<int:id>/media/<int:media_id>")
class MediaDelete(MethodView):
    @require_permission("prompts")
    @prompts.arguments(models.MediaDelete, location="path", as_kwargs=True)
    @prompts.response(204, schema=Generic.Empty)
    @prompts.alt_response(403, schema=Generic.HttpError)
    @prompts.alt_response(404, schema=Generic.HttpError)
    def delete(self, **kwargs: dict[str, Any]):
        """Delete an existing Prompt Media record.

        * **Permission Required**: `has_prompts`
        """
        if not db.prompts.delete_media(kwargs):
            abort(404)
