from datetime import datetime, timedelta
from pathlib import Path

from flask import current_app

from src.blueprints import archive
from src.core import database, helpers
from src.core.auth_helpers import authorize_route

# Set some constants for a consistent filename
BASE_FILE_NAME = "vss365today-prompt-archive-"
FILE_NAME_EXT = ".xlsx"


@archive.route("/", methods=["GET"])
def get():
    """Get the filename for the newest Prompt archive spreadsheet."""
    # Set up all date values we need
    today = datetime.now()
    today_iso = helpers.format_datetime_ymd(today)
    yesterday_iso = helpers.format_datetime_ymd(today - timedelta(days=1))

    # Build out all the paths we need
    save_dir = Path(current_app.config["DOWNLOADS_DIR"]).resolve()
    today_file_name = f"{BASE_FILE_NAME}{today_iso}{FILE_NAME_EXT}"
    yesterday_file_name = f"{BASE_FILE_NAME}{yesterday_iso}{FILE_NAME_EXT}"
    today_full_path = save_dir / today_file_name
    yesterday_full_path = save_dir / yesterday_file_name

    # If a file with today's date exists, return it
    # Otherwise, attempt to return yesterday's file
    # If neither exist, error so the consumer knows to wait
    if today_full_path.exists():
        return {"file": today_file_name}
    if yesterday_full_path.exists():
        return {"file": yesterday_file_name}
    return helpers.make_error_response(
        404, "Word archive currently unavailable for download!"
    )


@authorize_route
@archive.route("/", methods=["POST"])
def post():
    """Generate a new Prompt archive spreadsheet."""
    # Don't do anything if an archive has already been made
    latest_archive = get()
    if isinstance(latest_archive, dict):
        return helpers.make_response(304)

    database.archive.make(
        {
            "base_name": BASE_FILE_NAME,
            "ext": FILE_NAME_EXT,
            "downloads_dir": current_app.config["DOWNLOADS_DIR"],
        }
    )
    return helpers.make_response(201)


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
    database.archive.make(
        {
            "base_name": BASE_FILE_NAME,
            "ext": FILE_NAME_EXT,
            "downloads_dir": current_app.config["DOWNLOADS_DIR"],
        }
    )
    return helpers.make_response(201)
