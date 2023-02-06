from datetime import date
from sqlalchemy.orm.exc import NoResultFound

from src.core.database.models import Prompt, PromptMedia, db


__all__ = ["delete", "get_by_date", "get_current"]


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


def create(info: dict):

    media = info.pop("media")
    prompt = Prompt(**info)
    db.session.add(prompt)

    pm = PromptMedia(**media)
    db.session.add(pm)

    db.session.commit()

    prompt.media = pm

    # TODO: Add navigation obj

    return prompt


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
