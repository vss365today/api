from typing import List, Literal, Union

from tweepy.error import TweepError
from sqlalchemy.exc import DataError, IntegrityError
from sqlalchemy.sql import text

from src.core.database.core import connect_to_db, create_transaction
from src.core.helpers import connect_to_twitter
from src.core.models.v1.Host import Host


__all__ = [
    "create",
    "create_date",
    "delete",
    "delete_date",
    "lookup",
    "get",
    "get_all",
    "get_by_date",
    "get_by_year",
    "get_by_year_month",
    "update",
]


def create(host_info: dict) -> bool:
    """Create a new Host."""
    sql = "INSERT INTO writers (uid, handle) VALUES (:uid, :handle)"
    try:
        with connect_to_db() as db:
            db.query(sql, uid=host_info["id"], handle=host_info["handle"])
            return True
    except DataError as exc:
        print(exc)
        return False


def create_date(host_info: dict) -> bool:
    """Create a new hosting date."""
    sql = "INSERT INTO writer_dates (uid, date) VALUES (:uid, :date)"
    try:
        with connect_to_db() as db:
            db.query(sql, uid=host_info["id"], date=host_info["date"])
            return True
    except DataError as exc:
        print(exc)
        return False


def delete(uid: str) -> bool:
    """Delete a Host from the database by their Twitter ID.

    Due to database FK constraints, this will only succeed
    if the Host does not have any Prompts associated with them.
    The presence of any Prompts will stop all deletion so as to
    prevent orphaned records or an incomplete record.
    """
    sql = "DELETE FROM writers WHERE uid = :uid"
    try:
        with connect_to_db() as db:
            db.query(sql, uid=uid)
            return True
    except IntegrityError:
        return False


def delete_date(uid: str, date: str) -> Literal[True]:
    """Delete a specific date for a Host."""
    sql = "DELETE FROM writer_dates WHERE uid = :uid AND date = :date"
    with connect_to_db() as db:
        db.query(sql, uid=uid, date=date)
    return True


def get(*, uid: str, handle: str) -> List[Host]:
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
    with connect_to_db() as db:
        return [Host(host) for host in db.query(sql, uid=uid, handle=handle)]


def get_all() -> List[Host]:
    """Get a list of all Hosts."""
    sql = """
    SELECT DISTINCT writers.uid, handle
    FROM writers
        JOIN writer_dates ON writer_dates.uid = writers.uid
    WHERE writer_dates.date <= CURRENT_TIMESTAMP()
    ORDER BY handle
    """
    with connect_to_db() as db:
        return db.query(sql).all(as_dict=True)


def get_by_date(date: str) -> List[Host]:
    """Get the Host for the given date."""
    sql = """
    SELECT writers.uid, handle, writer_dates.date
    FROM writers
        JOIN writer_dates ON writer_dates.uid = writers.uid
    WHERE writer_dates.date = :date
    """
    with connect_to_db() as db:
        return [Host(host) for host in db.query(sql, date=date)]


def get_by_year(year: str) -> List[Host]:
    """Get a list of all Hosts for a given year."""
    sql = """
    SELECT writers.uid, handle, writer_dates.date
    FROM writers
        JOIN writer_dates ON writer_dates.uid = writers.uid
    WHERE YEAR(writer_dates.date) = :year
        AND DATE_FORMAT(writer_dates.date, '%Y-%m') <=
            DATE_FORMAT(CURRENT_TIMESTAMP(), '%Y-%m')
    ORDER BY writer_dates.date ASC
    """
    with connect_to_db() as db:
        return [Host(host) for host in db.query(sql, year=year)]


def get_by_year_month(year: str, month: str) -> List[Host]:
    """Get all the Hosts in a year-month combination."""
    sql = """
    SELECT writers.uid, handle, writer_dates.date
    FROM writers
        JOIN writer_dates ON writer_dates.uid = writers.uid
    WHERE
        YEAR(writer_dates.date) = :year
        AND MONTH(writer_dates.date) = :month
    """
    with connect_to_db() as db:
        return [Host(host) for host in db.query(sql, year=year, month=month)]


def lookup(handle: str) -> Union[str, Literal[False]]:
    """Get the Host's Twitter user ID."""
    try:
        api = connect_to_twitter()
        host = api.get_user(handle)
        return host.id_str

    # That handle couldn't be found
    except TweepError:
        return False


def update(host_info: dict) -> None:
    """Update a Host's information."""
    sql_host = text("UPDATE writers SET handle = :handle WHERE uid = :uid;")
    sql_host_date = text(
        "UPDATE writer_dates SET date =  STR_TO_DATE(:date, '%Y-%m-%d') WHERE uid = :uid;"
    )

    # Update the host info in a transaction
    with connect_to_db() as db:
        with create_transaction(db) as tx:
            if host_info["handle"] is not None:
                tx.execute(sql_host, uid=host_info["id"], handle=host_info["handle"])
            if host_info["date"] is not None:
                tx.execute(sql_host_date, uid=host_info["id"], date=host_info["date"])
