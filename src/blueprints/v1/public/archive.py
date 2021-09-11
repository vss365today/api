from datetime import datetime, timedelta
from pathlib import Path

from flask import current_app

from src.blueprints import archive
from src.core import database, helpers
from src.core.auth_helpers import authorize_route


@archive.route("/", methods=["GET"])
def get():
    """Get the filename for the newest Prompt archive spreadsheet."""
    # Attempt to get today's and yesterday's files
    now = datetime.now()
    today = database.archive.get_file_for_date(now)
    yesterday = database.archive.get_file_for_date(now - timedelta(days=1))

    # If a file with today's date exists, return it
    # Otherwise, attempt to return yesterday's file
    # If neither exist, error so the consumer knows to wait
    if today is not None:
        return {"file": today}
    if yesterday is not None:
        return {"file": yesterday}
    return helpers.make_error_response(
        404, "Word archive currently unavailable for download!"
    )


@authorize_route
@archive.route("/", methods=["POST"])
def post():
    """Generate a new Prompt archive spreadsheet."""
    # Don't do anything if today's archive has already been generated
    now = datetime.now()
    if database.archive.get_file_for_date(now):
        return helpers.make_response(304)

    if database.archive.make():
        return helpers.make_response(201)
    return helpers.make_error_response(422, "Unable to create new archive file!")


@authorize_route
@archive.route("/", methods=["PUT"])
def put():
    """Regenerate the newest Prompt archive spreadsheet."""
    # Don't do anything if an archive can't be found
    latest_archive = get()
    if isinstance(latest_archive, tuple):
        return latest_archive

    # Delete the old archive
    save_dir = Path(current_app.config["DOWNLOADS_DIR"]).resolve()
    (save_dir / latest_archive["file"]).unlink(missing_ok=True)

    # Generate a new archive file
    if database.archive.make():
        return helpers.make_response(201)
    return helpers.make_error_response(422, "Unable to regenerate archive file!")
