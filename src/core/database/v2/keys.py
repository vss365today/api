from secrets import token_hex

from flask import current_app
from sqlalchemy import inspect
from sqlalchemy.exc import DataError, NoResultFound

from src.core.database.models import ApiKey, ApiKeyHistory, db


__all__ = [
    "available_permissions",
    "can_access",
    "create",
    "delete",
    "exists",
    "get",
    "get_all",
    "update",
]


def available_permissions() -> list[str]:
    """List all permissions that can be used to protect an endpoint."""
    return [
        c.removeprefix("has_")
        for c in inspect(ApiKey).columns.keys()
        if c.startswith("has_")
    ]


def can_access(token: str, perms: set) -> bool:
    """Determine if the given API key has all permissions needed to access an endpoint."""
    filters = [getattr(ApiKey, f"has_{perm}") == 1 for perm in perms]
    qs = db.select(ApiKey).filter(*filters, ApiKey.token == token)
    try:
        db.session.execute(qs).scalar_one()
        return True
    except NoResultFound:
        return False


def create(data: dict) -> dict | None:
    """Create an API key with specified permissions."""
    try:
        new_token = token_hex()
        key = ApiKey(token=new_token, **data)
        db.session.add(key)
        db.session.commit()
        current_app.logger.debug("New API key created.")
        return {"token": new_token}

    # We hit some DB error
    except DataError as exc:
        db.session.rollback()
        current_app.logger.exception(exc)
        return None


def delete(token: str) -> bool:
    """Delete a key."""
    if exists(token):
        db.session.delete(get(token))
        db.session.commit()
        current_app.logger.debug("API key deleted.")
        return True

    current_app.logger.error("API key unable to be deleted.")
    return False


def exists(token: str) -> bool:
    """Determine if a key exists."""
    return (
        db.session.execute(db.select(ApiKey._id).filter_by(token=token)).first()
        is not None
    )


def get(token: str) -> ApiKey | None:
    """Get a single key."""
    return (
        db.session.execute(db.select(ApiKey).filter_by(token=token)).scalars().first()
    )


def get_all() -> list[ApiKey]:
    """Get all recorded API key's permissions."""
    return db.session.execute(db.select(ApiKey).order_by(ApiKey._id)).scalars().all()


def update(data: dict) -> None:
    """Update a single key."""
    # Get the current key object
    token = data.pop("token")
    key = get(token)

    # Record the key's current permissions for auditing purposes
    original_info = key.as_dict()
    original_info["key_id"] = original_info["_id"]
    del original_info["_id"]
    del original_info["desc"]
    del original_info["token"]
    del original_info["date_created"]
    db.session.add(ApiKeyHistory(**original_info))
    current_app.logger.debug(
        f"API key {original_info['key_id']} former permissions archived."
    )

    # Update the key with the permission changes and save everything
    key.update_with(data)
    db.session.commit()
    current_app.logger.debug(
        f"API key {original_info['key_id']} new permissions recorded."
    )
    return None
