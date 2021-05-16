from typing import Dict, List, Literal, Optional

from sqlalchemy.exc import IntegrityError

from src.core.database.core import connect_to_db, flatten_records
from src.core.models.v1.Prompt import Prompt

__all__ = [
    "delete",
    "create",
    "exists",
    "get_by_date",
    "get_by_host",
    "get_latest",
    "get_months",
    "get_years",
    "search",
    "update",
]


def delete(pid: str) -> Literal[True]:
    """Delete an existing prompt."""
    sql = "DELETE FROM prompts WHERE tweet_id = :id"
    with connect_to_db() as db:
        db.query(sql, **{"id": pid})
    return True


def create(prompt: Dict[str, Optional[str]]) -> bool:
    """Create a new prompt."""
    sql = """
    INSERT INTO prompts (
        tweet_id, date, uid, content, word, media
    )
    VALUES (
        :id, :date, :uid, :content, :word, :media
    )
    """
    try:
        with connect_to_db() as db:
            db.query(sql, **prompt)
            return True

    # A prompt with this ID already exists
    except IntegrityError as exc:
        print(f"Prompt creation exception: {exc}")
        print(prompt)
        return False


def exists(*, pid: str, date: str) -> bool:
    """Find an existing prompt."""
    sql = """SELECT 1
    FROM prompts
    WHERE (tweet_id = :tweet_id OR date = :date)"""
    with connect_to_db() as db:
        return bool(db.query(sql, tweet_id=pid, date=date).first())


def get_by_date(date: str, *, date_range: bool = False) -> List[Prompt]:
    """Get prompts by a single date or in a date range."""
    # Base query info
    sql = """
    SELECT prompts.*, writers.handle as writer_handle
    FROM prompts
        JOIN writers ON prompts.uid = writers.uid"""

    # Use the proper filter depending on if
    # we want a date range or single date
    if date_range:
        sql = f"""{sql}
        WHERE DATE_FORMAT(prompts.date, '%Y-%m') = :date
            AND prompts.date <= CURRENT_TIMESTAMP()
        ORDER BY prompts.date ASC"""
    else:
        sql = f"""{sql}
        WHERE prompts.date = STR_TO_DATE(:date, '%Y-%m-%d')
            AND STR_TO_DATE(:date, '%Y-%m-%d') <= CURRENT_TIMESTAMP()"""

    # Finally perform the query
    with connect_to_db() as db:
        return [Prompt(record) for record in db.query(sql, date=date)]


def get_by_host(handle: str) -> List[Prompt]:
    """Get a prompt tweet by the Host who prompted it."""
    sql = """
    SELECT prompts.*, writers.handle AS writer_handle
    FROM prompts
        JOIN writers ON writers.uid = prompts.uid
    WHERE prompts.date <= CURRENT_TIMESTAMP()
        AND writers.handle = :handle
    """
    with connect_to_db() as db:
        return [Prompt(record) for record in db.query(sql, handle=handle)]


def get_latest() -> List[Prompt]:
    """Get the newest prompt."""
    # Get the latest date in the database
    latest_date_sql = "SELECT date FROM prompts ORDER BY date DESC LIMIT 1"
    with connect_to_db() as db:
        latest_date = db.query(latest_date_sql).one().date

    # Using the latest date, fetch the prompt(s) for the date
    sql = """
    SELECT prompts.*, writers.handle AS writer_handle
    FROM prompts
        JOIN writers ON prompts.uid = writers.uid
    WHERE date = :latest_date
    ORDER BY date DESC
    """
    with connect_to_db() as db:
        return [Prompt(record) for record in db.query(sql, latest_date=latest_date)]


def get_months(year: str) -> List[str]:
    """Make all Prompts dates for a given year into a unique set.

    For some months in 2017, November 2020, and in 2021 and beyond,
    there are multiple Hosts per month giving out the prompts.
    While the individual dates are stored distinctly,
    we need a unique month list in order to correctly display
    the year browsing page.
    """
    sql = """
    SELECT DISTINCT DATE_FORMAT(date, '%m')
    FROM prompts
    WHERE YEAR(date) = :year AND
        :year <= YEAR(CURRENT_TIMESTAMP())
    ORDER BY MONTH(date) ASC
    """
    with connect_to_db() as db:
        return flatten_records(db.query(sql, year=year).all())


def get_years() -> List[str]:
    """Get a list of years of recorded Prompts."""
    sql = """
    SELECT DISTINCT CAST(YEAR(date) AS CHAR)
    FROM prompts
    ORDER BY date ASC
    """
    with connect_to_db() as db:
        return flatten_records(db.query(sql).all())


def search(word: str) -> List[Prompt]:
    """Search for prompts by partial or full word."""
    sql = """
    SELECT prompts.*, writers.handle AS writer_handle
    FROM prompts
        JOIN writers ON writers.uid = prompts.uid
    WHERE prompts.date <= CURRENT_TIMESTAMP()
        AND prompts.word LIKE CONCAT('%', :word, '%')
    ORDER BY UPPER(word)
    """
    with connect_to_db() as db:
        return [Prompt(record) for record in db.query(sql, word=word)]


def update(prompt: Dict[str, Optional[str]]) -> None:
    """Update an existing prompt."""
    sql = """
    UPDATE prompts
    SET
        date = :date,
        content = :content,
        word = :word,
        media =  :media
    WHERE tweet_id = :id
    """
    with connect_to_db() as db:
        db.query(sql, **prompt)
