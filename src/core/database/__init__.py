from typing import Dict, List, Literal, Optional

import records
from flask import current_app
from sqlalchemy.exc import DBAPIError, IntegrityError
from sqlalchemy.sql import text

from src.core.models.v1.Host import Host
from src.core.models.v1.Prompt import Prompt


__all__ = [
    "prompt_create",
    "prompt_delete",
    "prompt_update",
    "prompt_find_existing",
    "prompt_get_latest",
    "prompt_get_years",
    "prompt_search",
    "prompts_get_by_date",
    "prompts_get_by_host",
    "host_create",
    "host_delete",
    "host_get",
    "host_get_by_date",
    "hosts_get_by_year",
    "hosts_get_by_year_month",
]


def __connect_to_db() -> records.Database:
    """Create a connection to the database."""
    conn_str = "mysql+pymysql://{}:{}@{}/{}".format(
        current_app.config["DB_USERNAME"],
        current_app.config["DB_PASSWORD"],
        current_app.config["DB_HOST"],
        current_app.config["DB_DBNAME"],
    )
    conn = records.Database(conn_str)
    return conn


def __create_transaction(db):
    """Reach into SQLAlchemy to start a transaction."""
    return db._engine.begin()  # skipcq: PYL-W0212


def __flatten_tuple_list(tup) -> list:
    """Flatten a list of tuples into a tuple of actual data."""
    return [item[0] for item in tup]


def prompt_create(prompt: Dict[str, Optional[str]]) -> bool:
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
        with __connect_to_db() as db:
            db.query(sql, **prompt)
            return True

    # A prompt with this ID already exists
    except IntegrityError as exc:
        print(f"Prompt creation exception: {exc}")
        print(prompt)
        return False


def prompt_delete(pid: str) -> Literal[True]:
    """Delete an existing prompt."""
    sql = "DELETE FROM prompts WHERE tweet_id = :id"
    with __connect_to_db() as db:
        db.query(sql, **{"id": pid})
    return True


def prompt_update(prompt: Dict[str, Optional[str]]) -> None:
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
    with __connect_to_db() as db:
        db.query(sql, **prompt)


def prompt_find_existing(*, pid: str, date: str) -> bool:
    """Find an existing prompt."""
    sql = """SELECT 1
    FROM prompts
    WHERE (tweet_id = :tweet_id OR date = :date)"""
    with __connect_to_db() as db:
        return bool(db.query(sql, tweet_id=pid, date=date).first())


def prompt_get_latest() -> List[Prompt]:
    """Get the newest prompt."""
    # Get the latest date in the database
    latest_date_sql = "SELECT date FROM prompts ORDER BY date DESC LIMIT 1"
    with __connect_to_db() as db:
        latest_date = db.query(latest_date_sql).one().date

    # Using the latest date, fetch the prompt(s) for the date
    sql = """
    SELECT prompts.*, writers.handle AS writer_handle
    FROM prompts
        JOIN writers ON prompts.uid = writers.uid
    WHERE date = :latest_date
    ORDER BY date DESC
    """
    with __connect_to_db() as db:
        return [Prompt(record) for record in db.query(sql, latest_date=latest_date)]


def prompt_get_years() -> List[str]:
    """Get a list of years of recorded prompts."""
    sql = """
    SELECT DISTINCT YEAR(date)
    FROM writer_dates
    WHERE YEAR(date) <= YEAR(CURRENT_TIMESTAMP())
    ORDER BY date ASC
    """
    with __connect_to_db() as db:
        return __flatten_tuple_list(db.query(sql).all())


def prompt_search(word: str) -> List[Prompt]:
    """Search for prompts by partial or full word."""
    sql = """
    SELECT prompts.*, writers.handle AS writer_handle
    FROM prompts
        JOIN writers ON writers.uid = prompts.uid
    WHERE prompts.date <= CURRENT_TIMESTAMP()
        AND prompts.word LIKE CONCAT('%', :word, '%')
    ORDER BY UPPER(word)
    """
    with __connect_to_db() as db:
        return [Prompt(record) for record in db.query(sql, word=word)]


def prompts_get_by_date(date: str, *, date_range: bool = False) -> List[Prompt]:
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
    with __connect_to_db() as db:
        return [Prompt(record) for record in db.query(sql, date=date)]


def prompts_get_by_host(handle: str) -> List[Prompt]:
    """Get a prompt tweet by the Host who prompted it."""
    sql = """
    SELECT prompts.*, writers.handle AS writer_handle
    FROM prompts
        JOIN writers ON writers.uid = prompts.uid
    WHERE prompts.date <= CURRENT_TIMESTAMP()
        AND writers.handle = :handle
    """
    with __connect_to_db() as db:
        return [Prompt(record) for record in db.query(sql, handle=handle)]


def host_create(host_info: dict) -> bool:
    """Create a new Host."""
    # Create the SQL needed to insert
    sql_host = text("INSERT INTO writers (uid, handle) VALUES (:uid, :handle)")
    sql_host_date = text("INSERT INTO writer_dates (uid, date) VALUES (:uid, :date)")

    with __connect_to_db() as db:
        # Perform the insertion using a transaction
        # since both parts are required for it to be successful
        try:
            # Reach into sqlalchemy to perform a transaction as Records
            # utterly fails to properly support this
            with __create_transaction(db) as tx:
                tx.execute(sql_host, uid=host_info["id"], handle=host_info["handle"])

                # Only insert a date if one was given
                if host_info["date"] is not None:
                    tx.execute(
                        sql_host_date, uid=host_info["id"], date=host_info["date"]
                    )
                return True

        # The transaction failed
        except DBAPIError as exc:
            print(exc)
            return False


def host_delete(uid: str) -> bool:
    """Delete a Host from the database by their Twitter ID.

    Due to database FK constraints, this will only succeed
    if the Host does not have any Prompts associated with them.
    The presence of any Prompts will stop all deletion so as to
    prevent orphaned records or an incomplete record."""
    sql = "DELETE FROM writers WHERE uid = :uid"
    try:
        with __connect_to_db() as db:
            db.query(sql, uid=uid)
            return True
    except IntegrityError:
        return False


def host_get(*, uid: str, handle: str) -> List[Host]:
    """Get Host info by either their Twitter ID or handle."""
    sql = """
    SELECT writers.uid, handle, writer_dates.date
    FROM writers
        JOIN writer_dates ON writer_dates.uid = writers.uid
    WHERE
        writer_dates.date <= CURRENT_TIMESTAMP()
        AND (writers.uid = :uid OR UPPER(handle) = UPPER(:handle))
    ORDER BY date DESC
    """
    with __connect_to_db() as db:
        return [Host(host) for host in db.query(sql, uid=uid, handle=handle)]


def host_update(host_info: dict) -> None:
    """Update a Host's information."""
    sql_host = text("UPDATE writers SET handle = :handle WHERE uid = :uid;")
    sql_host_date = text(
        "UPDATE writer_dates SET date =  STR_TO_DATE(:date, '%Y-%m-%d') WHERE uid = :uid;"
    )

    # Update the host info in a transaction
    with __connect_to_db() as db:
        with __create_transaction(db) as tx:
            if host_info["handle"] is not None:
                tx.execute(sql_host, uid=host_info["id"], handle=host_info["handle"])
            if host_info["date"] is not None:
                tx.execute(sql_host_date, uid=host_info["id"], date=host_info["date"])


def host_get_by_date(date: str) -> List[Host]:
    """Get the Host for the exact date given."""
    sql = """
    SELECT writers.uid, handle, writer_dates.date
    FROM writers
        JOIN writer_dates ON writer_dates.uid = writers.uid
    WHERE writer_dates.date = :date
    """
    with __connect_to_db() as db:
        return [Host(host) for host in db.query(sql, date=date)]


def hosts_get_by_year(year: str) -> List[Host]:
    """Get a list of all Hosts for a particular year."""
    sql = """
    SELECT writers.uid, handle, writer_dates.date
    FROM writers
        JOIN writer_dates ON writer_dates.uid = writers.uid
    WHERE YEAR(writer_dates.date) = :year
        AND DATE_FORMAT(writer_dates.date, '%Y-%m') <=
            DATE_FORMAT(CURRENT_TIMESTAMP(), '%Y-%m')
    ORDER BY writer_dates.date ASC
    """
    with __connect_to_db() as db:
        return [Host(host) for host in db.query(sql, year=year)]


def hosts_get_by_year_month(year: str, month: str) -> List[Host]:
    """Get all the Hosts in a year-month combination."""
    sql = """
    SELECT writers.uid, handle, writer_dates.date
    FROM writers
        JOIN writer_dates ON writer_dates.uid = writers.uid
    WHERE
        YEAR(writer_dates.date) = :year
        AND MONTH(writer_dates.date) = :month
    """
    with __connect_to_db() as db:
        return [Host(host) for host in db.query(sql, year=year, month=month)]
