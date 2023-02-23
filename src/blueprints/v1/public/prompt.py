from datetime import datetime, timedelta
from typing import Literal, Optional, Union

from flask import jsonify
from webargs import fields
from webargs.flaskparser import use_args

from src.blueprints import prompt
from src.core import database, helpers
from src.core.auth_helpers import authorize_route
from src.core.helpers import media


def prompt_exists(
    today: datetime, direction: Union[Literal["previous"], Literal["next"]]
) -> Optional[datetime]:
    """Determine if there's a Prompt for the surrounding date."""
    # Get the proper surrounding date
    if direction == "previous":
        diff = today - timedelta(1)
    elif direction == "next":
        diff = today + timedelta(1)
    else:
        return None

    # Special one year anniversary case
    if diff.year == 2017 and diff.month == 9 and diff.day == 5:
        return diff

    # Check the database for a Prompt
    if database.prompt.get_by_date(helpers.format_datetime_ymd(diff)):
        return diff
    return None


@prompt.get("/")
@use_args({"date": fields.DateTime()}, location="query")
def get(args: dict):
    """Get a Prompt, either the latest or from a specific date."""
    # Hitting the endpoint without a date returns the latest prompt(s)
    if "date" not in args:
        prompts = database.prompt.get_latest()

    # We want the prompt from a particular day
    else:
        # Handle the special one year anniversary image prompts
        if (
            args["date"].year == 2017
            and args["date"].month == 9
            and args["date"].day == 5
        ):
            return database.prompt.get_one_year()

        # Format the date in the proper format before fetching
        date = helpers.format_datetime_ymd(args["date"])

        # A prompt for that date doesn't exist
        prompts = database.prompt.get_by_date(date, date_range=False)
        if not prompts:
            return helpers.make_error_response(
                404, f"No prompt exists for date {date}!"
            )

    # Find out if we have a Prompt for the surrounding days
    for day_prompt in prompts:
        day_prompt["previous"] = prompt_exists(day_prompt.date, "previous")
        day_prompt["next"] = prompt_exists(day_prompt.date, "next")
    return jsonify(prompts)


@authorize_route
@prompt.post("/")
@use_args(
    {
        "id": fields.String(required=True),
        "uid": fields.String(required=True),
        "date": fields.DateTime(required=True),
        "word": fields.String(required=True),
        "content": fields.String(required=True),
        "media": fields.String(missing=None, allow_none=True),
        "media_alt_text": fields.String(missing=None, allow_none=True),
        "is_duplicate_date": fields.Boolean(required=False, missing=False),
    },
    location="json",
)
def post(args: dict):
    """Create a new Prompt."""
    # Format the date in the proper format before writing
    args["date"] = helpers.format_datetime_ymd(args["date"])

    # If we've not received an explicit flag that this a duplicate data
    # (which can occur because there happened to more >1 prompt for the day),
    # we need to enforce a one-prompt-a-day constraint
    if not args["is_duplicate_date"]:
        # Don't create a prompt if it already exists
        if database.prompt.exists(pid="", date=args["date"]):
            return helpers.make_error_response(
                422, f"A prompt for {args['date']} already exists!"
            )

    # Download the given media
    media_result = True
    if args["media"] is not None and media.is_valid_url(args["media"]):
        media_url = args["media"]
        media_result = media.move(media.download(args["id"], media_url))

        # Extract the media URL
        args["media"] = media.saved_name(args["id"], media_url)

    # Write the prompt to the database
    db_result = database.prompt.create(args)

    # Return the proper status depending on adding result
    if db_result and media_result:
        return helpers.make_response(201)
    return helpers.make_error_response(422, "Unable to record new Prompt!")


@authorize_route
@prompt.put("/")
@use_args({"id": fields.String(required=True)}, location="query")
@use_args(
    {
        "date": fields.DateTime(required=True),
        "word": fields.String(required=True),
        "content": fields.String(required=True),
        "media": fields.String(missing=None, allow_none=True),
        "media_alt_text": fields.String(missing=None, allow_none=True),
        "media_replace": fields.Boolean(required=False, missing=False),
    },
    location="json",
)
def put(query_args: dict, json_args: dict):
    """Update an existing Prompt."""
    # Merge the two args dicts into a single dict for easier use
    args = {**query_args, **json_args}

    # The prompt needs to exist first
    if not database.prompt.exists(pid=args["id"], date=""):
        msg = "The prompt ID '{}' does not exist!".format(args["id"])
        return helpers.make_error_response(404, msg)

    # If media is set to nothing, we want to delete it
    if args["media"] is None:
        media.delete(args["id"])

    # We want to replace the existing media
    elif (
        args["media"] is not None
        and media.is_valid_url(args["media"])
        and args["media_replace"]
    ):
        # Start by deleting the old media
        media.delete(args["id"])

        # Download the new media
        media.move(media.download(args["id"], args["media"]))

        # Set the new media file name. It's not likely to be different
        # but better safe than sorry here
        args["media"] = media.saved_name(args["id"], args["media"])

    # Format the date in the proper format
    args["date"] = helpers.format_datetime_ymd(args["date"])

    # Finally, save all this to the database
    database.prompt.update(args)
    return helpers.make_response(204)


@authorize_route
@prompt.delete("/")
@use_args({"id": fields.String(required=True)}, location="query")
def delete(args: dict):
    """Delete an existing Prompt."""
    # Going to mimic SQL's behavior and pretend
    # we deleted something even if we didn't
    media.delete(args["id"])
    database.prompt.delete(args["id"])
    return helpers.make_response(204)
