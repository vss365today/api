from flask import jsonify

from webargs import fields
from webargs.flaskparser import use_args

from src.blueprints import browse
from src.core import database
from src.core.helpers import make_error_response


def browse_by_year(year: str) -> dict:
    year = year.strip()
    hosts: list = database.get_writers_by_year(year)
    return {
        "query": year,
        "hosts": hosts,
        "total": len(hosts)
    }


def browse_by_month(year: str, month: str) -> dict:
    year = year.strip()
    month = month.strip()
    date: str = f"{year}-{month}"
    hosts = database.get_writers_by_date(date)
    prompts = database.get_prompts_by_date(date)
    return {
        "hosts": hosts,
        "prompts": prompts,
        "total": len(prompts)
    }


@browse.route("/", methods=["GET"])
@use_args({
    "year": fields.Str(
        location="query",
        validate=lambda x: len(x) == 4
    ),
    "month": fields.Str(
        location="query",
        validate=lambda x: len(x) == 2
    )
})
def get(args: dict):
    # We always need a year
    if "year" not in args:
        return make_error_response("A year must be provided!", 422)

    # We also have a month, meaning we're browsing an individual month
    if "month" in args:
        return browse_by_month(args["year"], args["month"])

    # We only have a year, so we're browsing by year
    else:
        return browse_by_year(args["year"])


@browse.route("/years/", methods=["GET"])
def get_years():
    """Get the years of recorded prompts."""
    return jsonify(database.get_prompt_years())
