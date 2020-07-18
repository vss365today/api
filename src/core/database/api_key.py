from typing import Dict
from secrets import token_hex

from sqlalchemy.exc import DataError

from src.core.database import __connect_to_db


__all__ = ["create", "delete", "exists", "has_permission", "get", "update"]


def __int_to_bool(records: dict) -> dict:
    for k, v in records.items():
        if isinstance(v, int):
            records[k] = bool(v)
    return records


def __bool_to_int(records: dict) -> dict:
    for k, v in records.items():
        if isinstance(v, bool):
            records[k] = int(v)
    return records


def create(permissions: dict) -> Dict[str, str]:
    """Create an API key with specified permissions."""
    # Convert the boolean fields to integers
    permissions = __bool_to_int(permissions)

    # Generate a new token for the API key
    new_token = token_hex()

    # Create the record
    sql = """INSERT INTO api_keys (
        token, `desc`, has_api_key, has_archive,
        has_broadcast, has_host, has_prompt,
        has_subscription
    ) VALUES (
        :token, :desc, :has_api_key, :has_archive,
        :has_broadcast, :has_host, :has_prompt,
        :has_subscription
    )
    """
    try:
        with __connect_to_db() as db:
            db.query(sql, token=new_token, **permissions)
            return {"token": new_token}
    except DataError as exc:
        print(f"API key creation exception: {exc}")
        return {}


def delete(token: str) -> bool:
    """Delete an API key."""
    sql = "DELETE FROM api_keys WHERE token = :token"
    with __connect_to_db() as db:
        return bool(db.query(sql, token=token).one())


def exists(token: str) -> bool:
    """Determine if an API key exists."""
    sql = "SELECT 1 FROM api_keys WHERE token = :token"
    with __connect_to_db() as db:
        return bool(db.query(sql, token=token).one())


def get(token: str) -> dict:
    """Get an API key's permissions."""
    sql = "SELECT * FROM api_keys WHERE token = :token LIMIT 1"
    with __connect_to_db() as db:
        info = db.query(sql, token=token).one(as_dict=True)

    # The requested key has information
    if info:
        # Delete unneeded info from the result set
        del info["id"]
        del info["token"]

        # Convert all boolean columns into proper booleans
        info = __int_to_bool(info)
    return info


def has_permission(route: str, token: str) -> bool:
    """Determine if the given API key has permission to access a route."""
    sql = f"SELECT has_{route} FROM api_keys WHERE token = :token"
    with __connect_to_db() as db:
        return bool(db.query(sql, token=token).one()[0])


def update():
    """Update an API key's permissions."""
    raise NotImplementedError
