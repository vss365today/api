from datetime import timedelta
from typing import Optional

from flask import jsonify

from webargs import fields
from webargs.flaskparser import use_args

from src.blueprints import prompt
from src.core import database
from src.core.helpers import (
    date_iso_format,
    make_response,
    make_error_response
)
from src.core.models.v1.Prompt import Prompt


def prompt_yesterday_exists(prompt: Prompt) -> Optional[str]:
    yesterday_date = date_iso_format(prompt.date - timedelta(1))
    if database.prompts_get_by_date(yesterday_date):
        return yesterday_date
    return None


def prompt_tomorrow_exists(prompt: Prompt) -> Optional[str]:
    tomorrow_date = date_iso_format(prompt.date + timedelta(1))
    if database.prompts_get_by_date(tomorrow_date):
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
        date = date_iso_format(args["date"])

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
            return make_error_response(
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
    "tweet_id": fields.Str(location="json", required=True),
    "uid": fields.Str(location="json", required=True),
    "content": fields.Str(location="json", required=True),
    "word": fields.Str(location="json", required=True),
    "media": fields.Str(location="json", missing=None),
    "date": fields.DateTime(location="json", required=True)
})
def post(args: dict):
    # Format the date in the proper format before writing
    args["date"] = date_iso_format(args["date"])

    # Don't create a prompt if it already exists
    if database.prompt_find_existing(args["tweet_id"]):
        return make_error_response(
            f"A prompt for {args['date']} already exists!",
            422
        )

    # Return the proper status depending on adding result
    result = database.prompt_create(args)
    status_code = 201 if result else 422
    return make_response({}, status_code)


# TODO This needs to be protected via @authorize_route
@prompt.route("/", methods=["PUT"])
@use_args({
    "tweet_id": fields.Str(location="query", required=True),
    "content": fields.Str(location="json", required=True),
    "word": fields.Str(location="json", required=True),
    "media": fields.Str(location="json", missing=None),
    "date": fields.DateTime(location="json", required=True)
})
def put(args: dict):
    # The prompt needs to exist first
    if not database.prompt_find_existing(args["tweet_id"]):
        msg = "The prompt ID '{}' does not exist!".format(args["tweet_id"])
        return make_error_response(msg, 422)

    # Format the date in the proper format before writing
    args["date"] = date_iso_format(args["date"])
    database.prompt_update(args)
    return make_response({}, 204)


@prompt.route("/", methods=["DELETE"])
@use_args({
    "tweet_id": fields.Str(location="query", required=True)
})
def delete(args: dict):
    # Going to mimic SQL's behavior and pretend we deleted something
    # even if we really didn't
    database.prompt_delete(args["tweet_id"])
    return make_response({}, 204)
