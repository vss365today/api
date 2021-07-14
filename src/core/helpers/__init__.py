from datetime import datetime
from flask import current_app
from typing import Any, Dict, Tuple

import tweepy


__all__ = [
    "twitter_v1_api",
    "format_datetime_pretty",
    "format_datetime_ymd",
    "make_response",
    "make_error_response",
]


def twitter_v1_api() -> tweepy.API:
    """Connect to Twitter API v1 using OAuth 2."""
    auth = tweepy.AppAuthHandler(
        current_app.config["TWITTER_CONSUMER_KEY"],
        current_app.config["TWITTER_CONSUMER_SECRET"],
    )
    return tweepy.API(auth)


def format_datetime_pretty(date_obj: datetime) -> str:
    """Pretty format a date as MM DD, YYYY."""
    return date_obj.strftime("%B %d, %Y")


def format_datetime_ymd(date_obj: datetime) -> str:
    """Format a date as YYYY-MM-DD."""
    return date_obj.strftime("%Y-%m-%d")


def make_response(status: int, data: Dict[str, Any] = None) -> Tuple[dict, int]:
    """Construct a non-error endpoint response."""
    if data is None:
        data = {}
    return (data, status)


def make_error_response(status: int, msg: str) -> Tuple[Dict[str, str], int]:
    """Construct an error endpoint response."""
    return make_response(status, {"error_msg": msg})
