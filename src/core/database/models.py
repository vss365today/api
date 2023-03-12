from contextlib import suppress
from datetime import date as date_obj, datetime, timedelta
from typing import TypedDict

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, ForeignKey, inspect
from sqlalchemy.dialects.mysql import TINYINT
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import Boolean, BigInteger, Date, DateTime, String


db = SQLAlchemy()


__all__ = [
    "ApiKey",
    "ApiKeyHistory",
    "Email",
    "PromptLegacy",
    "Writer",
    "WriterDate",
    "Prompt",
    "PromptMedia",
    "Host",
    "HostDate",
    "db",
]


class PromptNavigation(TypedDict):
    """Typing Hint for Prompt surrounding dates."""

    next: date_obj | None
    previous: date_obj | None


class HelperMethods:
    def as_dict(self) -> dict:
        """Return a model as a dictionary."""
        return {c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs}


class ApiKey(HelperMethods, db.Model):
    __tablename__ = "api_keys"
    __table_args__ = {
        "comment": (
            "API keys for accessing protected API endpoints. By default, keys can only access "
            "public, unprotected endpoints and actions. Authorization can be granted on a granular "
            "level for complete control over key permissions."
        )
    }

    _id = Column(TINYINT(3), primary_key=True)
    token = Column(String(64, "utf8mb4_unicode_ci"), nullable=False, unique=True)
    date_created = Column(DateTime, nullable=False, default=datetime.now)
    desc = Column(String(256, "utf8mb4_unicode_ci"))
    has_archive = Column(Boolean, nullable=False, default=False)
    has_notifications = Column("has_broadcast", Boolean, nullable=False, default=False)
    has_hosts = Column("has_host", Boolean, nullable=False, default=False)
    has_keys = Column(Boolean, nullable=False, default=False)
    has_prompts = Column("has_prompt", Boolean, nullable=False, default=False)
    has_settings = Column(Boolean, nullable=False, default=False)
    has_emails = Column("has_subscription", Boolean, nullable=False, default=False)

    history = relationship("ApiKeyHistory", backref="history")


class Writer(db.Model):
    __tablename__ = "writers"

    uid = Column(String(30, "utf8mb4_unicode_ci"), primary_key=True, unique=True)
    handle = Column(String(20, "utf8mb4_unicode_ci"), nullable=False)

    @hybrid_property
    def url(self) -> str:
        """Create a Twitter URL to the Host's profile."""
        return f"https://twitter.com/{self.handle}"

    @classmethod
    def get_handle(cls, /, uid: str) -> str:
        """Get a Host's user ID from their handle."""
        return cls.query.filter_by(id=uid).first().handle

    @classmethod
    def get_uid(cls, /, handle: str) -> str:
        """Get a Host's handle from their user ID."""
        return cls.query.filter_by(handle=handle).first().uid


class WriterDate(db.Model):
    __tablename__ = "writer_dates"

    uid = Column(
        ForeignKey("writers.uid", ondelete="CASCADE", onupdate="CASCADE"),
        primary_key=True,
        nullable=False,
    )
    date = Column(Date, primary_key=True, nullable=False)

    writer = relationship("Writer")


class ApiKeyHistory(db.Model):
    __tablename__ = "audit_api_keys"
    __table_args__ = {"comment": "Audit table to track permission changes to API keys."}

    _id = Column(TINYINT(3), primary_key=True)
    key_id = Column(
        ForeignKey("api_keys._id", ondelete="CASCADE"), nullable=False, index=True
    )
    date_updated = Column(DateTime, nullable=False, default=datetime.now)
    has_archive = Column(Boolean, nullable=False, default=False)
    has_hosts = Column(Boolean, nullable=False, default=False)
    has_keys = Column(Boolean, nullable=False, default=False)
    has_notifications = Column(Boolean, nullable=False, default=False)
    has_prompts = Column(Boolean, nullable=False, default=False)
    has_settings = Column(Boolean, nullable=False, default=False)
    has_emails = Column(Boolean, nullable=False, default=False)

    key = relationship("ApiKey", backref="key")


class PromptLegacy(db.Model):
    __tablename__ = "prompts"
    __table_args__ = {"comment": "Legacy table for storing prompts."}

    tweet_id = Column(String(25, "utf8mb4_unicode_ci"), primary_key=True, unique=True)
    date = Column(Date, nullable=False)
    uid = Column(
        ForeignKey("writers.uid", onupdate="CASCADE"), nullable=False, index=True
    )
    content = Column(String(2048, "utf8mb4_unicode_ci"), nullable=False)
    word = Column(String(30, "utf8mb4_unicode_ci"), nullable=False)
    media = Column(String(512, "utf8mb4_unicode_ci"))
    media_alt_text = Column(String(1000, "utf8mb4_unicode_ci"))
    date_added = Column(
        DateTime,
        nullable=False,
        default=datetime.now,
        onupdate=datetime.now,
    )

    writer = relationship("Writer")

    @hybrid_property
    def url(self) -> str:
        """Create a Twitter URL to the Host's profile."""
        return f"https://twitter.com/{self.handle}/{self.tweet_id}"


# 2023+ models
class Host(db.Model):
    __tablename__ = "hosts"
    __table_args__ = {"comment": "Store the #vss365 Hosts."}

    _id = Column(BigInteger, primary_key=True, autoincrement=True)
    handle = Column(String(30, "utf8mb4_unicode_ci"), nullable=False, unique=True)
    twitter_uid = Column(String(40, "utf8mb4_unicode_ci"), nullable=False, unique=True)

    prompts = relationship("Prompt", backref="prompts", lazy="dynamic")

    @hybrid_property
    def url(self) -> str:
        """Create a Twitter URL to the Host's profile."""
        return f"https://twitter.com/{self.handle}"

    @classmethod
    def get_handle(cls, /, id: str) -> str:
        """Get a Host's handle from their user ID."""
        return cls.query.filter_by(_id=id).first().handle

    @classmethod
    def get_id(cls, /, handle: str) -> str:
        """Get a Host's user ID from their handle."""
        return cls.query.filter_by(handle=handle).first()._id

    @classmethod
    def get_twitter_uid(cls, /, handle: str) -> str:
        """Get a Host's Twitter ID from their handle."""
        return cls.query.filter_by(handle=handle).first().twitter_uid


class HostDate(db.Model):
    __tablename__ = "host_dates"
    __table_args__ = {"comment": "Store the hosting dates of #vss365 Hosts."}

    _id = Column(BigInteger, primary_key=True, autoincrement=True)
    date = Column(Date, nullable=False)
    host_id = Column(
        ForeignKey("hosts._id", ondelete="RESTRICT", onupdate="CASCADE"),
        nullable=False,
    )

    host = relationship("Host", backref="host")


class Prompt(HelperMethods, db.Model):
    __tablename__ = "prompts_new"
    __table_args__ = {"comment": "Store the #vss365 Prompts."}

    _id = Column(BigInteger, primary_key=True, autoincrement=True)
    twitter_id = Column(
        String(30, "utf8mb4_unicode_ci"),
        nullable=False,
        unique=True,
    )
    date = Column(Date, nullable=False)
    date_added = Column(
        DateTime,
        nullable=False,
        default=datetime.now,
        onupdate=datetime.now,
    )
    word = Column(String(30, "utf8mb4_unicode_ci"), nullable=False)
    content = Column(String(2048, "utf8mb4_unicode_ci"), nullable=False)
    host_id = Column(
        ForeignKey("hosts._id", ondelete="RESTRICT", onupdate="CASCADE"),
        nullable=False,
    )

    host = relationship("Host")
    media = relationship("PromptMedia")

    def __str__(self) -> str:
        return f"Prompt {self._id}, {self.date.isoformat()}, {self.word}"

    @hybrid_property
    def url(self) -> str:
        """Create a Twitter URL to the Prompt's source tweet."""
        return f"https://twitter.com/{self.host.handle}/{self.twitter_id}"

    @hybrid_property
    def navigation(self) -> PromptNavigation:
        """Get the previous/next Prompt dates."""
        # Because the previous or next day is not always available,
        # we must be careful to handle NoneType values correctly
        navi = PromptNavigation(next=None, previous=None)
        with suppress(AttributeError):
            navi["previous"] = (
                Prompt.query.filter_by(date=self.date - timedelta(days=1)).first().date
            )
            navi["next"] = (
                Prompt.query.filter_by(date=self.date + timedelta(days=1)).first().date
            )
        return navi


class PromptMedia(db.Model):
    __tablename__ = "prompt_media"
    __table_args__ = {"comment": "Store the #vss365 Prompt media."}

    _id = Column(BigInteger, primary_key=True, autoincrement=True)
    media = Column(String(512, "utf8mb4_unicode_ci"))
    alt_text = Column(String(1000, "utf8mb4_unicode_ci"))
    prompt_id = Column(
        ForeignKey("prompts_new._id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    )

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
