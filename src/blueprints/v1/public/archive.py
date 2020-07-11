from pathlib import Path

from flask import current_app

from src.blueprints import archive
from src.core.auth_helpers import authorize_route
from src.core.database import archive as db_archive

# from src.core.helpers import make_response, make_error_response


@authorize_route
@archive.route("/", methods=["POST"])
def post():
    # spredsheet_location = Path(current_app.config["DOWNLOADS_PATH"]).resolve()

    # Get the full word archive
    word_archive = db_archive.get_archive()

    # TODO Should be kicked off by finder
    # TODO Generates only once a day
    # TODO Should there be a no-dup words option?
    # TODO Generate a new sheet for each year?
    # TODO CSV, xlsx, JSON?
    # TODO Basic archive stats?
    # - Can these just be excel formulas?
    # TODO Generate archive generation metadata
    # TODO Generate new spreadsheet with temp name
    # TODO Delete old spreadsheet or maybe have a 5 day backup?
    # - Doing so would add a GET option to return the latest filename
    # TODO Rename new spreadsheet to proper name
    # - What is the format of the name?
    return {}
