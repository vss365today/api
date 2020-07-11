from typing import List

from records import Record

from src.core.database import __connect_to_db


__all__ = ["get_unique_word_count", "get_archive"]


def get_unique_word_count() -> Record:

    sql = "SELECT DISTINCT COUNT(word) AS total_num_of_words FROM prompts"
    with __connect_to_db() as db:
        return db.query(sql).one()


def get_archive() -> List[Record]:
    """Get the full word archive for public use.

    Note: this method can take a while to run as the archive grows.
    """
    sql = """
SELECT
    `date`,
    word,
    handle AS `host`,
    CONCAT('https://twitter.com/', handle, '/status/', tweet_id) AS url
FROM prompts
JOIN writers ON writers.uid = prompts.uid
ORDER BY `date` DESC"""
    with __connect_to_db() as db:
        return db.query(sql).all()
