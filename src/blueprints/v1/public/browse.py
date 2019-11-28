from flask import jsonify

from webargs import fields
from webargs.flaskparser import use_args

from src.blueprints import browse
from src.core import database
from src.core.helpers import make_error_response


def __build_browse_response(writers: list) -> dict:
    """Collect just the info needed to display the results."""
    return {
        "writers": writers,
        "total": len(writers)
    }


def browse_by_year(year: str) -> dict:
    year = year.strip()
    writers: list = database.get_writers_by_year(year)
    response: dict = __build_browse_response(writers)
    response["query"] = year
    return response


def browse_by_month(year: str, month: str) -> dict:
    year = year.strip()
    month = month.strip()
    pass


@browse.route("/", methods=["GET"])
@use_args({
    "year": fields.Str(
        location="query",
        missing=None,
        validate=lambda x: len(x) == 4
    ),
    "month": fields.Str(
        location="query",
        missing=None,
        validate=lambda x: len(x) == 2
    )
})
def get(args: dict):
    # We always need a year
    if args["year"] is None:
        return make_error_response("A year must be provided!", 422)

    # We also have a month, meaning we're browsing an individual month
    if args["month"] is not None:
        return browse_by_month(args["year"], args["month"])

    # We only have a year, so we're browsing by year
    else:
        return browse_by_year(args["year"])


@browse.route("/years", methods=["GET"])
def get_years():
    """Get the years of recorded prompts."""
    return jsonify(database.get_prompt_years())
