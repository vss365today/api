from typing import Any

from flask.views import MethodView
from flask_smorest import abort

import src.core.database.v2 as db
from src.core.models.v2 import Generic
from src.core.models.v2 import Search as models
from src.views import search


@search.route("/host/<string:query>")
class SearchByHost(MethodView):
    @search.arguments(models.Query, location="path", as_kwargs=True)
    @search.response(200, models.Results)
    @search.alt_response(404, schema=Generic.HttpError)
    @search.alt_response(422, schema=Generic.HttpError)
    def get(self, **kwargs: dict[str, Any]):
        """Search available Prompts by Host.

        Queries less than 2 characters are refused and will always return a 422 error.
        """
        query = kwargs["query"].strip()

        # Stop early if the handle doesn't exist
        if not db.hosts.exists(query):
            abort(404, message=f"The Host '{query}' does not exist.")

        r = db.prompts.get_by_host(query)
        return {"prompts": r, "total": len(r), "query": query}


@search.route("/query/<string:query>")
class SearchByQuery(MethodView):
    @search.arguments(models.Query, location="path", as_kwargs=True)
    @search.response(200, models.Results)
    @search.alt_response(422, schema=Generic.HttpError)
    def get(self, **kwargs: dict[str, Any]):
        """Search available Prompts words by query.

        Queries less than 2 characters are refused and will always return a 422 error.
        """
        query = kwargs["query"].strip()
        r = db.prompts.search(query)
        return {"prompts": r, "total": len(r), "query": query}
