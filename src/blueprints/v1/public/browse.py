import re
from flask import jsonify

from webargs import fields
from webargs.flaskparser import use_args

from src.blueprints import browse
from src.core import database
from src.core.helpers import make_error_response


def browse_by_year(year: str) -> dict:
    year = year.strip()
    hosts: list = database.hosts_get_by_year(year)
    return {"query": year, "hosts": hosts, "total": len(hosts)}


def browse_by_month(year: str, month: str) -> dict:
    year = year.strip()
    month = month.strip()
    hosts = database.hosts_get_by_year_month(year, month)
    prompts = database.prompts_get_by_date(f"{year}-{month}", date_range=True)
    return {"hosts": hosts, "prompts": prompts, "total": len(prompts)}


@browse.route("/", methods=["GET"])
@use_args(
    {
        "year": fields.Str(validate=lambda x: len(x) == 4),
        "month": fields.Str(
            validate=lambda x: re.search(r"^(?:0?\d)|(?:\d{2})$", x) is not None
        ),
    },
    location="query",
)
def get(args: dict):
    """Browse available Prompts by year or month-year combo."""
    # We always need a year
    if "year" not in args:
        return make_error_response(422, "At the least, a prompt year must be provided!")

    # We also have a month, meaning we're browsing an individual month
    if "month" in args:
        # Handle the month coming in as single number
        if len(args["month"]) == 1:
            args["month"] = f"0{args['month']}"

        month_data = browse_by_month(args["year"], args["month"])

        # Error out if there's no data
        if month_data["total"] != 0:
            return month_data
        return make_error_response(
            404,
            f"No prompts available for year-month {args['year']}-{args['month']}!",  # noqa
        )

    # We only have a year, so we're browsing by year
    year_results = browse_by_year(args["year"])

    # Error out if there's no data
    if year_results["total"] != 0:
        return year_results
    return make_error_response(404, f"No prompts available for year {args['year']}!")


@browse.route("/years/", methods=["GET"])
def get_years():
    """Get the years of recorded prompts."""
    return jsonify(database.prompt_get_years())
