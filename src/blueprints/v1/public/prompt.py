from datetime import date, timedelta
from typing import Optional

from flask import Blueprint
from flask import abort, jsonify

from webargs import fields
from webargs.flaskparser import use_args

from src.blueprints import prompt
from src.core.auth_helpers import authorize_route
from src.core import database
from src.core.helpers import make_response, make_error_response
from src.core.models.v1.Prompt import Prompt


def prompt_yesterday_exists(prompt: Prompt) -> Optional[str]:
    yesterday_date = (prompt.date - timedelta(1)).isoformat()
    r = database.get_prompt_by_date(yesterday_date)

    if database.get_prompt_by_date(yesterday_date):
        return yesterday_date
    return None


def prompt_tomorrow_exists(prompt: Prompt) -> Optional[str]:
    tomorrow_date = (prompt.date + timedelta(1)).isoformat()
    r = database.get_prompt_by_date(tomorrow_date)

    if database.get_prompt_by_date(tomorrow_date):
        return tomorrow_date
    return None


@prompt.route("/", methods=["GET"])
@use_args({
    "date": fields.Date(
        "%Y-%m-%d",
        location="query",
        missing=None
    )
})
def get(args: dict):
    # We want the prompt from a particular day
    if args["date"] is not None:
        # Format the date in the proper format before fetching
        date = args["date"].isoformat()

        # If we have a prompt, return it
        # Sweet Python 3.8+ walrus operator usage :D
        if (prompts := database.get_prompt_by_date(date)):  # noqa
            # Find out if we have a prompt for tomorrow or yesterday
            for prompt in prompts:
                prompt["previous_day"] = prompt_yesterday_exists(prompt)
                prompt["next_day"] = prompt_tomorrow_exists(prompt)
            return jsonify(prompts)

        # A prompt for that date doesn't exisd
        else:
            return make_error_response(
                f"No prompt exists for date {date}!",
                404
            )

    # Hitting the endpoint without a date returns the latest prompt
    latest_prompt = database.get_latest_prompt()[0]
    latest_prompt["previous_day"] = prompt_yesterday_exists(latest_prompt)
    latest_prompt["next_day"] = None
    return jsonify([latest_prompt])


@prompt.route("/", methods=["POST"])
@authorize_route
@use_args({
    "tweet_id": fields.Str(location="json", required=True),
    "uid": fields.Str(location="json", required=True),
    "content": fields.Str(location="json", required=True),
    "word": fields.Str(location="json", required=True),
    "media": fields.Str(location="json", missing=None),
    "date": fields.Date(
        "%Y-%m-%d",
        location="json",
        required=True
    )
})
def post(args: dict):
    # Format the date in the proper format before writing
    args["date"] = args["date"].isoformat()
    result = database.create_prompt(args)

    # Return the proper status depending on adding result
    status_code = 201 if result else 422
    return make_response({}, status_code)


@prompt.route("/", methods=["PUT"])
@authorize_route
@use_args({
    "tweet_id": fields.Str(location="query", required=True),
    "content": fields.Str(location="json", required=True),
    "word": fields.Str(location="json", required=True),
    "media": fields.Str(location="json", required=True),
    "date": fields.Date(
        "%Y-%m-%d",
        location="json",
        required=True
    )
})
def put(args: dict):
    # The prompt needs to exist first
    if not database.find_existing_prompt(args["tweet_id"]):
        msg = "The prompt ID '{}' does not exist.".format(args["tweet_id"])
        return make_error_response(msg, 422)

    # Format the date in the proper format before writing
    args["date"] = args["date"].isoformat()
    database.update_prompt(args)
    return make_response({}, 204)


@prompt.route("/", methods=["DELETE"])
@use_args({
    "tweet_id": fields.Str(location="query", required=True)
})
def delete(args: dict):
    # Going to mimic SQL's behavior and pretend we deleted something
    # even if we really didn't
    database.delete_prompt(args["tweet_id"])
    return make_response({}, 204)
