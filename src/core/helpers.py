import filecmp
import os.path
import secrets
import shutil
from urllib import parse
from typing import Optional

import requests

from src.core.config import load_app_config


__all__ = [
    "date_iso_format",
    "make_response",
    "make_error_response",
    "media_compare",
    "media_download",
    "media_file_name",
    "media_move",
    "media_remove"
]


CONFIG = load_app_config()


def date_iso_format(dt) -> str:
    return dt.strftime("%Y-%m-%d")


def make_response(data: dict, status: int) -> tuple:
    return (data, status)


def make_error_response(msg: str, status: int) -> tuple:
    return make_response({"error_msg": msg}, status)


def media_compare(current: str, new: str) -> bool:
    # Generate paths to the two files and compare them
    current_path = os.path.join(CONFIG["IMAGES_DIR"], current)
    new_path = os.path.join(CONFIG["IMAGES_DIR_TEMP"], new)
    return filecmp.cmp(current_path, new_path)


def media_download(url: str) -> dict:
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
        "orginal": original_f_name,
        "temp": temp_f_name
    }


def media_file_name(url: str) -> Optional[str]:
    """Extract the media file name from its URL."""
    if url is not None:
        return parse.urlsplit(url).path.split("/")[2]
    return None


def media_move(details: dict) -> bool:
    current_path = os.path.join(CONFIG["IMAGES_DIR_TEMP"], details["temp"])
    final_path = os.path.join(CONFIG["IMAGES_DIR"], details["orginal"])
    shutil.move(current_path, final_path)
    return os.path.isfile(final_path)


def media_remove(f_name: str):
    pass
