from datetime import date, datetime
from typing import Optional
from pathlib import Path

from records import Record
import xlsxwriter

from src.configuration import get_secret
from src.core import helpers
from src.core.database.core import connect_to_db
from src.core import database
from src.core.models.v1.Prompt import Prompt


__all__ = ["get", "get_column_widths", "get_file_for_date", "make", "prompt_date_range"]


# Set some constants for a consistent filename
FILE_NAME_BASE = "vss365today-prompt-archive-"
FILE_NAME_EXT = ".xlsx"


def prompt_date_range() -> dict[str, date]:
    """Get the first and last recorded Prompt dates."""
    dates = {}

    # Get the oldest prompt date
    sql = "SELECT DISTINCT `date` FROM prompts ORDER BY `date` ASC LIMIT 1"
    with connect_to_db() as db:
        dates["oldest"] = db.query(sql).one().date

    # Get the newest prompt date
    sql = "SELECT DISTINCT `date` FROM prompts ORDER BY `date` DESC LIMIT 1"
    with connect_to_db() as db:
        dates["newest"] = db.query(sql).one().date
    return dates


def get(year: int) -> list[Record]:
    """Get the full word archive for the given year."""
    sql = """
SELECT
    `date`,
    word,
    handle AS `writer_handle`,
    tweet_id
FROM prompts
JOIN writers ON writers.uid = prompts.uid
WHERE YEAR(`date`) = :year
ORDER BY word ASC"""
    with connect_to_db() as db:
        return db.query(sql, year=year)


def get_column_widths(year: int) -> Record:
    """Determine the best column widths for the yearly data."""
    sql = """
SELECT
    MAX(LENGTH(word)) + 2 AS longest_word,
    MAX(LENGTH(handle)) + 2 AS longest_handle,
    MAX(LENGTH(handle)) + MAX(LENGTH(tweet_id)) + 29 AS longest_url
FROM prompts
JOIN writers ON writers.uid = prompts.uid
WHERE YEAR(`date`) = :year"""
    with connect_to_db() as db:
        return db.query(sql, year=year).one()


def get_file_for_date(full_date: datetime) -> Optional[str]:
    """Determine if an archive file for a date exists."""
    date_iso = helpers.format_datetime_ymd(full_date)
    save_dir = Path(get_secret("DOWNLOADS_DIR")).resolve()
    file_name = f"{FILE_NAME_BASE}{date_iso}{FILE_NAME_EXT}"
    full_path = save_dir / file_name

    # If the file exists, return a Path to it
    if full_path.exists():
        return file_name
    return None


def make() -> bool:
    """Generate a new Prompt archive spreadsheet."""
    # Check that we have permission to write to the save directory
    save_dir = Path(get_secret("DOWNLOADS_DIR")).resolve()
    try:
        temp_file = save_dir / "perm.temp"
        temp_file.write_text("")
        temp_file.unlink()
    except PermissionError:
        return False

    # Set up all date values we need
    archive_years = database.prompt.get_years()
    archive_range = prompt_date_range()
    oldest_date = helpers.format_datetime_pretty(archive_range["oldest"])
    newest_date = helpers.format_datetime_pretty(archive_range["newest"])
    today = datetime.now()
    today_iso = helpers.format_datetime_ymd(today)
    today_pretty = helpers.format_datetime_pretty(today)

    # Put together the archive's file name
    file_name = f"{FILE_NAME_BASE}{today_iso}{FILE_NAME_EXT}"
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
            f"#vss365 prompt archive from {oldest_date} to {newest_date}",
        )
        worksheet.write(1, 0, "Sorted by prompt in alphabetical order")
        worksheet.write(2, 0, f"Generated on {today_pretty}")
        worksheet.write_url(3, 0, "https://vss365today.com")

        # Group each year's prompts in their own sheet
        for year in archive_years:
            worksheet = workbook.add_worksheet(str(year))

            # Set the column widths
            widths = get_column_widths(int(year))
            worksheet.set_column(0, 0, 10)
            worksheet.set_column(1, 1, widths.longest_word)
            worksheet.set_column(2, 2, widths.longest_handle)
            worksheet.set_column(3, 3, widths.longest_url)

            # Write the headings
            worksheet.write(0, 0, "Date", bolded_text)
            worksheet.write(0, 1, "Prompt", bolded_text)
            worksheet.write(0, 2, "Host", bolded_text)
            worksheet.write(0, 3, "URL", bolded_text)

            # Get the prompt archive for the current year
            for row, prompt in enumerate(get(int(year))):
                # Rows are zero-indexed, meaning we need to increment
                # so we don't clobber the headings
                row += 1

                # Write all the data
                worksheet.write_datetime(row, 0, prompt.date)
                worksheet.write(row, 1, prompt.word)
                worksheet.write(row, 2, prompt.writer_handle)
                url = Prompt.make_url(prompt.writer_handle, prompt.tweet_id)
                worksheet.write_url(row, 3, url)
    return True
