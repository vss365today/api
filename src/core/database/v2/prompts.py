from sqlalchemy.orm.exc import NoResultFound

from src.core.database.models import Prompt, db


__all__ = []


def delete(_id: int) -> bool:
    """Delete a Prompt from the database by the Prompt ID.

    This will fail if the given Prompt does not exist.

    A database FK constraint will ensure any associated media is also deleted.
    """
    # We can't delete a Prompt that does not exist
    try:
        prompt = Prompt.query.filter_by(_id=_id).one()
    except NoResultFound:
        return False

    # Delete the Prompt and any associated Media.
    # TODO: Actually delete the media file(s)
    db.session.delete(prompt)
    db.session.commit()
    return True


def create():
    ...


def update():
    ...
