from contextlib import suppress
from datetime import date as date_obj
from datetime import datetime, timedelta
from typing import Any, TypedDict

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, ForeignKey, inspect, select
from sqlalchemy.dialects.mysql import TINYINT
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    column_property,
    mapped_column,
    relationship,
)
from sqlalchemy.types import BigInteger, DateTime, String

__all__ = [
    "ApiKey",
    "ApiKeyHistory",
    "Email",
    "Prompt",
    "PromptMedia",
    "Host",
    "HostDate",
    "db",
]


# Set up the flask-sqlalchemy extension for "new-style" models
class Base(DeclarativeBase): ...


db = SQLAlchemy(model_class=Base)


class PromptNavigation(TypedDict):
    """Typing Hint for Prompt surrounding dates."""

    next: date_obj | None
    previous: date_obj | None


class HelperMethods:
    def as_dict(self) -> dict:
        """Return a model as a dictionary."""
        return {c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs}

    def update_with(self, data: dict[str, Any]) -> None:
        """Update a record with the given data."""
        for k, v in data.items():
            setattr(self, k, v)
        return None


class Host(HelperMethods, db.Model):
    __tablename__ = "hosts"
    __table_args__ = {"comment": "Store the #vss365 Hosts."}

    _id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    handle: Mapped[str] = mapped_column(
        String(30, collation="utf8mb4_unicode_ci"), unique=True
    )
    twitter_uid: Mapped[str] = mapped_column(
        String(40, collation="utf8mb4_unicode_ci"), unique=True
    )

    prompts: Mapped[list["Prompt"]] = relationship(back_populates="host")
    dates: Mapped[list["HostDate"]] = relationship(back_populates="host")

    url = column_property("https://twitter.com/" + handle)


class HostDate(db.Model):
    __tablename__ = "host_dates"
    __table_args__ = {"comment": "Store the hosting dates of #vss365 Hosts."}

    _id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    date: Mapped[date_obj]
    host_id: Mapped[int] = mapped_column(
        ForeignKey("hosts._id", ondelete="CASCADE", onupdate="CASCADE")
    )
    host: Mapped["Host"] = relationship(back_populates="dates")


class Prompt(HelperMethods, db.Model):
    __tablename__ = "prompts"
    __table_args__ = {"comment": "Store the #vss365 Prompts."}

    def __str__(self) -> str:
        return f"Prompt {self._id}, {self.date.isoformat()}, {self.word}"

    _id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    twitter_id: Mapped[str] = mapped_column(
        String(30, collation="utf8mb4_unicode_ci"), unique=True
    )
    date: Mapped[date_obj]
    date_added: Mapped[datetime] = Column(
        DateTime,
        nullable=False,
        default=datetime.now,
        onupdate=datetime.now,
    )
    word: Mapped[str] = mapped_column(String(30, collation="utf8mb4_unicode_ci"))
    content: Mapped[str] = mapped_column(String(2048, collation="utf8mb4_unicode_ci"))
    host_id: Mapped[int] = mapped_column(
        ForeignKey("hosts._id", ondelete="RESTRICT", onupdate="CASCADE")
    )

    host: Mapped["Host"] = relationship(back_populates="prompts")
    media: Mapped[list["PromptMedia"]] = relationship(back_populates="prompt")

    url = column_property(
        "https://twitter.com/"
        + select(Host.handle)
        .where(Host._id == host_id)
        .correlate_except(Host)
        .scalar_subquery()
        + "/status/"
        + twitter_id
    )

    @hybrid_property
    def navigation(self) -> PromptNavigation:
        """Get the previous/next Prompt dates."""
        # Because the previous or next day is not always available,
        # we must be careful to handle NoneType values correctly
        navi = PromptNavigation(next=None, previous=None)
        with suppress(AttributeError):
            navi["previous"] = (
                db.session.execute(
                    db.select(Prompt.date).filter_by(date=self.date - timedelta(days=1))
                )
                .first()
                .date
            )

        # We need to catch the possible `AttributeError` for the next date separately from
        # the previous date because these are separate events, and if we catch them together,
        # we can end up with a case where the whole previous/next information is lost despite
        # us having one of them
        with suppress(AttributeError):
            navi["next"] = (
                db.session.execute(
                    db.select(Prompt.date).filter_by(date=self.date + timedelta(days=1))
                )
                .first()
                .date
            )
        return navi


class PromptMedia(HelperMethods, db.Model):
    __tablename__ = "prompt_media"
    __table_args__ = {"comment": "Store the #vss365 Prompt media."}

    _id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    file: Mapped[str | None] = mapped_column(
        String(512, collation="utf8mb4_unicode_ci")
    )
    alt_text: Mapped[str | None] = mapped_column(
        String(1000, collation="utf8mb4_unicode_ci")
    )
    prompt_id: Mapped[int] = mapped_column(
        ForeignKey("prompts._id", ondelete="CASCADE", onupdate="CASCADE")
    )

    prompt: Mapped["Prompt"] = relationship(back_populates="media")


class Email(db.Model):
    __tablename__ = "emails"
    __table_args__ = {
        "comment": "Store email addresses for those who want Prompt notifications."
    }

    address: Mapped[str] = mapped_column(
        "email",
        String(150, collation="utf8mb4_unicode_ci"),
        primary_key=True,
        unique=True,
    )
    date_added: Mapped[datetime] = Column(DateTime, default=datetime.now)


class ApiKey(HelperMethods, db.Model):
    __tablename__ = "api_keys"
    __table_args__ = {
        "comment": (
            "API keys for accessing protected API endpoints. By default, keys can only "
            "access public, unprotected endpoints and actions. Authorization can be "
            "granted on a granular level for complete control over key permissions."
        )
    }

    _id: Mapped[int] = mapped_column(TINYINT(3), primary_key=True)
    token: Mapped[str] = mapped_column(String(64, "utf8mb4_unicode_ci"), unique=True)
    date_created: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.now,
    )
    desc: Mapped[str | None] = mapped_column(
        String(256, collation="utf8mb4_unicode_ci")
    )
    has_archive: Mapped[bool] = mapped_column(default=False)
    has_hosts: Mapped[bool] = mapped_column("has_host", default=False)
    has_notifications: Mapped[bool] = mapped_column(default=False)
    has_keys: Mapped[bool] = mapped_column(default=False)
    has_prompts: Mapped[bool] = mapped_column("has_prompt", default=False)
    has_emails: Mapped[bool] = mapped_column("has_subscription", default=False)

    history: Mapped[list["ApiKeyHistory"]] = relationship(back_populates="key")


class ApiKeyHistory(db.Model):
    __tablename__ = "audit_api_keys"
    __table_args__ = {"comment": "Audit table to track permission changes to API keys."}

    _id: Mapped[int] = mapped_column(TINYINT(3), primary_key=True)
    key_id: Mapped[int] = mapped_column(
        ForeignKey("api_keys._id", ondelete="CASCADE"),
        index=True,
    )
    date_updated: Mapped[datetime] = Column(
        DateTime,
        nullable=False,
        default=datetime.now,
    )
    has_archive: Mapped[bool] = mapped_column(default=False)
    has_hosts: Mapped[bool] = mapped_column(default=False)
    has_keys: Mapped[bool] = mapped_column(default=False)
    has_notifications: Mapped[bool] = mapped_column(default=False)
    has_prompts: Mapped[bool] = mapped_column(default=False)
    has_emails: Mapped[bool] = mapped_column(default=False)

    key: Mapped["ApiKey"] = relationship(back_populates="history")
