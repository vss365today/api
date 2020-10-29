import json
from pathlib import Path


__all__ = ["get", "update", "timer_get", "timer_update"]


def __get_path() -> Path:
    """Provide a Path object to the settings file."""
    return (Path() / "settings" / "settings.json").resolve()


def get() -> dict:
    """Return the JSON contents of the settings file."""
    return json.loads(__get_path().read_text())


def update(content: dict) -> bool:
    """Update the JSON contents of the settings file."""
    __get_path().write_text(json.dumps(content, indent=2, sort_keys=True))
    return True


def timings_get():
    """Return the runtime timings for the finder service."""
    return json.loads(__get_path().read_text())["timings"]


def timer_update():
    """TK."""
    pass
