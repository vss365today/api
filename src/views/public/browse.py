# from datetime import date, timedelta

from flask.views import MethodView
from flask_smorest import abort

import src.core.database.v2 as db
from src.blueprints import browse_v2
from src.core.models.v2 import Generic, Browse as models


# @browse_v2.route("/")
# class Browse(MethodView):
#     @browse_v2.response(200, models.File)
#     @browse_v2.alt_response(404, schema=Generic.HttpError)
#     def get(self):
#         pass
