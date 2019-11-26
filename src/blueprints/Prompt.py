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
    "date": fields.Date(
        "%Y-%m-%d",
        location="json",
        required=True
    )
})
def post(args: dict):
    args["method"] = "POST"
    return args


@bp.route("/", methods=["PUT"])
@use_args({
    "date": fields.Date(
        "%Y-%m-%d",
        location="json",
        required=True
    )
})
def put(args: dict):
    args["method"] = "PUT"
    return args


@bp.route("/years", methods=["GET"])
def get_years():
    """Get the years of recorded prompts."""
    return jsonify(database.get_prompt_years())
