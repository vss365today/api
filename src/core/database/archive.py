from datetime import date
from typing import Dict, List

from records import Record

from src.core.database import __connect_to_db


__all__ = ["get_unique_word_count", "get_archive"]


def get_unique_word_count() -> Record:

    sql = "SELECT DISTINCT COUNT(word) AS total_num_of_words FROM prompts"
    with __connect_to_db() as db:
        return db.query(sql).one()


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


def get_archive(year: int) -> List[Record]:
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
