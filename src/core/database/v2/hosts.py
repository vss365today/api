from calendar import monthrange
from datetime import date
from typing import TypedDict

from sqlalchemy.orm.exc import NoResultFound

from src.core.database.models import Host, HostingDate, Prompt, db


__all__ = [
    "current",
    "delete",
    "delete_date",
    "get",
    "get_by_date",
    "get_all",
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


def current() -> Host | None:
    """Determine the current Host.

    If there is no Host recording for now, this will return None.
    """
    # Always start by checking if there is a Host assigned to this single day.
    # This is not a common occurrence but it has happened, and we don't want
    # to prevent it from happening again in the future.
    today = date.today()
    if host := get_by_date(today):
        return host[0]

    # If we don't have a host assigned to today, we need to determine the starting date
    # for the current hosting period and use that to get the current host
    host_start_date = today.replace(day=__hosting_period_for_date(today)["start"])
    try:
        return get_by_date(host_start_date)[0]
    except IndexError:
        return None


def delete(handle: str) -> bool:
    """Delete a Host from the database by their Twitter ID.

    Due to database FK constraints, this will only succeed
    if the Host does not have any Prompts associated with them.
    The presence of any Prompts will stop all deletion so as to
    prevent orphaned records or an incomplete record.
    """
    # We can't delete a Host that does not exist.
    try:
        host = Host.query.filter_by(handle=handle).one()
    except NoResultFound:
        return False

    # We can't delete a Host if they have assigned Hosting dates
    dates = HostingDate.query.filter_by(uid=host.uid).all()
    if dates:
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
        host = Host.query.filter_by(handle=handle).one()
    except NoResultFound:
        return False

    # We can't delete a Hosting Date if it is not recorded or
    # they are not assigned to it
    try:
        hdate = HostingDate.query.filter_by(uid=host.uid, date=given_date).one()
    except NoResultFound:
        return False

    # Determine the Hosting period for the given date
    hp = __hosting_period_for_date(hdate.date)
    hp_start = date(given_date.year, given_date.month, hp["start"])
    hp_end = date(given_date.year, given_date.month, hp["end"])

    # We can't delete a Hosting Date if the Host
    # has given out a Prompt during the Hosting period
    prompt = Prompt.query.filter(
        Prompt.uid == host.uid,
        Prompt.date >= hp_start,
        Prompt.date <= hp_end,
    ).first()
    if prompt is not None:
        return False

    # We can delete this Hosting Date
    db.session.delete(hdate)
    db.session.commit()
    return True


def get(handle: str) -> Host | None:
    """Get an individual Host and all Hosting dates by a Twitter handle."""
    try:
        host = Host.query.filter_by(handle=handle).one()

    # That host doesn't exist
    except NoResultFound:
        return None

    # TODO: Once we upgrade to Flask-SQLAlchemy 3.0+,
    # revise this to only pull the `HostingDate.date` column
    dates = [r.date for r in HostingDate.query.filter_by(uid=host.uid).all()]
    host.dates = dates
    return host


def get_by_date(date: date) -> list[Host]:
    """Get all of the Hosts for the given date.

    While the majority of the time this will only return a single item
    in the list, historically, there have been days where multiple Hosts
    gave out a prompt on the same day. We cannot merely support the modern
    day prompt format of a string one Host per day, hence, it's a list.
    """
    return Host.query.join(HostingDate).filter(HostingDate.date == date).all()


def get_all() -> list[Host]:
    """Get all recorded Hosts."""
    return Host.query.all()
