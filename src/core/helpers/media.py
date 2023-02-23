import secrets
from pathlib import Path, PurePath
from typing import Literal

import requests
from urllib3.exceptions import LocationParseError
from urllib3.util import parse_url

from src.configuration import get_secret


__all__ = ["delete", "delete_v2", "download", "is_valid_url", "move", "saved_name"]


def delete(prompt_id: str) -> Literal[True]:
    """Delete any Media files attached to a Prompt."""
    all_media = Path(get_secret("IMAGES_DIR")).glob(f"{prompt_id}*")
    for f in all_media:
        f.unlink()
    return True


def delete_v2(prompt_id: int, media_id: int | None = None) -> Literal[True]:
    """Delete media files associated with a Prompt.

    If a specific Media file ID is given, only that file will be deleted.
    Otherwise, all files associated with the Prompt ID will be deleted.
    """
    pattern = f"{prompt_id}*" if media_id is None else f"{prompt_id}-{media_id}*"
    all_media = Path(get_secret("IMAGES_DIR")).glob(pattern)
    for f in all_media:
        f.unlink()
    return True


def download(prompt_id: str, url: str) -> dict[str, str]:
    """Download a Tweet's media."""
    # Generate a random file name for the download
    original_f_name = original_name(url)
    temp_f_name = "{name}{ext}".format(
        name=secrets.token_hex(12), ext=PurePath(original_f_name).suffix
    )

    # Download the media to a temp directory
    r = requests.get(url)
    dl_path = Path(get_secret("IMAGES_DIR_TEMP")).resolve() / temp_f_name
    dl_path.write_bytes(r.content)

    # Return the original and temp file name
    return {
        "original": original_f_name,
        "temp": temp_f_name,
        "final": saved_name(prompt_id, url),
    }


def is_valid_url(url: str) -> bool:
    """Attempt to determine if a URL is valid."""
    # Make sure it's an actual web URL
    if not url.lower().startswith("http"):
        return False

    try:
        result = parse_url(url)

        # We're missing parts of the URL
        if not result.scheme or not result.host:
            return False
        return True

    # This is a SUPER malformed thing
    except LocationParseError:
        return False


def move(details: dict) -> bool:
    """Move a media file from the temporary directory to final location."""
    current_path = Path(get_secret("IMAGES_DIR_TEMP")) / details["temp"]
    final_path = Path(get_secret("IMAGES_DIR")) / details["final"]
    current_path.replace(final_path)
    return final_path.is_file()


def original_name(url: str) -> str:
    """Extract the media file name from its URL."""
    # Extract the media filename from the URL
    name = parse_url(url).path.split("/")[2]

    # If there's a colon in the filename, it means there's an image size tag.
    # We want to remove this from the filename
    if ":" in name:
        name = name[: name.find(":")]
    return name


def saved_name(prompt_id: str, url: str) -> str:
    """Generate the media's saved file name."""
    return "{id}-{original}".format(id=prompt_id, original=original_name(url))
