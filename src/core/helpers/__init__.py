from datetime import date, datetime

import tweepy

from src.configuration import get_secret


__all__ = ["twitter_v2_api", "format_datetime_pretty"]


def twitter_v2_api() -> tweepy.Client:
    """Connect to Twitter API v2 using a Bearer token."""
    return tweepy.Client(bearer_token=get_secret("TWITTER_BEARER"))


def format_datetime_pretty(date_obj: date | datetime) -> str:
    """Pretty format a date as MM DD, YYYY."""
    return date_obj.strftime("%B %d, %Y")
