from sqlalchemy.orm.exc import NoResultFound

from src.core.database.models import Prompt, PromptMedia, db


__all__ = ["delete"]


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
