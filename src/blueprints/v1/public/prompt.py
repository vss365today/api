from flask import Blueprint
from flask import abort, jsonify

from webargs import fields
from webargs.flaskparser import use_args

from src.blueprints import prompt
from src.core import database
from src.core.helpers import make_error_response


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
        if (prompt := database.get_prompt_by_date(date)):  # noqa
            return jsonify(prompt)

    # Hitting the endpoint without a date returns the latest prompt
    return jsonify(database.get_latest_prompt())


@prompt.route("/", methods=["POST"])
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
    return {}, status_code


@prompt.route("/", methods=["PUT"])
@use_args({
    "tweet_id": fields.Str(location="query", required=True),
    "content": fields.Str(location="json", required=True),
    "word": fields.Str(location="json", required=True),
    "media": fields.Str(location="json", missing=None),
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
    return {}, 204


@prompt.route("/", methods=["DELETE"])
@use_args({
    "tweet_id": fields.Str(location="query", required=True)
})
def delete(args: dict):
    # Going to mimic SQL's behavior and pretend we deleted something
    # even if we really didn't
    database.delete_prompt(args["tweet_id"])
    return {}, 204


@prompt.route("/years", methods=["GET"])
def get_years():
    """Get the years of recorded prompts."""
    return jsonify(database.get_prompt_years())
