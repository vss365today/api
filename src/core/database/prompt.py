from datetime import datetime
from typing import Literal, Optional

from sqlalchemy.exc import IntegrityError

from src.core.database.core import connect_to_db
from src.core.models.v1.Prompt import Prompt

__all__ = [
    "delete",
    "create",
    "exists",
    "get_by_date",
    "get_by_host",
    "get_latest",
    "get_months",
    "get_one_year",
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


def create(prompt: dict[str, Optional[str]]) -> bool:
    """Create a new prompt."""
    sql = """
    INSERT INTO prompts (
        tweet_id, date, uid, content, word, media, media_alt_text
    )
    VALUES (
        :id, :date, :uid, :content, :word, :media, :media_alt_text
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


def get_by_date(date: str, *, date_range: bool = False) -> list[Prompt]:
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


def get_by_host(handle: str) -> list[Prompt]:
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


def get_latest() -> list[Prompt]:
    """Get the newest prompt."""
    # Get the latest date in the database
    latest_date_sql = "SELECT date FROM prompts ORDER BY date DESC LIMIT 1"
    with connect_to_db() as db:
        latest_date = db.query(latest_date_sql).one()["date"]

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


def get_months(year: str) -> list[str]:
    """Make all Prompts dates for a given year into a unique set.

    For some months in 2017, November 2020, and in 2021 and beyond,
    there are multiple Hosts per month giving out the prompts.
    While the individual dates are stored distinctly,
    we need a unique month list in order to correctly display
    the year browsing page.
    """
    sql = """
    SELECT DISTINCT DATE_FORMAT(date, '%m') as `month`
    FROM prompts
    WHERE YEAR(date) = :year AND
        :year <= YEAR(CURRENT_TIMESTAMP())
    ORDER BY MONTH(date) ASC
    """
    with connect_to_db() as db:
        return [r["month"] for r in db.query(sql, year=year).all()]


def get_one_year() -> dict:
    """Get the images for the special one year anniversary Prompts."""
    return {
        "previous": datetime(2017, 9, 4, 0, 0, 0),
        "next": datetime(2017, 9, 6, 0, 0, 0),
        "writer_handle": "FlashDogs",
        "prompts": [
            {
                "media": "one-year-01.jpg",
                "url": "https://twitter.com/FlashDogs/status/904845903151984641",
            },
            {
                "media": "one-year-02.jpg",
                "url": "https://twitter.com/FlashDogs/status/904859017440137216",
            },
            {
                "media": "one-year-03.jpg",
                "url": "https://twitter.com/FlashDogs/status/904875614691348480",
            },
            {
                "media": "one-year-04.jpg",
                "url": "https://twitter.com/FlashDogs/status/904887621050097666",
            },
            {
                "media": "one-year-05.jpg",
                "url": "https://twitter.com/FlashDogs/status/904902281392508928",
            },
            {
                "media": "one-year-06.jpg",
                "url": "https://twitter.com/FlashDogs/status/904921977550491649",
            },
            {
                "media": "one-year-07.jpg",
                "url": "https://twitter.com/FlashDogs/status/904936216252047360",
            },
            {
                "media": "one-year-08.jpg",
                "url": "https://twitter.com/FlashDogs/status/904947975574753288",
            },
            {
                "media": "one-year-09.jpg",
                "url": "https://twitter.com/FlashDogs/status/904962425874731008",
            },
            {
                "media": "one-year-10.jpg",
                "url": "https://twitter.com/FlashDogs/status/904977597230178305",
            },
            {
                "media": "one-year-11.jpg",
                "url": "https://twitter.com/FlashDogs/status/904998249538433024",
            },
            {
                "media": "one-year-12.jpg",
                "url": "https://twitter.com/FlashDogs/status/905008561775943680",
            },
            {
                "media": "one-year-13.jpg",
                "url": "https://twitter.com/FlashDogs/status/905025269320343553",
            },
            {
                "media": "one-year-14.jpg",
                "url": "https://twitter.com/FlashDogs/status/905038056041873408",
            },
            {
                "media": "one-year-15.jpg",
                "url": "https://twitter.com/FlashDogs/status/905053527717892096",
            },
            {
                "media": "one-year-16.jpg",
                "url": "https://twitter.com/FlashDogs/status/905068825330241536",
            },
            {
                "media": "one-year-17.jpg",
                "url": "https://twitter.com/FlashDogs/status/905083147490086912",
            },
            {
                "media": "one-year-18.jpg",
                "url": "https://twitter.com/FlashDogs/status/905099149263167488",
            },
            {
                "media": "one-year-19.jpg",
                "url": "https://twitter.com/FlashDogs/status/905118874881929216",
            },
            {
                "media": "one-year-20.jpg",
                "url": "https://twitter.com/FlashDogs/status/905129473498107906",
            },
            {
                "media": "one-year-21.jpg",
                "url": "https://twitter.com/FlashDogs/status/905155776611799041",
            },
            {
                "media": "one-year-22.jpg",
                "url": "https://twitter.com/FlashDogs/status/905159105899372545",
            },
            {
                "media": "one-year-23.jpg",
                "url": "https://twitter.com/FlashDogs/status/905173946655531008",
            },
            {
                "media": "one-year-24.jpg",
                "url": "https://twitter.com/FlashDogs/status/905188903900106752",
            },
        ],
    }


def get_years() -> list[str]:
    """Get a list of years of recorded Prompts."""
    sql = """
    SELECT DISTINCT CAST(YEAR(date) AS CHAR) as `year`
    FROM prompts
    ORDER BY date ASC
    """
    with connect_to_db() as db:
        return [r["year"] for r in db.query(sql).all()]


def search(word: str) -> list[Prompt]:
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


def update(prompt: dict[str, Optional[str]]) -> None:
    """Update an existing prompt."""
    sql = """
    UPDATE prompts
    SET
        date = :date,
        content = :content,
        word = :word,
        media = :media,
        media_alt_text = :media_alt_text
    WHERE tweet_id = :id
    """
    with connect_to_db() as db:
        db.query(sql, **prompt)
