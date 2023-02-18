from typing import Any

from flask.views import MethodView
from flask_smorest import abort

import src.core.database.v2 as db
from src.blueprints import prompts
from src.core.auth_helpers import authorize_route_v2
from src.core.helpers import is_valid_url, media
from src.core.models.v2 import Generic
from src.core.models.v2 import Prompts as models


@prompts.route("/")
class Prompt(MethodView):
    @prompts.response(200, models.Prompt(many=True))
    def get(self):
        """Get the Prompt(s) for the current day.

        The current day is defined as the latest day recorded in the database.
        It would be helpful to think of it as "the latest or newest Prompt(s)."

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

    @authorize_route_v2
    @prompts.arguments(models.Prompt, location="json", as_kwargs=True)
    @prompts.response(201, models.Prompt)
    @prompts.alt_response(403, schema=Generic.HttpError)
    @prompts.alt_response(422, schema=Generic.HttpError)
    @prompts.alt_response(500, schema=Generic.HttpError)
    def post(self, **kwargs: Any):
        """Create a new Prompt.

        By default, recording a Prompt for day that already has a Prompt is forbidden
        unless the `is_additional` property is `true`.

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

        # Download the given media, silently discarding any invalid URLs,
        # recording if we saved each file successfully
        media_saved = []
        if kwargs["media"] is not None:
            for item in kwargs["media"]:
                # The URL to the media is invalid, throw it out
                if not is_valid_url(item["url"]):
                    continue

                # Download the media to our predefined location, and rewrite the url
                # field with just the new media file name to save to the database
                save_result = media.move(
                    media.download(kwargs["twitter_id"], item["url"])
                )
                item["url"] = media.saved_name(kwargs["twitter_id"], item["url"])
                media_saved.append(save_result)

        # If we can't create the Prompt or some of the Media didn't save, error
        if (prompt := db.prompts.create(kwargs)) is None or not all(media_saved):
            # Delete any saved media
            media.delete(kwargs["twitter_id"])
            abort(500, message="Unable to create Prompt for this day.")
        return prompt


@prompts.route("/<int:id>")
class PromptAlter(MethodView):
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

        This will also delete any associated media record and files.

        * **Permission Required**: `has_prompts`
        """
        if not db.prompts.delete(kwargs["id"]):
            abort(404)


@prompts.route("/date/<string:date>")
class PromptDate(MethodView):
    @prompts.arguments(models.PromptDate, location="path", as_kwargs=True)
    @prompts.response(200, models.Prompt(many=True))
    @prompts.alt_response(404, schema=Generic.HttpError)
    def get(self, **kwargs: Any):
        """Get the Prompt(s) for a date.

        Special care should be taken to recognize multiple possible
        prompts being provided when consuming this endpoint.
        Historically, and as late as 2020, multiple Prompts could be
        and occasionally were given out on the same day. Even the 2021+ charter
        does not mention nor forbid multiple Prompts on the same day, though
        that is frowned upon and understood to not happen.

        As a result, this endpoint will provide all Prompts recorded for the given day,
        though for the vast majority of dates, there should only be one Prompt.
        """
        if not (prompts := db.prompts.get_by_date(kwargs["date"])):
            abort(404)
        return prompts
