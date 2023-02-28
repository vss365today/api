from datetime import date
from typing import TypedDict
from pathlib import Path

from sqlalchemy.sql import func

from src.configuration import get_secret
from src.core.database.models import Prompt, db


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
    ...


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


def __get_by_year(year: int) -> list[Prompt]:
    ...


def create() -> bool:
    ...


def get_for_date(date: date) -> str | None:
    """Get an archive file for the given date."""
    save_dir = Path(get_secret("DOWNLOADS_DIR")).resolve()
    file_name = f"{FILE_NAME_BASE}{date.isoformat()}{FILE_NAME_EXT}"
    full_path = save_dir / file_name
    return file_name if full_path.exists() else None
