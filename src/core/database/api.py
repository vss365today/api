from src.core.database import __connect_to_db


__all__ = [
    "api_key_has_permission",
    "api_key_is_valid",
]


def api_key_has_permission(route: str, token: str) -> bool:
    """Determine if the given API key has permission to access a route."""
    sql = f"SELECT has_{route} AS has_permission FROM api_keys WHERE token = :token"
    with __connect_to_db() as db:
        return bool(db.query(sql, token=token).one()[0])


def api_key_is_valid(token: str) -> bool:
    """Determine if the given API key is valid."""
    sql = "SELECT 1 FROM api_keys WHERE token = :token"
    with __connect_to_db() as db:
        return bool(db.query(sql, token=token).one())
