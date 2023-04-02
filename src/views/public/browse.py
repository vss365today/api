# from datetime import date, timedelta

from typing import Any
from flask.views import MethodView
from flask_smorest import abort

import src.core.database.v2 as db
from src.blueprints import browse_v2
from src.core.models.v2 import Generic, Browse as models


@browse_v2.route("/years")
class BrowseYears(MethodView):
    @browse_v2.response(200, models.Years)
    def get(self):
        return {"years": db.prompts.get_years()}


@browse_v2.route("/years/<int:year>")
class BrowseMonths(MethodView):
    @browse_v2.arguments(models.Months, location="path", as_kwargs=True)
    @browse_v2.response(200, models.Months)
    def get(self, **kwargs: dict[str, Any]):
        return {"months": db.prompts.get_months(kwargs["year"])}
