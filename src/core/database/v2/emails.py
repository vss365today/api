from flask import current_app
from sqlalchemy.exc import DataError

from src.core.database.models import Email, db


__all__ = ["create", "delete", "exists", "get_all"]


def create(email: str) -> bool:
    """Add an email address."""
    try:
        db.session.add(Email(email=email))
        db.session.commit()
        current_app.logger.debug("New email added to subscription list.")
        return True

    # We hit some DB error
    except DataError as exc:
        db.session.rollback()
        current_app.logger.exception(exc)
        return False


def delete(email: str) -> bool:
    """Remove an email address."""
    if exists(email):
        db.session.delete(Email.query.filter_by(email=email).first())
        db.session.commit()
        current_app.logger.debug("Email removed from subscription list.")
        return True

    current_app.logger.error("Email unable to be removed from subscription list.")
    return False


def exists(email: str) -> bool:
    """Determine if an email address exists."""
    return Email.query.filter_by(email=email).first() is not None


def get_all() -> list[Email]:
    """Get all email addresses."""
    return Email.query.order_by(Email.email).all()
