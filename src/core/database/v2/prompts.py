from datetime import date, datetime
from typing import cast

from sqlalchemy.sql import func
from sqlalchemy.orm.exc import NoResultFound

from src.core.database.models import Host, Prompt, PromptMedia, db
from src.core.database.v2 import hosts
from src.core.helpers import media


__all__ = [
    "create",
    "delete",
    "exists",
    "get_by_date",
    "get_current",
    "get_months",
    "get_years",
    "update",
]


def create(info: dict) -> Prompt | None:
    """Create a new Prompt."""
    # Start by extracting Media info from the Prompt.
    # We'll deal with it after we create the Prompt
    prompt_media = info.pop("media")

    # Get the Host who gave out this Prompt
    host = hosts.get(info.pop("host_handle"))
    if host is None:
        return None

    # Create the Prompt itself
    prompt = Prompt(host=host, **info)
    db.session.add(prompt)

    # If this Prompt has media attached to it, we need to keep
    # a record of all provided items
    if prompt_media is not None:
        for item in prompt_media:
            # Note that we don't respect the `replace` flag in this context.
            # It does not make sense here as we are creating Media for the first time
            pm = PromptMedia(
                prompt=prompt,
                alt_text=item["alt_text"],
                media=item["url"],
            )
            db.session.add(pm)

    # Now that we have everything created, provide the caller
    # with the full Prompt context and info
    db.session.commit()
    return prompt


def delete(prompt_id: int) -> bool:
    """Delete a Prompt from the database by the Prompt ID.

    This will fail if the given Prompt does not exist.

    A database FK constraint will ensure any associated media records is also deleted.
    """
    # We can't delete a Prompt that does not exist
    try:
        prompt = Prompt.query.filter_by(_id=prompt_id).one()
    except NoResultFound:
        return False

    # Delete the Prompt and any associated Media records and files
    db.session.delete(prompt)
    db.session.commit()
    media.delete(prompt["twitter_id"])
    return True


def exists(prompt_date: date) -> bool:
    """Determine if a Prompt has been recorded for this date."""
    return bool(Prompt.query.filter_by(date=prompt_date).count())


def get_by_date(prompt_date: date) -> list[Prompt]:
    """Get all of the Prompts for this date."""
    return Prompt.query.filter_by(date=prompt_date).all()


def get_current() -> list[Prompt]:
    """Get the current Prompt."""
    # Start by determining the newest recorded Prompt date
    # TODO: Once we upgrade to Flask-SQLAlchemy 3.0+,
    # revise this to only pull the `Prompt.date` column
    newest_date = Prompt.query.order_by(Prompt.date.desc()).first().date

    # Now that we have the latest recorded date, nab all the Prompts for it.
    # This really should be a single Prompt under the 2021+ character,
    # bu we cannot be 100% sure of multiple Prompts on a single day
    # ever occurring again, meaning we future-proof this to support
    # multiple Prompts, at risk of YAGNI
    return get_by_date(newest_date)


def get_months(year: int) -> list[int]:
    """Make all Prompts dates for a given year into a unique set.

    For some months in 2017, November 2020, and in 2021 and beyond,
    there are multiple Hosts per month giving out the prompts.
    While the individual dates are stored distinctly,
    we need a unique month list in order to correctly display
    the year browsing page.
    """
    # TODO: Expose this in browse endpoint, not prompts
    # Be sure to filter out any future, as of yet unreleased, Prompt years
    current_year = datetime.now().year
    r = (
        Prompt.query.with_entities(func.month(Prompt.date).label("month"))
        .distinct()
        .filter(
            func.year(Prompt.date) == year,
            func.year(Prompt.date) <= current_year,
        )
        .order_by("month")
    )
    return [month[0] for month in r]


def get_years() -> list[int]:
    """Get a list of years of recorded Prompts."""
    # TODO: Expose this in browse endpoint, not prompts
    # Be sure to filter out any future, as of yet unreleased, Prompt years
    current_year = datetime.now().year
    r = (
        Prompt.query.with_entities(func.year(Prompt.date).label("year"))
        .distinct()
        .filter(func.year(Prompt.date) <= current_year)
        .order_by("year")
    )
    return [year[0] for year in r]


def update(info: dict) -> bool:
    """Update an existing Prompt."""
    # We have to have a Prompt to update
    try:
        prompt_q = Prompt.query.filter_by(_id=info["id"])
        prompt = prompt_q.one()
    except NoResultFound:
        return False

    # If a Host handle if given, we assume we want to change the Prompt association
    if (host_handle := info.pop("host_handle", None)) is not None:
        # That Host doesn't exist in the system, we can't continue on
        if (new_host := hosts.get(host_handle)) is None:
            return False

        # The given prompt Host is different from the recorded Host.
        # Let's presume that means we want to change the Host association
        new_host = cast(Host, new_host)
        if prompt.host != new_host:
            info["host_id"] = new_host._id

    # # Extract any Media info from the Prompt
    # if (prompt_media := info.pop("media", None)) is not None:
    # TODO: This needs working out
    #     ...

    del info["id"]
    prompt_q.update(info)
    db.session.commit()
    return True
