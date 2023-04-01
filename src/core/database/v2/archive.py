from datetime import date
from pathlib import Path
from typing import TypedDict

import xlsxwriter
from sqlalchemy.sql import func
from sqlalchemy.engine.row import Row

from src.configuration import get_secret
from src.core.database.models import Host, Prompt, db
from src.core.database.v2 import prompts
from src.core.helpers import format_datetime_pretty


__all__ = ["create", "get_for_date"]

# Set some constants for a consistent filename
FILE_NAME_BASE = "vss365today-prompt-archive-"
FILE_NAME_EXT = ".xlsx"


class _PromptDateRange(TypedDict):
    oldest: date
    newest: date


class _ColumnSizes(TypedDict):
    longest_word: int
    longest_handle: int
    longest_url: int


def __get_column_widths(year: int) -> _ColumnSizes:
    """Determine the best column widths for the given year data."""
    r = (
        Prompt.query.with_entities(
            (func.max(func.length(Prompt.word)) + 2).label("longest_word"),
            (func.max(func.length(Host.handle)) + 2).label("longest_handle"),
            (
                (func.max(func.length(Host.handle)))
                + (func.max(func.length(Prompt.twitter_id)) + 29)
            ).label("longest_url"),
        )
        .filter(
            func.year(Prompt.date) == year,
            func.year(Prompt.date) <= date.today().year,
        )
        .join(Host)
        .one()
    )
    return _ColumnSizes(
        longest_word=r.longest_word,
        longest_handle=r.longest_handle,
        longest_url=r.longest_url,
    )


def __get_prompt_date_range() -> _PromptDateRange:
    """Get the dates of the oldest and newest Prompts.

    Newest is a bit of a lie. It technically is the newest *non-future* Prompt.
    If it is a future Prompt, the newest recorded non-future Prompt is provided.
    """
    r = (
        Prompt.query.with_entities(
            func.min(Prompt.date).label("oldest"),
            func.max(Prompt.date).label("newest"),
        )
        .filter(Prompt.date <= date.today())
        .one()
    )
    return _PromptDateRange(oldest=r.oldest, newest=r.newest)


def __get_by_year(year: int) -> list[Row]:
    """Get all relevant Prompt information for the archive for the given year."""
    qs = (
        db.select(Host.handle, Prompt.date, Prompt.url, Prompt.word)
        .join(Host)
        .filter(func.year(Prompt.date) == year)
        .order_by(Prompt.word)
    )
    return db.session.execute(qs).all()


def create() -> str | None:
    """Generate a new Prompt archive."""
    # Check that we have permission to write to the save directory
    save_dir = Path(get_secret("DOWNLOADS_DIR")).resolve()
    try:
        temp_file = save_dir / "perm.temp"
        temp_file.write_bytes(b"")
        temp_file.unlink()
    except PermissionError:
        return None

    # Set up all of the date values we need
    today = date.today()
    all_prompt_years = prompts.get_years()
    year_range = __get_prompt_date_range()

    # Put together the archive's file name
    file_name = f"{FILE_NAME_BASE}{today.isoformat()}{FILE_NAME_EXT}"
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
            "#vss365 prompt archive from {} to {}".format(
                format_datetime_pretty(year_range["oldest"]),
                format_datetime_pretty(year_range["newest"]),
            ),
        )
        worksheet.write(1, 0, "Sorted by prompt in alphabetical order")
        worksheet.write(2, 0, f"Generated on {format_datetime_pretty(today)}")
        worksheet.write_url(3, 0, "https://vss365today.com")

        # Group each year's prompts in their own sheet
        for year in all_prompt_years:
            worksheet = workbook.add_worksheet(str(year))

            # Set the column widths
            widths = __get_column_widths(year)
            worksheet.set_column(0, 0, 10)
            worksheet.set_column(1, 1, widths["longest_word"])
            worksheet.set_column(2, 2, widths["longest_handle"])
            worksheet.set_column(3, 3, widths["longest_url"])

            # Write the headings
            worksheet.write(0, 0, "Date", bolded_text)
            worksheet.write(0, 1, "Prompt", bolded_text)
            worksheet.write(0, 2, "Host", bolded_text)
            worksheet.write(0, 3, "URL", bolded_text)

            # Get the prompt archive for the current year
            for row, prompt in enumerate(__get_by_year(year)):
                # Rows are zero-indexed, meaning we need to increment
                # so we don't clobber the headings
                row += 1

                # Write all the data
                worksheet.write_datetime(row, 0, prompt.date)
                worksheet.write(row, 1, prompt.word)
                worksheet.write(row, 2, prompt.handle)
                worksheet.write_url(row, 3, prompt.url)
    return file_name


def get_for_date(date: date) -> str | None:
    """Get an archive file for the given date."""
    save_dir = Path(get_secret("DOWNLOADS_DIR")).resolve()
    file_name = f"{FILE_NAME_BASE}{date.isoformat()}{FILE_NAME_EXT}"
    full_path = save_dir / file_name
    return file_name if full_path.exists() else None
