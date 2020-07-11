from datetime import datetime
from pathlib import Path

from flask import current_app
import xlsxwriter

from src.blueprints import archive
from src.core import database
from src.core.auth_helpers import authorize_route
from src.core.database import archive as db_archive
from src.core.helpers import format_datetime_iso, make_response


@authorize_route
@archive.route("/", methods=["POST"])
def post():
    # Get the full word archive
    word_archive = db_archive.get_archive()
    archive_years = database.prompt_get_years()

    # Put together the save path and file name
    today = format_datetime_iso(datetime.now())
    file_name = f"vss365today-word-archive-{today}.xlsx"
    save_dir = Path(current_app.config["DOWNLOADS_PATH"]).resolve()
    full_save_path = save_dir / file_name

    # Create a new spreadsheet file
    # with xlsxwriter.Workbook(full_save_path) as workbook:
    #     for year in archive_years:
    #         worksheet = workbook.add_worksheet(year)

    #     worksheet.write("A1", "Hello world")

    # TODO Should be kicked off by finder
    # TODO Generates only once a day
    # TODO Should there be a no-dup words option?
    # TODO Generate new spreadsheet
    # - https://xlsxwriter.readthedocs.io/getting_started.html
    # TODO Generate a new sheet for each year
    # TODO Basic archive stats?
    # - Can these just be excel formulas?
    # TODO Generate archive generation metadata
    # TODO Delete old spreadsheet or maybe have a 5 day backup?
    # - Doing so would add a GET option to return the latest filename
    # TODO Rename new spreadsheet to proper name
    # - What is the format of the name?
    return make_response(201)
