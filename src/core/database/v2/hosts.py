from datetime import date

from sqlalchemy.orm.exc import NoResultFound

from src.core.database.models import Host, HostingDate, Prompt, db


__all__ = [
    "by_date",
    "current",
    "delete",
    "get",
    "get_all",
]


def __hosting_start_date(day: date) -> int:
    """Determine the starting date for this Hosting period."""
    # Determine the Hosting period for the current month.
    # In February only, Hosts begin on the 1st and 15th,
    # while for all other months, Hosts begin on the 1st and 16th
    start_dates = (1, 15) if day.month == 2 else (1, 16)

    # If the current day is between the start and (exclusive) end,
    # we are in the first Host's period
    if start_dates[0] <= day.day < start_dates[1]:
        return start_dates[0]

    # Except it's not in that first range, so we're in the second Host's period
    return start_dates[1]


def by_date(date: date) -> list[Host]:
    """Get all of the Hosts for the given date.

    While the majority of the time this will only return a single item
    in the list, historically, there have been days where multiple Hosts
    gave out a prompt on the same day. We cannot merely support the modern
    day prompt format of a string one Host per day, hence, it's a list.
    """
    return Host.query.join(HostingDate).filter(HostingDate.date == date).all()


def current() -> Host | None:
    """Determine the current Host.

    If there is no Host recording for now, this will return None.
    """
    # Always start by checking if there is a Host assigned to this single day.
    # This is not a common occurrence but it has happened, and we don't want
    # to prevent it from happening again in the future.
    today = date.today()
    if host := by_date(today):
        return host[0]

    # If we don't have a host assigned to today, we need to determine the starting date
    # for the current hosting period and use that to get the current host
    host_start_date = today.replace(day=__hosting_start_date(today))
    try:
        return by_date(host_start_date)[0]
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


def get(handle: str) -> Host | None:
    """Get an individual Host and all Hosting dates by a Twitter handle."""
    try:
        host = Host.query.filter(Host.handle == handle).one()

    # That host doesn't exist
    except NoResultFound:
        return None

    # TODO: Once we upgrade to Flask-SQLAlchemy 3.0+,
    # revise this to only pull the `HostingDate.date` column
    dates = [r.date for r in HostingDate.query.filter_by(uid=host.uid).all()]
    host.dates = dates
    return host


def get_all() -> list[Host]:
    """Get all recorded Hosts."""
    return Host.query.all()
