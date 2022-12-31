from secrets import token_hex
from typing import Literal

from flask import current_app
from sqlalchemy.exc import DataError

from src.core.database.models import ApiKey, ApiKeyHistory, db


__all__ = ["can_access", "create", "delete", "exists", "get", "get_all", "update"]


def can_access(route: str, token: str) -> bool:
    """Determine if the given API key has permission to access a route."""
    route = "archive"
    return (
        ApiKey.query.with_entities(getattr(ApiKey, f"has_{route}"))
        .filter_by(token=token)
        .first()[0]
    )


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
        db.session.delete(ApiKey.query.filter_by(token=token).first())
        db.session.commit()
        current_app.logger.debug("API key deleted.")
        return True

    current_app.logger.error("API key unable to be deleted.")
    return False


def exists(token: str) -> bool:
    """Determine if a key exists."""
    return ApiKey.query.filter_by(token=token).first() is not None


def get(token: str) -> ApiKey | None:
    """Get a single key."""
    return ApiKey.query.filter_by(token=token).first()


def get_all() -> list[ApiKey]:
    """Get all recorded API key's permissions."""
    return ApiKey.query.order_by(ApiKey._id).all()


def update(data: dict) -> None:
    """Update a single key."""
    # Set up a query to get the current key object but don't fetch it
    token = data.pop("token")
    key = ApiKey.query.filter_by(token=token)

    # Run the query to get the current object and record it for auditing purposes
    original_info = key.first().as_dict()
    original_info["key_id"] = original_info["_id"]
    del original_info["_id"]
    del original_info["desc"]
    del original_info["token"]
    del original_info["date_created"]
    db.session.add(ApiKeyHistory(**original_info))
    current_app.logger.debug(
        f"API key {original_info['key_id']} former permissions archived."
    )

    # Go back to our original object, update it with
    # the key changes, and save everything
    key.update(data)
    db.session.commit()
    current_app.logger.debug(
        f"API key {original_info['key_id']} new permissions recorded."
    )
    return None
