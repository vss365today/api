from records import Record

from src.core.database import __connect_to_db


__all__ = ["create", "delete", "has_permission", "get", "is_valid", "update"]


def create(permissions: dict):
    """Create an API key with specified permissions."""
    raise NotImplementedError


def delete(token: str) -> bool:
    """Delete an API key."""
    sql = "DELETE FROM api_keys WHERE token = :token"
    with __connect_to_db() as db:
        return bool(db.query(sql, token=token))


def get(token: str) -> Record:
    """Get an API key's permissions."""
    sql = "SELECT * FROM api_keys WHERE token = :token LIMIT 1"
    with __connect_to_db() as db:
        info = db.query(sql, token=token).one()

    # Delete unneeded from the fetched results
    del info["id"]
    del info["token"]
    return info


def has_permission(route: str, token: str) -> bool:
    """Determine if the given API key has permission to access a route."""
    sql = f"SELECT has_{route} FROM api_keys WHERE token = :token"
    with __connect_to_db() as db:
        return bool(db.query(sql, token=token).one()[0])


def is_valid(token: str) -> bool:
    """Determine if the given API key is valid."""
    sql = "SELECT 1 FROM api_keys WHERE token = :token"
    with __connect_to_db() as db:
        return bool(db.query(sql, token=token).one())


def update():
    """Update an API key's permissions."""
    raise NotImplementedError
