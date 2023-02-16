from datetime import date

from sqlalchemy.orm.exc import NoResultFound

from src.core.database.models import Prompt, PromptMedia, db
from src.core.database.v2 import hosts


__all__ = ["create", "delete", "exists", "get_by_date", "get_current"]


def create(info: dict) -> Prompt | None:
    """Create a new Prompt."""

    # Start by extracting Media and Host info from the Prompt.
    # We'll deal with the after we create the Prompt
    media = info.pop("media")

    # Get the Host who gave out this Prompt
    host = hosts.get(info.pop("host_handle"))
    if host is None:
        return None

    # Create the Prompt itself
    prompt = Prompt(host=host, **info)
    db.session.add(prompt)

    # If this Prompt has media attached to it, we need to keep
    # a record of all provided items
    # TODO: Proper media file names, see v1 prompt route code
    if media is not None:
        for item in media:
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


def delete(_id: int) -> bool:
    """Delete a Prompt from the database by the Prompt ID.

    This will fail if the given Prompt does not exist.

    A database FK constraint will ensure any associated media records is also deleted.
    """
    # We can't delete a Prompt that does not exist
    try:
        prompt = Prompt.query.filter_by(_id=_id).one()
    except NoResultFound:
        return False

    # Delete the Prompt and any associated Media records
    db.session.delete(prompt)
    db.session.commit()
    return True


def exists(prompt_date: date) -> bool:
    """Determine if a Prompt has been recorded for this date."""
    return bool(Prompt.query.filter_by(date=prompt_date).count())


def update():
    ...


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
