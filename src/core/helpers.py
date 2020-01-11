import os
import secrets
import shutil
from urllib import parse
from typing import Literal, Optional

import requests

from src.core.config import load_app_config


__all__ = [
    "date_iso_format",
    "make_response",
    "make_error_response",
    "media_download",
    "media_file_name",
    "media_move",
    "media_remove",
    "media_saved_name"
]


CONFIG = load_app_config()


def date_iso_format(dt) -> str:
    return dt.strftime("%Y-%m-%d")


def make_response(data: dict, status: int) -> tuple:
    return (data, status)


def make_error_response(msg: str, status: int) -> tuple:
    return make_response({"error_msg": msg}, status)


def media_download(pid: str, url: str) -> dict:
    # Generate a random file name for the download
    original_f_name = media_file_name(url)
    temp_f_name = "{name}{ext}".format(
        name=secrets.token_hex(12),
        ext=os.path.splitext(original_f_name)[1]
    )

    # Download the media to a temp directory
    r = requests.get(url)
    dl_path = os.path.join(
        os.path.abspath(CONFIG["IMAGES_DIR_TEMP"]),
        temp_f_name
    )
    with open(dl_path, "wb") as f:
        f.write(r.content)

    # Return the original and temp file name
    return {
        "original": original_f_name,
        "temp": temp_f_name,
        "final": media_saved_name(pid, url)
    }


def media_file_name(url: str) -> Optional[str]:
    """Extract the media file name from its URL."""
    if url is not None:
        # Extract the media filename from the URL
        name = parse.urlsplit(url).path.split("/")[2]

        # If there's a colon in the filename,
        # it means there's an image size tag.
        # We want to remove this from the filename
        if ":" in name:
            name = name[:name.find(":")]
        return name
    return None


def media_move(details: dict) -> bool:
    """Move a media file from the temporary directory to final location."""
    current_path = os.path.join(CONFIG["IMAGES_DIR_TEMP"], details["temp"])
    final_path = os.path.join(CONFIG["IMAGES_DIR"], details["final"])
    shutil.move(current_path, final_path)
    return os.path.isfile(final_path)


def media_remove(pid: str) -> Literal[True]:
    """Delete a media file."""
    f_name = [
        f
        for f in os.listdir(CONFIG["IMAGES_DIR"])
        if f.startswith(pid)
    ]
    if len(f_name) == 1:
        os.remove(os.path.join(CONFIG["IMAGES_DIR"], f_name[0]))
    return True


def media_saved_name(pid: str, url: str) -> str:
    """Generate the media's saved file name."""
    return "{id}-{original}".format(
        id=pid,
        original=media_file_name(url)
    )
