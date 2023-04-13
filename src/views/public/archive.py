from datetime import date, timedelta

from flask.views import MethodView
from flask_smorest import abort

import src.core.database.v2 as db
from src.core.auth_helpers import require_permission
from src.core.models.v2 import Archive as models
from src.core.models.v2 import Generic
from src.views import archive


@archive.route("/")
class Archive(MethodView):
    @archive.response(200, models.File)
    @archive.alt_response(404, schema=Generic.HttpError)
    def get(self):
        """Get the file name of the newest Prompt archive."""
        # Attempt to get an archive with today's date,
        # then yesterday's date if that fails
        today = date.today()
        if (file := db.archive.get_for_date(today)) is not None:
            return {"file_name": file}
        if (file := db.archive.get_for_date(today - timedelta(days=1))) is not None:
            return {"file_name": file}

        # We don't have an archive to download. This really shouldn't happen
        # but it can if an archive hasn't been generated for a few days
        abort(404, "Latest Prompt archive currently unavailable.")

    @require_permission("archive")
    @archive.response(201, models.File)
    @archive.alt_response(403, schema=Generic.HttpError)
    @archive.alt_response(404, schema=Generic.HttpError)
    def post(self):
        """Generate a new Prompt archive using today's date.

        * **Permission Required**: `has_archive`
        """
        # Attempt to create a new archive file
        if (file := db.archive.create()) is not None:
            return {"file_name": file}

        abort(404, "Unable to generate new Prompt archive file.")
