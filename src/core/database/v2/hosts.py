from calendar import monthrange
from datetime import date
from typing import TypedDict

from sqlalchemy.exc import NoResultFound
from sqlalchemy.sql import func

from src.core.database.models import Host, HostDate, Prompt, db
from src.core.helpers import twitter_v2_api


__all__ = [
    "current",
    "delete",
    "delete_date",
    "get",
    "get_all",
    "get_by_calendar_month",
    "get_by_date",
    "get_by_year",
    "exists",
    "update",
]


class _HostingPeriod(TypedDict):
    start: int
    end: int


def __hosting_periods_for_month(date: date) -> list[_HostingPeriod]:
    """Determine the Hosting periods for this month."""
    # Always automatically get the last day of the month for determining
    # the end of the second Host's Hosting period
    last_day_of_month = monthrange(date.year, date.month)[1]

    # Because February is a shorter month, the Hosting period is a little different
    if date.month == 2:
        return [
            _HostingPeriod(start=1, end=14),
            _HostingPeriod(start=15, end=last_day_of_month),
        ]

    return [
        _HostingPeriod(start=1, end=15),
        _HostingPeriod(start=16, end=last_day_of_month),
    ]


def __hosting_period_for_date(date: date) -> _HostingPeriod:
    """Get the Hosting period for the given date."""
    hosting_periods = __hosting_periods_for_month(date)

    # If the current day is between the start and (exclusive) end,
    # we are in the first Host's period
    if hosting_periods[0]["start"] <= date.day < hosting_periods[1]["start"]:
        return hosting_periods[0]

    # Except it's not in that first range, so we're in the second Host's period
    return hosting_periods[1]


def create(handle: str) -> Host | None:
    """Create a new Host.

    This will fail if the Host already exists or the Twitter user ID cannot be found.
    """
    # Attempt to get the user ID from the Twitter API
    api = twitter_v2_api()
    host = api.get_user(username=handle)

    # That username couldn't be found
    if host.errors:
        return None

    # Create the Host. A database level unique constraint
    # will stop duplicate Hosts from being created
    host = Host(handle=handle, twitter_uid=host.data.id)
    db.session.add(host)
    db.session.commit()
    return host


def create_date(handle: str, date: date) -> bool:
    """Create a Hosting Date for the given Host.

    This will fail if the Host does not exist or a Host has already
    been assigned to that date.
    """
    # We can't create a Hosting date for a Host that does not exist
    try:
        qs = db.select(Host).filter_by(handle=handle)
        uid = db.session.execute(qs).scalar_one()._id
    except NoResultFound:
        return False

    # We can't create a Hosting date if a Host is already assigned to it
    if db.session.execute(db.select(HostDate).filter_by(date=date)).first() is not None:
        return False

    # Create the Hosting date
    db.session.add(HostDate(host_id=uid, date=date))
    db.session.commit()
    return True


def current() -> Host | None:
    """Determine the current Host.

    If there is no Host recording for now, this will return None.
    """
    # Always start by checking if there is a Host assigned to this single day.
    # This is not a common occurrence but it has happened, and we don't want
    # to prevent it from happening again in the future.
    today = date.today()
    if host := get_by_date(today):
        return host

    # If we don't have a host assigned to today, we need to determine the starting date
    # for the current hosting period and use that to get the current host
    host_start_date = today.replace(day=__hosting_period_for_date(today)["start"])
    return get_by_date(host_start_date)


def delete(handle: str) -> bool:
    """Delete a Host from the database by their Twitter ID.

    Due to database FK constraints, this will only succeed
    if the Host does not have any Prompts associated with them.
    The presence of any Prompts will stop all deletion so as to
    prevent orphaned records or an incomplete record.
    """
    # We can't delete a Host that does not exist
    try:
        host = db.session.execute(db.select(Host).filter_by(handle=handle)).scalar_one()
    except NoResultFound:
        return False

    # We can't delete a Host if they have assigned Hosting dates
    if host.dates:
        return False

    # We can delete this Host
    db.session.delete(host)
    db.session.commit()
    return True


def delete_date(handle: str, given_date: date) -> bool:
    """Delete a Hosting Date assigned to a Host.

    Due to database FK constraints, this will only succeed
    if the Host is actually assigned to the Hosting period and
    the Host does not have any Prompts associated with them during that time.
    Failure to meet these requirements  will stop all deletion
    so as to prevent orphaned records or an incomplete record.
    """
    # We can't delete a Hosting Date for a Host that does not exist
    try:
        host = db.session.execute(db.select(Host).filter_by(handle=handle)).scalar_one()
    except NoResultFound:
        return False

    # We can't delete a Hosting Date if it is not recorded
    # or they are not assigned to it
    try:
        hdate = [hd for hd in host.dates if hd.date == given_date][0]
    except IndexError:
        return False

    # Determine the Hosting period for the given date
    hp = __hosting_period_for_date(given_date)
    hp_start = date(given_date.year, given_date.month, hp["start"])
    hp_end = date(given_date.year, given_date.month, hp["end"])

    # We can't delete a Hosting Date if the Host
    # has given out a Prompt during the Hosting period
    qs = db.select(Prompt._id).filter(
        Prompt.host_id == host._id,
        Prompt.date >= hp_start,
        Prompt.date <= hp_end,
    )
    prompt = db.session.execute(qs).first()
    if prompt is not None:
        return False

    # We can delete this Hosting Date
    db.session.delete(hdate)
    db.session.commit()
    return True


def get(handle: str) -> Host | None:
    """Get an individual Host and all Hosting dates by a Twitter handle."""
    # Get the Host's info
    try:
        host = db.session.execute(db.select(Host).filter_by(handle=handle)).scalar_one()
    except NoResultFound:
        return None

    # Pull the Hosting Dates for the Host, ensuring to take out any future dates
    today = date.today()
    host.dates = [hd for hd in host.dates if hd.date <= today]
    return host


def get_all() -> list[Host]:
    """Get all recorded Hosts."""
    return db.session.execute(db.select(Host)).scalars().all()


def get_by_calendar_month(year: int, month: int) -> list[Host]:
    """Get all the Hosts in a year-month combination."""
    qs = (
        db.select(Host)
        .join(HostDate)
        .filter(
            func.year(HostDate.date) == year,
            func.month(HostDate.date) == month,
            HostDate.date <= date.today(),
        )
        .order_by(HostDate.date)
    )
    return db.session.execute(qs).scalars().all()


def get_by_date(date: date) -> Host | None:
    """Get the Host for the given date.

    Unlike Prompts, there are no recorded instances of two Hosts giving out
    two Prompts on the same day. As a result, this is a one-to-one mapping
    between the Hosting Date and the Host.
    """
    try:
        return (
            db.session.execute(db.select(HostDate).filter_by(date=date))
            .scalar_one()
            .host
        )
    except NoResultFound:
        return None


def get_by_year(year: int) -> list[Host]:
    """Get a list of all Hosts for a given year."""
    qs = (
        db.select(Host)
        .join(HostDate)
        .filter(func.year(HostDate.date) == year, HostDate.date <= date.today())
        .order_by(HostDate.date)
    )
    return db.session.execute(qs).scalars().all()


def exists(handle: str) -> bool:
    """Determine if a Host has been recorded in the system."""
    qs = db.select(Host._id).filter_by(handle=handle)
    return bool(db.session.execute(qs).first())


def update(handle: str, new_handle: str) -> bool:
    """Update a Host's Twitter handle."""
    # We can't update a Host that doesn't exist
    try:
        host = db.session.execute(db.select(Host).filter_by(handle=handle)).scalar_one()
    except NoResultFound:
        return False

    host.update_with({"handle": new_handle})
    db.session.commit()
    return True
