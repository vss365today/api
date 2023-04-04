from datetime import datetime
from typing import Any, Literal, TypeAlias

from sqlalchemy.exc import DataError, IntegrityError

from src.core.database.models import quick_sql
from src.core.helpers import twitter_v2_api
from src.core.models.v1.Host import Host


__all__ = [
    "create",
    "create_date",
    "delete",
    "delete_date",
    "exists",
    "exists_date",
    "get",
    "get_all",
    "get_by_date",
    "get_by_year",
    "get_by_year_month",
    "get_date",
    "lookup",
    "update",
]


Host2: TypeAlias = dict[str, Any]


def create(host_info: dict) -> Host2 | None:
    """Create a new Host."""
    sql = "INSERT INTO writers (uid, handle) VALUES (:uid, :handle)"
    try:
        quick_sql.query(sql, uid=host_info["uid"], handle=host_info["handle"])
        return Host(**host_info).as_dict()
    except DataError as exc:
        print(exc)
        return None


def create_date(host_info: dict) -> bool:
    """Create a new hosting date."""
    sql = """INSERT INTO writer_dates (
        uid, date
    ) VALUES (
        :uid, STR_TO_DATE(:date, '%Y-%m-%d 00:00:00')
    )"""
    try:
        quick_sql.query(sql, uid=host_info["uid"], date=host_info["date"])
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
        quick_sql.query(sql, uid=uid)
        return True
    except IntegrityError:
        return False


def delete_date(uid: str, date: str) -> Literal[True]:
    """Delete a specific date for a Host."""
    sql = "DELETE FROM writer_dates WHERE uid = :uid AND date = :date"
    quick_sql.query(sql, uid=uid, date=date)
    return True


def exists(*, uid: str = "", handle: str = "") -> bool:
    """Find an existing Host."""
    sql = "SELECT 1 FROM writers WHERE uid = :uid OR handle = :handle"
    return bool(quick_sql.query(sql, uid=uid, handle=handle).first())


def exists_date(uid: str, date: str) -> bool:
    """Find an existing hosting date for the Host."""
    sql = """
    SELECT 1
    FROM writer_dates
    WHERE
        uid = :uid AND
        date = STR_TO_DATE(:date, '%Y-%m-%d')
    """
    return bool(quick_sql.query(sql, uid=uid, date=date).first())


def get(*, uid: str = "", handle: str = "") -> Host2 | None:
    """Get Host info by either their Twitter ID or handle."""
    sql = """
    SELECT writers.uid, handle
    FROM writers
    WHERE writers.uid = :uid OR UPPER(handle) = UPPER(:handle)
    """
    r = quick_sql.query(sql, uid=uid, handle=handle).one()
    return Host(**r).as_dict() if r is not None else None


def get_all() -> list[Host2]:
    """Get a list of all Hosts."""
    sql = """
    SELECT writers.uid, handle
    FROM writers
    ORDER BY handle
    """
    return [Host(**host).as_dict() for host in quick_sql.query(sql)]


def get_by_date(date: str) -> Host2 | None:
    """Get the Host for the given date."""
    sql = """
    SELECT writers.uid, handle
    FROM writers
        JOIN writer_dates ON writer_dates.uid = writers.uid
    WHERE writer_dates.date = :date
    """
    r = quick_sql.query(sql, date=date).one()
    return Host(**r).as_dict() if r is not None else None


def get_by_year(year: str) -> list[Host2]:
    """Get a list of all Hosts for a given year."""
    sql = """
    SELECT writers.uid, handle
    FROM writers
        JOIN writer_dates ON writer_dates.uid = writers.uid
    WHERE YEAR(writer_dates.date) = :year
        AND DATE_FORMAT(writer_dates.date, '%Y-%m') <=
            DATE_FORMAT(CURRENT_TIMESTAMP(), '%Y-%m')
    ORDER BY writer_dates.date ASC
    """
    return [Host(**host).as_dict() for host in quick_sql.query(sql, year=year)]


def get_by_year_month(year: str, month: str) -> list[Host2]:
    """Get all the Hosts in a year-month combination."""
    sql = """
    SELECT writers.uid, handle
    FROM writers
        JOIN writer_dates ON writer_dates.uid = writers.uid
    WHERE
        YEAR(writer_dates.date) = :year
        AND MONTH(writer_dates.date) = :month
    """
    return [
        Host(**host).as_dict() for host in quick_sql.query(sql, year=year, month=month)
    ]


def get_date(handle: str) -> list[datetime]:
    """Get the hosting periods for the given Host."""
    sql = """
    SELECT date
    FROM writer_dates
    WHERE uid = (
        SELECT uid FROM writers
        WHERE handle = :handle
    )
    ORDER BY date DESC
    """
    return [
        datetime.combine(record["date"], datetime.min.time())
        for record in quick_sql.query(sql, handle=handle)
    ]


def lookup(username: str) -> str | Literal[False]:
    """Get the Host's Twitter user ID."""
    api = twitter_v2_api()
    host = api.get_user(username=username)

    # That username couldn't be found
    if host.errors:
        return False
    return str(host.data.id)


def update(host_info: dict) -> bool:
    """Update a Host's handle."""
    sql = "UPDATE writers SET handle = :handle WHERE uid = :uid"
    try:
        quick_sql.query(sql, uid=host_info["uid"], handle=host_info["handle"])
        return True
    except DataError as exc:
        print(exc)
        return False
