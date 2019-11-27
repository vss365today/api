from flask import jsonify

from webargs import fields
from webargs.flaskparser import use_args

from src.blueprints import browse
from src.core import database
from src.core.helpers import make_error_response


def browse_by_year(year: str) -> dict:

    return {}


def browse_by_month(year: str, month: str) -> dict:
    pass


@browse.route("/", methods=["GET"])
@use_args({
    "year": fields.Str(
        location="query",
        missing=None
    ),
    "month": fields.Str(
        location="query",
        missing=None
    )
})
def get(args: dict):
    # We always need a year
    if args["year"] is None:
        return make_error_response("A year must be provided!", 422)

    year: str = args["year"].strip()

    # We also have a month, meaning we're browsing an individual month
    if args["month"] is not None:
        month: str = args["month"].strip()
        return browse_by_month(year, month)

    # We only have a year, so we're browsing by year
    else:
        return browse_by_year(year)


@browse.route("/years", methods=["GET"])
def get_years():
    """Get the years of recorded prompts."""
    return jsonify(database.get_prompt_years())
