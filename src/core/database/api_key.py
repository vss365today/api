from src.core.database import __connect_to_db


__all__ = [
    "has_permission",
    "is_valid",
]


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
