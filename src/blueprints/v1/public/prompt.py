from datetime import datetime, timedelta
from typing import Optional

from flask import jsonify

from webargs import fields
from webargs.flaskparser import use_args

from src.blueprints import prompt
from src.core import database
from src.core import helpers
from src.core.models.v1.Prompt import Prompt


def prompt_yesterday_exists(prompt: Prompt) -> Optional[datetime]:
    yesterday_date = prompt.date - timedelta(1)
    if database.prompts_get_by_date(helpers.date_iso_format(yesterday_date)):
        return yesterday_date
    return None


def prompt_tomorrow_exists(prompt: Prompt) -> Optional[datetime]:
    tomorrow_date = prompt.date + timedelta(1)
    if database.prompts_get_by_date(helpers.date_iso_format(tomorrow_date)):
        return tomorrow_date
    return None


@prompt.route("/", methods=["GET"])
@use_args({
    "date": fields.DateTime(location="query")
})
def get(args: dict):
    # We want the prompt from a particular day
    if "date" in args:
        # Format the date in the proper format before fetching
        date = helpers.date_iso_format(args["date"])

        # If we have a prompt, return it
        prompts = database.prompts_get_by_date(date, date_range=False)
        if prompts:
            # Find out if we have a prompt for tomorrow or yesterday
            for day_prompt in prompts:
                day_prompt["previous_day"] = prompt_yesterday_exists(
                    day_prompt
                )
                day_prompt["next_day"] = prompt_tomorrow_exists(
                    day_prompt
                )
            return jsonify(prompts)

        # A prompt for that date doesn't exisd
        else:
            return helpers.make_error_response(
                f"No prompt exists for date {date}!",
                404
            )

    # Hitting the endpoint without a date returns the latest prompt
    latest_prompt = database.prompt_get_latest()[0]
    latest_prompt["previous_day"] = prompt_yesterday_exists(latest_prompt)
    latest_prompt["next_day"] = None
    return jsonify([latest_prompt])


# TODO This needs to be protected via @authorize_route
@prompt.route("/", methods=["POST"])
@use_args({
    "id": fields.Str(location="json", required=True),
    "uid": fields.Str(location="json", required=True),
    "content": fields.Str(location="json", required=True),
    "word": fields.Str(location="json", required=True),
    "media": fields.Str(location="json", missing=None, allow_none=True),
    "date": fields.DateTime(location="json", required=True)
})
def post(args: dict):
    # Format the date in the proper format before writing
    args["date"] = helpers.date_iso_format(args["date"])

    # Don't create a prompt if it already exists
    if database.prompt_find_existing(pid="", date=args["date"]):
        return helpers.make_error_response(
            f"A prompt for {args['date']} already exists!",
            422
        )

    # Download the given media
    media_result = True
    if args["media"] is not None:
        media_url = args["media"]
        media_result = helpers.media_move(
            helpers.media_download(args["id"], media_url)
        )

        # Extract the media URL
        args["media"] = helpers.media_saved_name(args["id"], media_url)

    # Write the prompt to the database
    db_result = database.prompt_create(args)

    # Return the proper status depending on adding result
    status_code = 201 if db_result and media_result else 422
    return helpers.make_response({}, status_code)


# TODO This needs to be protected via @authorize_route
@prompt.route("/", methods=["PUT"])
@use_args({
    "id": fields.Str(location="query", required=True),
    "date": fields.DateTime(location="json", required=True),
    "word": fields.Str(location="json", required=True),
    "content": fields.Str(location="json", required=True),
    "media": fields.Str(location="json", missing=None, allow_none=True),
    "media_replace": fields.Bool(location="json", required=False)
})
def put(args: dict):
    # The prompt needs to exist first
    if not database.prompt_find_existing(pid=args["id"], date=""):
        msg = "The prompt ID '{}' does not exist!".format(args["id"])
        return helpers.make_error_response(msg, 422)

    # If media is set to nothing, we want to delete it
    if args["media"] is None:
        helpers.media_remove(args["id"])

    # We want to replace the existng media
    elif args["media"] is not None and args["media_replace"]:
        # Start by deleting the old media
        helpers.media_remove(args["id"])

        # Download the new media
        # We're assuming that, by virtue of a true replacement flag,
        # the media string is a URL
        helpers.media_move(
            helpers.media_download(args["id"], args["media"])
        )

        # Set the new media file name. It's not likely to be different
        # but better safe than sorry here
        args["media"] = helpers.media_saved_name(args["id"], args["media"])

    # Format the date in the proper format
    args["date"] = helpers.date_iso_format(args["date"])

    # Finally, save all this to the database
    database.prompt_update(args)
    return helpers.make_response({}, 204)


@prompt.route("/", methods=["DELETE"])
@use_args({
    "id": fields.Str(location="query", required=True)
})
def delete(args: dict):
    # Going to mimic SQL's behavior and pretend
    # we deleted somethin even if we didn't
    helpers.media_remove(args["id"])
    database.prompt_delete(args["id"])
    return helpers.make_response({}, 204)
