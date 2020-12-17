from datetime import datetime
from flask import current_app
from typing import Any, Dict, Tuple

import tweepy


__all__ = [
    "connect_to_twitter",
    "format_datetime_pretty",
    "format_datetime_ymd",
    "make_response",
    "make_error_response",
]


def connect_to_twitter() -> tweepy.API:
    """Connect to the Twitter API."""
    auth = tweepy.OAuthHandler(
        current_app.config["TWITTER_APP_KEY"], current_app.config["TWITTER_APP_SECRET"]
    )
    auth.set_access_token(
        current_app.config["TWITTER_KEY"], current_app.config["TWITTER_SECRET"]
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
