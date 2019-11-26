from flask import Blueprint
from flask import abort, jsonify

from webargs import fields
from webargs.flaskparser import use_args

from src.core import database


bp = Blueprint("prompt", __name__, url_prefix="/prompt")


@bp.route("/", methods=["GET"])
@use_args({
    "date": fields.Date(
        "%Y-%m-%d",
        location="query",
        required=True
    )
})
def get(args: dict):
    # Format the date in the proper format before fetching
    date = args["date"].isoformat()

    # If we have a prompt, return it
    # Sweet Python 3.8+ walrus operator usage :D
    if (prompt := database.get_prompt_by_date(date)):  # noqa
        return jsonify(prompt)

    # Default to a not found response
    return abort(404)


@bp.route("/", methods=["POST"])
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


@bp.route("/", methods=["PUT"])
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
    if not database.find_existing_prompt(args["tweet_id"]):
        return {"error_msg": "The given tweet ID does not exist."}, 422

    # Format the date in the proper format before writing
    args["date"] = args["date"].isoformat()
    result = database.update_prompt(args)

    # Return the proper status depending on adding result
    status_code = 204 if result else 422
    return {}, status_code


@bp.route("/years", methods=["GET"])
def get_years():
    """Get the years of recorded prompts."""
    return jsonify(database.get_prompt_years())
