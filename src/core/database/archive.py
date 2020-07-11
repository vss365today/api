from typing import List

from records import Record

from src.core.database import __connect_to_db


__all__ = ["get_unique_word_count", "get_archive"]


def get_unique_word_count() -> Record:

    sql = "SELECT DISTINCT COUNT(word) AS total_num_of_words FROM prompts"
    with __connect_to_db() as db:
        return db.query(sql).one()


def get_archive(year: int) -> List[Record]:
    """Get the full word archive for the given year."""
    sql = """
SELECT
    `date`,
    word,
    handle AS `host`,
    tweet_id
FROM prompts
JOIN writers ON writers.uid = prompts.uid
WHERE YEAR(`date`) = :year
ORDER BY `date` DESC"""
    with __connect_to_db() as db:
        return db.query(sql, year=year)
