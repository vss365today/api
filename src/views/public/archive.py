from datetime import date
from typing import Any

from flask.views import MethodView
from flask_smorest import abort

import src.core.database.v2 as db
from src.blueprints import archive_v2
from src.core.auth_helpers_v2 import require_permission
from src.core.models.v2 import Generic, Archive as models


@archive_v2.route("/")
class Archive(MethodView):
    @archive_v2.response(200, models.File)
    @archive_v2.alt_response(404, schema=Generic.HttpError)
    def get(self):
        ...

    @require_permission("archive")
    @archive_v2.response(201, Generic.Empty)
    @archive_v2.alt_response(403, schema=Generic.HttpError)
    @archive_v2.alt_response(422, schema=Generic.HttpError)
    def put(self):
        """TODO: write me!

        * **Permission Required**: `has_archive`
        """
        ...

    @require_permission("archive")
    @archive_v2.response(201, models.File)
    @archive_v2.alt_response(403, schema=Generic.HttpError)
    @archive_v2.alt_response(422, schema=Generic.HttpError)
    def post(self):
        """TODO: write me!

        * **Permission Required**: `has_archive`
        """
        ...
