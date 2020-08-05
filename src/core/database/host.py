from typing import List

from sqlalchemy.exc import DBAPIError, IntegrityError
from sqlalchemy.sql import text

from src.core.database.core import connect_to_db, create_transaction
from src.core.models.v1.Host import Host

__all__ = [
    "create",
    "delete",
    "get",
    "get_all",
    "get_by_date",
    "get_by_year",
    "get_by_year_month",
    "update",
]


def create(host_info: dict) -> bool:
    """Create a new Host."""
    # Create the SQL needed to insert
    sql_host = text("INSERT INTO writers (uid, handle) VALUES (:uid, :handle)")
    sql_host_date = text("INSERT INTO writer_dates (uid, date) VALUES (:uid, :date)")

    with connect_to_db() as db:
        # Perform the insertion using a transaction
        # since both parts are required for it to be successful
        try:
            # Reach into sqlalchemy to perform a transaction as Records
            # utterly fails to properly support this
            with create_transaction(db) as tx:
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


def delete(uid: str) -> bool:
    """Delete a Host from the database by their Twitter ID.

    Due to database FK constraints, this will only succeed
    if the Host does not have any Prompts associated with them.
    The presence of any Prompts will stop all deletion so as to
    prevent orphaned records or an incomplete record."""
    sql = "DELETE FROM writers WHERE uid = :uid"
    try:
        with connect_to_db() as db:
            db.query(sql, uid=uid)
            return True
    except IntegrityError:
        return False


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
    """Get the Host for the exact date given."""
    sql = """
    SELECT writers.uid, handle, writer_dates.date
    FROM writers
        JOIN writer_dates ON writer_dates.uid = writers.uid
    WHERE writer_dates.date = :date
    """
    with connect_to_db() as db:
        return [Host(host) for host in db.query(sql, date=date)]


def get_by_year(year: str) -> List[Host]:
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
