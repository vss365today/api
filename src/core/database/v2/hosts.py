from datetime import date
from src.core.database.models import Host, HostingDate


__all__ = ["delete"]


def host_by_date(handle: str, date: date):
    ...


# SELECT writers.uid, handle
# FROM writers
#     JOIN writer_dates ON writer_dates.uid = writers.uid
# WHERE writer_dates.date = :date


def current_host() -> Host | None:
    """Determine the current Host.

    If there is no Host recording for now, this will return None.
    """

    def _get(date: date) -> Host | None:
        return Host.query.join(HostingDate).filter(HostingDate.date == date).first()

    # Always start by checking if there is a Host assigned to this single day.
    # This is not a common occurrence but it has happened, and we don't want
    # to prevent it from happening again in the future.
    today = date.today()
    if host := _get(today):
        return host

    # If we don't have a host assigned to today, we need to determine the starting date
    # for the current hosting period and use that to get the current host
    host_start_date = today.replace(day=hosting_start_date(today))
    return _get(host_start_date)


def hosting_start_date(day: date) -> int:
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


def delete(handle: str) -> bool:
    """Delete a Host from the database by their Twitter ID.

    Due to database FK constraints, this will only succeed
    if the Host does not have any Prompts associated with them.
    The presence of any Prompts will stop all deletion so as to
    prevent orphaned records or an incomplete record.
    """
    # Host.query.delete()
    ...
