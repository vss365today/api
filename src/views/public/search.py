from typing import Any

from flask.views import MethodView
from flask_smorest import abort

import src.core.database.v2 as db
from src.blueprints import search_v2
from src.core.models.v2 import Generic, Search as models


@search_v2.route("/host/<string:query>")
class SearchByHost(MethodView):
    @search_v2.arguments(models.ByHost, location="path", as_kwargs=True)
    @search_v2.response(200, models.ByHost)
    def get(self, **kwargs: dict[str, Any]):
        """Search available Prompts by Host."""
        query = kwargs["query"].strip()

        return {}


@search_v2.route("/query/<string:query>")
class SearchByQuery(MethodView):
    @search_v2.arguments(models.ByQuery, location="path", as_kwargs=True)
    @search_v2.response(200, models.ByQuery)
    @search_v2.alt_response(422, schema=Generic.HttpError)
    def get(self, **kwargs: dict[str, Any]):
        """Search available Prompts words by query.

        Queries less than 2 characters are refused and will always return a 422 error.
        """
        query = kwargs["query"].strip()
        r = db.prompts.search(query)
        return {"prompts": r, "total": len(r), "query": query}
