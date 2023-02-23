from datetime import date
from typing import cast

from sqlalchemy.sql import func
from sqlalchemy.orm.exc import NoResultFound

from src.core.database.models import Host, Prompt, PromptMedia, db
from src.core.database.v2 import hosts
from src.core.helpers import media


__all__ = [
    "create",
    "create_media",
    "delete",
    "delete_media",
    "exists",
    "get_by_date",
    "get_current",
    "get_months",
    "get_years",
    "update",
]


def create(info: dict) -> Prompt | None:
    """Create a new Prompt."""
    # Get the Host who gave out this Prompt
    host = hosts.get(info.pop("host_handle"))
    if host is None:
        return None

    # Create the Prompt itself
    prompt = Prompt(host=host, **info)
    db.session.add(prompt)

    # Now that we have everything created, provide the caller
    # with the full Prompt context and info
    db.session.commit()
    return prompt


def create_media(prompt_id: int, media_info: list[dict]) -> bool:
    """Create media files and records for an associated Prompt."""
    # Start by filtering out all media items with invalid URLs.
    # It's ok if invalid media URLs are silently discarded
    media_info = [item for item in media_info if media.is_valid_url(item["url"])]

    # If there's no media to save, we should shortcut
    # the remainder of the process and report all is well
    if not media_info:
        return True

    # If there are any valid media URLs, create a record
    # that associates them with the given Prompt
    media_recorded = []
    for item in media_info:
        pm = PromptMedia(
            prompt_id=prompt_id,
            alt_text=item["alt_text"],
            media=item["url"],
        )
        db.session.add(pm)
        db.session.flush()
        media_recorded.append(pm)

    media_saved = []
    for item in media_recorded:
        # Download the media to its final resting place
        temp_file = media.download_v2(item.media)
        final_file = media.saved_name_v2(prompt_id, item._id, item.media)
        save_result = media.move_v2(temp_file, final_file)
        media_saved.append(save_result)

        # After it is downloaded, we need to update the database record
        # with the proper  media URL. This is a little bit of a chicken
        # and egg problem. We want to save  the media file with the media ID,
        # but to get it, we need to save the media to the database first.
        # Oh well ¯\_(ツ)_/¯
        item.media = final_file

    # If all of the media saved successfully, we can write everything to the database
    if all(media_saved):
        db.session.commit()
        return True

    # But if all of the media *didn't* save correctly, we need to remove all of them
    # so there's no orphan records
    db.session.rollback()
    media.delete_v2(prompt_id)
    return False


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
    media.delete_v2(prompt_id)
    return True


def delete_media(info: dict) -> bool:
    """Delete media files and media records from a Prompt."""
    # We can't delete media that does not exist
    try:
        pm = PromptMedia.query.filter_by(_id=info["media_id"]).one()
    except NoResultFound:
        return False

    # Delete the Prompt and any associated Media records and files
    db.session.delete(pm)
    db.session.commit()
    media.delete_v2(info["id"], info["media_id"])
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
    newest_date = (
        Prompt.query.with_entities(Prompt.date)
        .order_by(Prompt.date.desc())
        .first()
        .date
    )

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
    current_year = date.today().year
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
    current_year = date.today().year
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
