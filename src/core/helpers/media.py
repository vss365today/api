import secrets
from pathlib import Path, PurePath
from typing import Literal

import httpx
from urllib3.exceptions import LocationParseError
from urllib3.util import parse_url

from src.configuration import get_secret

__all__ = [
    "delete",
    "download",
    "is_valid_url",
    "move",
    "saved_name",
]


def delete(prompt_id: int, media_id: int | None = None) -> Literal[True]:
    """Delete media files associated with a Prompt.

    If a specific Media file ID is given, only that file will be deleted.
    Otherwise, all files associated with the Prompt ID will be deleted.
    """
    pattern = f"*-{prompt_id}-*" if media_id is None else f"{media_id}-{prompt_id}*"
    all_media = Path(get_secret("IMAGES_DIR")).glob(pattern)
    for f in all_media:
        f.unlink()
    return True


def download(url: str) -> str:
    """Download a Tweet's media."""
    # Generate a random file name for the download
    temp_f_name = f"{secrets.token_hex(12)}{PurePath(original_name(url)).suffix}"

    # Download the media to a temp directory and provide the temp file name
    r = httpx.get(url)
    dl_path = Path(get_secret("IMAGES_DIR_TEMP")).resolve() / temp_f_name
    dl_path.write_bytes(r.content)
    return temp_f_name


def is_valid_url(url: str) -> bool:
    """Attempt to determine if a URL is valid."""
    # Make sure it's an actual web URL.
    # It's ok to not check for `https`. We're not enforcing
    # secure-only URLs (as we're not hotlinking) and this check
    # technically works for both secure and not secure :D
    if not url.lower().startswith("http"):
        return False

    try:
        # If we're missing parts of the URL, it's obviously not valid
        result = parse_url(url)
        return not (not result.scheme or not result.host)

    # This is a SUPER malformed thing
    except LocationParseError:
        return False


def move(temp_file: str, final_file: str) -> bool:
    """Move a media file from the temporary directory to final location."""
    current_path = Path(get_secret("IMAGES_DIR_TEMP")) / temp_file
    final_path = Path(get_secret("IMAGES_DIR")) / final_file
    current_path.replace(final_path)
    return final_path.is_file()


def original_name(url: str) -> str:
    """Extract the media file name from its URL."""
    name = parse_url(url).path.split("/")[2]

    # If there's a colon in the filename, it means there's an image size tag.
    # We want to remove this from the filename
    if ":" in name:
        name = name[: name.find(":")]
    return name


def saved_name(prompt_id: int, media_id: int, url: str) -> str:
    """Generate the media's saved file name."""
    return "{media_id}-{id}-{original}".format(
        media_id=media_id,
        id=prompt_id,
        original=original_name(url),
    )
