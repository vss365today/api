import json
from datetime import datetime
from pathlib import Path
from typing import List, Tuple


__all__ = [
    "get",
    "update",
    "timings_get",
    "timings_update",
    "hosting_period_get",
    "hosting_start_date_get",
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


def hosting_period_get(month: int) -> Tuple[int, int]:
    """Determine the Hosting period for the current month."""
    # In February only, Hosts begin on the 1st and 15th
    if month == 2:
        return (1, 15)

    # For all other months, Hosts begin on the 1st and 16th
    return (1, 16)


def hosting_start_date_get(today: datetime) -> int:
    """Determine the starting date for this Hosting period."""
    # Get the proper Hosting period
    START_DATES = hosting_period_get(today.month)

    # If the current day is between the start and (exclusive) end,
    # we are in the first Host's period
    if START_DATES[0] <= today.day < START_DATES[1]:
        return START_DATES[0]

    # Except it's not in that first range, so we're in the second Host's period
    return START_DATES[1]
