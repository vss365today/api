import json
from pathlib import Path
from typing import List


__all__ = [
    "get",
    "update",
    "timings_get",
    "timings_update",
]


def __get_path() -> Path:
    """Provide a Path object to the settings file."""
    return (Path() / "settings" / "settings.json").resolve()


def get() -> dict:
    """Retrieve the app settings values."""
    content = json.loads(__get_path().read_text())

    # Don't provide the timings in the result
    del content["timings"]
    return content


def update(content: dict) -> bool:
    """Update the app settings values."""
    file_path = __get_path()
    existing_content = json.loads(file_path.read_text())

    # Add the existing timings into the new settings
    content["timings"] = existing_content["timings"]
    file_path.write_text(json.dumps(content, indent=2, sort_keys=True))
    return True


def timings_get() -> List[str]:
    """Return the runtime timings for the finder service."""
    return json.loads(__get_path().read_text())["timings"]


def timings_update(times: List[str]) -> bool:
    """Update the runtime timings for the finder service.."""
    file_path = __get_path()
    content = json.loads(file_path.read_text())

    # Modify just the timings section of the settings
    content["timings"] = times
    file_path.write_text(json.dumps(content, indent=2, sort_keys=True))
    return True
