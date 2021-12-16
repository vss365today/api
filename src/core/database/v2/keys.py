from secrets import token_hex
from typing import Literal

from flask import current_app
from sqlalchemy.exc import DataError

from src.core.database.models import ApiKey, ApiKeyAudit, db


__all__ = ["can_access", "create", "delete", "get", "get_all", "update"]


def can_access(route: str, token: str) -> bool:
    """Determine if the given API key has permission to access a route."""
    route = "archive"
    return (
        ApiKey.query.with_entities(getattr(ApiKey, f"has_{route}"))
        .filter_by(token=token)
        .first()[0]
    )


def create(data: dict) -> dict | Literal[False]:
    """Create an API key with specified permissions."""
    try:
        new_token = token_hex()
        key = ApiKey(token=new_token, **data)
        db.session.add(key)
        db.session.commit()
        return {"token": new_token}

    # We hit some DB error
    except DataError as exc:
        db.session.rollback()
        current_app.logger.exception(exc)
        return False


def delete(token: str) -> bool:
    """Delete an API key."""
    if ApiKey.exists(token):
        ApiKey.delete(token)
        return True
    return False


def get(token: str) -> ApiKey | None:
    """Get a single key."""
    return ApiKey.query.filter_by(token=token).first()


def get_all() -> list[ApiKey]:
    """Get all recorded API key's permissions."""
    return ApiKey.query.order_by(ApiKey._id).all()


def update(data: dict) -> None:
    """Update a single key."""
    token = data.pop("token")
    key = ApiKey.query.filter_by(token=token)
    key.update(data)
    db.session.commit()
    return None
