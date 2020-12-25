from datetime import datetime, timedelta
from pathlib import Path

import xlsxwriter
from flask import current_app

from src.blueprints import archive
from src.core import database, helpers
from src.core.auth_helpers import authorize_route
from src.core.models.v1.Prompt import Prompt

# Set some constants for a consistent filename
BASE_FILE_NAME = "vss365today-word-archive-"
FILE_NAME_EXT = ".xlsx"


@archive.route("/", methods=["GET"])
def get():
    """Get the filename for the newest word archive spreadsheet."""
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
    """Generate a new word archive spreadsheet."""
    # Set up all date values we need
    archive_years = database.prompt.get_years()
    archive_range = database.archive.prompt_date_range()
    oldest_date = helpers.format_datetime_pretty(archive_range["oldest"])
    newest_date = helpers.format_datetime_pretty(archive_range["newest"])
    today = datetime.now()
    today_iso = helpers.format_datetime_ymd(today)
    today_pretty = helpers.format_datetime_pretty(today)

    # Put together the save path and file name
    file_name = f"{BASE_FILE_NAME}{today_iso}{FILE_NAME_EXT}"
    save_dir = Path(current_app.config["DOWNLOADS_DIR"]).resolve()
    full_save_path = save_dir / file_name

    # Create a new spreadsheet file
    workbook_config = {"constant_memory": True, "default_date_format": "yyyy-mm-dd"}
    with xlsxwriter.Workbook(full_save_path, workbook_config) as workbook:
        # Create a bold text formatter
        bolded_text = workbook.add_format()
        bolded_text.set_bold()

        # Start by creating a page with basic file generation info
        worksheet = workbook.add_worksheet("Info")
        worksheet.write(
            0,
            0,
            f"#vss365 word archive from {oldest_date} to {newest_date}",
        )
        worksheet.write(1, 0, "Sorted by word in alphabetical order")
        worksheet.write(2, 0, f"Generated on {today_pretty}")
        worksheet.write_url(3, 0, "https://vss365today.com")

        # Group each year's prompts in their own sheet
        for year in archive_years:
            worksheet = workbook.add_worksheet(str(year))

            # Set the column widths
            widths = database.archive.get_column_widths(year)
            worksheet.set_column(0, 0, 10)
            worksheet.set_column(1, 1, widths.longest_word)
            worksheet.set_column(2, 2, widths.longest_handle)
            worksheet.set_column(3, 3, widths.longest_url)

            # Write the headings
            worksheet.write(0, 0, "Date", bolded_text)
            worksheet.write(0, 1, "Word", bolded_text)
            worksheet.write(0, 2, "Host", bolded_text)
            worksheet.write(0, 3, "URL", bolded_text)

            # Get the word archive for the current year
            for row, prompt in enumerate(database.archive.get(year)):
                # Rows are zero-indexed, meaning we need to increment
                # so we don't clobber the headings
                row += 1

                # Write all the data
                worksheet.write_datetime(row, 0, prompt.date)
                worksheet.write(row, 1, prompt.word)
                worksheet.write(row, 2, prompt.writer_handle)
                url = Prompt.make_url(prompt.writer_handle, prompt.tweet_id)
                worksheet.write_url(row, 3, url)
    return helpers.make_response(201)
