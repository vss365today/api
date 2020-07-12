from datetime import date
from typing import Dict, List

from records import Record

from src.core.database import __connect_to_db


__all__ = ["get", "get_column_widths", "prompt_date_range"]


def prompt_date_range() -> Dict[str, date]:
    """Get the first and last recorded Prompt dates."""
    dates = {}

    # Get the oldest prompt date
    sql = "SELECT DISTINCT `date` FROM prompts ORDER BY `date` ASC LIMIT 1"
    with __connect_to_db() as db:
        dates["oldest"] = db.query(sql).one().date

    # Get the newest prompt date
    sql = "SELECT DISTINCT `date` FROM prompts ORDER BY `date` DESC LIMIT 1"
    with __connect_to_db() as db:
        dates["newest"] = db.query(sql).one().date
    return dates


def get(year: int) -> List[Record]:
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
    with __connect_to_db() as db:
        return db.query(sql, year=year)


def get_column_widths(year: int) -> List[Record]:
    """TODO"""
    sql = """
SELECT
    MAX(LENGTH(word)) + 2 AS longest_word,
    MAX(LENGTH(handle)) + 2 AS longest_handle,
    MAX(LENGTH(handle)) + MAX(LENGTH(tweet_id)) + 29 AS longest_url
FROM prompts
JOIN writers ON writers.uid = prompts.uid
WHERE YEAR(`date`) = :year"""
    with __connect_to_db() as db:
        return db.query(sql, year=year).one()
