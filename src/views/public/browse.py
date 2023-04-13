from datetime import date
from typing import Any

from flask.views import MethodView
from flask_smorest import abort

import src.core.database.v2 as db
from src.core.models.v2 import Browse as models
from src.core.models.v2 import Generic
from src.views import browse


@browse.route("/<int:year>")
class BrowseForYear(MethodView):
    @browse.arguments(models.ByYear, location="path", as_kwargs=True)
    @browse.response(200, models.BrowseResult)
    @browse.alt_response(404, schema=Generic.HttpError)
    def get(self, **kwargs: dict[str, Any]):
        """Get all of the Hosts for a given year."""
        if not (hosts := db.hosts.get_by_year(kwargs["year"])):
            abort(404, message=f"No data available for year {kwargs['year']}!")
        return {"hosts": hosts, "total": len(hosts)}


@browse.route("/<int:year>/<int:month>")
class BrowseForYearMonth(MethodView):
    @browse.arguments(models.ByYearMonth, location="path", as_kwargs=True)
    @browse.response(200, models.BrowseResult)
    @browse.alt_response(404, schema=Generic.HttpError)
    def get(self, **kwargs: dict[str, Any]):
        """Get the Hosts and Prompts for a valid calendar month."""
        # Make sure we're even given a valid calendar date
        try:
            date(year=kwargs["year"], month=kwargs["month"], day=1)
        except ValueError:
            abort(422, message="The month and year given is not a valid calendar date.")

        hosts = db.hosts.get_by_calendar_month(kwargs["year"], kwargs["month"])
        prompts = db.prompts.get_by_calendar_month(kwargs["year"], kwargs["month"])
        if not (hosts and prompts):
            abort(
                404,
                message=f"No data available for calendar month {kwargs['month']} {kwargs['year']}!",
            )

        return {"hosts": hosts, "prompts": prompts, "total": len(prompts)}


@browse.route("/years")
class BrowseYears(MethodView):
    @browse.response(200, models.GetYears)
    def get(self):
        """Get a list of years Prompts has been recorded."""
        return {"years": db.prompts.get_years()}


@browse.route("/years/<int:year>")
class BrowseMonths(MethodView):
    @browse.arguments(models.GetMonths, location="path", as_kwargs=True)
    @browse.response(200, models.GetMonths)
    def get(self, **kwargs: dict[str, Any]):
        """Get a list of months in a given year Prompts has been recorded.

        The month list may be blank if there are no Prompts for that year.
        """
        return {"months": db.prompts.get_months(kwargs["year"])}
